import unittest
import pytest

import pymzm


pytestmark = [pytest.mark.unit]


class TestLetExpressions(unittest.TestCase):
    def test_let_expression_can_be_used_in_constraints_and_objective(self):
        model = pymzm.Model()
        x = model.add_variable("x", val_min=0, val_max=10)

        model.add_constraint(
            pymzm.Expression.let(
                ["int: y = x + 1"],
                pymzm.Expression("y") >= 1,
            )
        )
        model.set_solve_criteria(
            pymzm.SOLVE_MAXIMIZE,
            pymzm.Expression.let(["int: y = x + 1"], pymzm.Expression("y")),
        )

        ir = model.to_ir()

        self.assertIn("constraint let { int: y = x + 1; } in ((y >= 1));", ir.constraints)
        self.assertEqual(ir.solve.expression, "let { int: y = x + 1; } in (y)")


if __name__ == "__main__":
    unittest.main()
