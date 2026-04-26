import unittest
import pytest

import pymzm


pytestmark = [pytest.mark.unit]


class TestScalarTypes(unittest.TestCase):
    def test_variable_scalar_type_declarations(self):
        model = pymzm.Model()

        b = model.add_variable("b", vtype=pymzm.Variable.VTYPE_BOOL)
        i = model.add_variable("i", vtype=pymzm.Variable.VTYPE_INTEGER, val_min=-2, val_max=5)
        f = model.add_variable("f", vtype=pymzm.Variable.VTYPE_FLOAT, val_min=-1, val_max=3)
        s = model.add_variable("s", vtype=pymzm.Variable.VTYPE_STRING)

        model.add_constraint(i >= -2)
        model.add_constraint(f <= 3)
        model.add_constraint(b == True)
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        ir = model.to_ir()

        self.assertIn("var bool: b;", ir.declarations)
        self.assertIn("var -2..5: i;", ir.declarations)
        self.assertIn("var -1..3: f;", ir.declarations)
        self.assertIn("var string: s;", ir.declarations)

    def test_constant_scalar_type_declarations(self):
        model = pymzm.Model()

        model.add_constant("ci", 7, vtype=pymzm.Variable.VTYPE_INTEGER)
        model.add_constant("cb", True, vtype=pymzm.Variable.VTYPE_BOOL)
        model.add_constant("cf", 3.25, vtype=pymzm.Variable.VTYPE_FLOAT)
        model.add_constant("cs", "hello \"mzn\"", vtype=pymzm.Variable.VTYPE_STRING)

        x = model.add_variable("x", val_min=0, val_max=10)
        model.add_constraint(x >= 0)
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        ir = model.to_ir()

        self.assertIn("int: ci = 7;", ir.declarations)
        self.assertIn("bool: cb = true;", ir.declarations)
        self.assertIn("float: cf = 3.25;", ir.declarations)
        self.assertIn('string: cs = "hello \\\"mzn\\\"";', ir.declarations)

    def test_set_domains_for_int_and_enum_type(self):
        model = pymzm.Model()

        set_int = model.add_variable("set_int", vtype=pymzm.Variable.VTYPE_SET, domain={3, 1, 2})
        set_enum = model.add_variable("set_enum", vtype=pymzm.Variable.VTYPE_SET, domain="Color")

        model.add_constraint(set_int.contains(1))
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        ir = model.to_ir()

        self.assertIn("var set of {1, 2, 3}: set_int;", ir.declarations)
        self.assertIn("var set of Color: set_enum;", ir.declarations)

    def test_nd_array_constant_serialization(self):
        model = pymzm.Model()
        values = [
            [[1, 2], [3, 4]],
            [[5, 6], [7, 8]],
        ]
        model.add_constant("a3", values, vtype=pymzm.Variable.VTYPE_INTEGER)
        x = model.add_variable("x", val_min=0, val_max=10)
        model.add_constraint(x >= 0)
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        ir = model.to_ir()

        self.assertIn(
            "array[1..2,1..2,1..2] of int: a3 = array3d(1..2, 1..2, 1..2, [1, 2, 3, 4, 5, 6, 7, 8]);",
            ir.declarations,
        )


if __name__ == "__main__":
    unittest.main()
