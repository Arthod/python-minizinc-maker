import unittest
import pytest

import pymzm


pytestmark = [pytest.mark.unit]


class TestParameters(unittest.TestCase):
    def test_parameters_are_separate_from_decision_variables(self):
        model = pymzm.Model()

        n = model.add_parameter("n", 5)
        x = model.add_variable("x", val_min=0, val_max=10)
        model.add_constraint(x <= n)
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        self.assertIn(n, model.parameters)
        self.assertNotIn(n, model.variables)
        self.assertIn(x, model.variables)

        ir = model.to_ir()
        self.assertIn("int: n = 5;", ir.declarations)
        self.assertIn("var 0..10: x;", ir.declarations)
        self.assertTrue(any("constraint (x <= n);" in line for line in ir.constraints))

    def test_add_parameters_supports_scalar_list_and_dict_values(self):
        model = pymzm.Model()

        p_scalar = model.add_parameters("w", indices=[0, 1, 2], values=7)
        p_list = model.add_parameters("v", indices=[0, 1], values=[3, 4])
        p_dict = model.add_parameters("d", indices=["a", "b"], values={"a": 9, "b": 11})

        x = model.add_variable("x", val_min=0, val_max=100)
        model.add_constraint(x >= p_scalar[0])
        model.add_constraint(x >= p_list[1])
        model.add_constraint(x >= p_dict["b"])
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        ir = model.to_ir()

        self.assertIn("int: w_0 = 7;", ir.declarations)
        self.assertIn("int: w_1 = 7;", ir.declarations)
        self.assertIn("int: w_2 = 7;", ir.declarations)
        self.assertIn("int: v_0 = 3;", ir.declarations)
        self.assertIn("int: v_1 = 4;", ir.declarations)
        self.assertIn("int: d_a = 9;", ir.declarations)
        self.assertIn("int: d_b = 11;", ir.declarations)

    def test_parameters_support_enum_values(self):
        model = pymzm.Model()
        color = model.add_enum("Color", ["RED", "GREEN"]) 

        fav = model.add_parameter("fav", color.GREEN, vtype="Color")
        x = model.add_variable("x", val_min=0, val_max=1)
        model.add_constraint(x >= 0)
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        ir = model.to_ir()

        self.assertEqual(str(fav), "fav")
        self.assertIn("Color: fav = GREEN;", ir.declarations)


if __name__ == "__main__":
    unittest.main()
