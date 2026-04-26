import unittest
import pytest

import pymzm


pytestmark = [pytest.mark.unit]


class TestFunctions(unittest.TestCase):
    def test_function_declaration_and_numeric_call_render(self):
        model = pymzm.Model()
        model.add_function_declaration("function int: plus_one(int: v) = v + 1")

        x = model.add_variable("x", val_min=0, val_max=10)
        fx = model.call_function("plus_one", x)

        model.set_solve_criteria(pymzm.SOLVE_MAXIMIZE, fx)
        ir = model.to_ir()

        self.assertIn("function int: plus_one(int: v) = v + 1;", ir.function_declarations)
        self.assertEqual(str(fx), "plus_one(x)")
        self.assertEqual(ir.solve.expression, "plus_one(x)")

    def test_function_call_with_array_argument_render(self):
        model = pymzm.Model()
        model.add_function_declaration(
            "function int: sum2(array[int] of var int: xs) = sum(xs)"
        )

        a = model.add_variable("a", val_min=0, val_max=5)
        b = model.add_variable("b", val_min=0, val_max=5)
        f = model.call_function("sum2", [a, b])
        model.add_constraint(f <= 7)
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        ir = model.to_ir()
        self.assertIn("constraint (sum2([a, b]) <= 7);", ir.constraints)

    def test_boolean_function_call_constraint_render(self):
        model = pymzm.Model()
        model.add_function_declaration(
            "function bool: nonnegative(int: v) = (v >= 0)"
        )

        x = model.add_variable("x", val_min=-2, val_max=2)
        model.add_function_call("nonnegative", x)
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        ir = model.to_ir()
        self.assertIn("constraint nonnegative(x);", ir.constraints)

    def test_duplicate_function_declarations_are_deduplicated_in_ir(self):
        model = pymzm.Model()
        d1 = "function int: plus_one(int: v) = v + 1"
        d2 = "function int: plus_one(int: v) = v + 1;"

        model.add_function_declaration(d1)
        model.add_function_declaration(d2)

        x = model.add_variable("x", val_min=0, val_max=10)
        model.set_solve_criteria(pymzm.SOLVE_MAXIMIZE, model.call_function("plus_one", x))

        ir = model.to_ir()
        decls = [line for line in ir.function_declarations if line.startswith("function int: plus_one")]
        self.assertEqual(len(decls), 1)


if __name__ == "__main__":
    unittest.main()
