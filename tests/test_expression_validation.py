import unittest
import pytest

import pymzm
from tests.mzn_verifier import assert_valid_mzn


pytestmark = [pytest.mark.unit]


class TestExpressionValidation(unittest.TestCase):
    def test_numeric_aggregations_accept_iterables(self):
        x = pymzm.Expression("x")
        y = pymzm.Expression("y")

        self.assertEqual(str(pymzm.Expression.sum([x, y, 3])), "sum([x, y, 3])")
        self.assertEqual(str(pymzm.Expression.product(v for v in [x, 2])), "product([x, 2])")
        self.assertEqual(str(pymzm.Expression.min([x, 1])), "min([x, 1])")
        self.assertEqual(str(pymzm.Expression.max([y, 9])), "max([y, 9])")

    def test_numeric_aggregations_reject_invalid_values(self):
        x = pymzm.Expression("x")

        self.assertRaises(pymzm.PymzmValueIsNotExpression, pymzm.Expression.sum, "x")
        self.assertRaises(pymzm.PymzmNoValues, pymzm.Expression.sum, [])
        self.assertRaises(pymzm.PymzmValueIsNotExpression, pymzm.Expression.product, [x, "bad"])
        self.assertRaises(pymzm.PymzmValueIsNotExpression, pymzm.Expression.min, [object()])
        self.assertRaises(pymzm.PymzmValueIsNotExpression, pymzm.Expression.max, [None])

    def test_condition_operators_validate_inputs(self):
        x = pymzm.Expression("x")
        y = pymzm.Expression("y")
        a = x >= 1
        b = y <= 2

        self.assertEqual(str(pymzm.Expression.AND([a, b])), "((x >= 1) /\\ (y <= 2))")
        self.assertEqual(str(pymzm.Expression.OR([a, b])), "((x >= 1) \\/ (y <= 2))")
        self.assertEqual(str(pymzm.Expression.implies([a, b])), "((x >= 1) -> (y <= 2))")

        self.assertRaises(pymzm.PymzmValueIsNotCondition, pymzm.Expression.AND, [a, x])
        self.assertRaises(pymzm.PymzmValueIsNotCondition, pymzm.Expression.OR, "a")

    def test_binary_operator_helpers_keep_behavior(self):
        x = pymzm.Expression("x")
        y = pymzm.Expression("y")

        self.assertEqual(str(x + y), "(x + y)")
        self.assertEqual(str(3 + x), "(3 + x)")
        self.assertEqual(str(x * 5), "(x * 5)")
        self.assertEqual(str(x == y), "(x == y)")
        self.assertEqual(str((x >= 1) & (y >= 2)), "((x >= 1) /\\ (y >= 2))")

        self.assertRaises(pymzm.PymzmValueIsNotExpression, lambda: x + "bad")
        self.assertRaises(pymzm.PymzmValueIsNotCondition, lambda: (x >= 1) & 3)

    def test_let_expression_renders_for_numeric_and_boolean_bodies(self):
        y = pymzm.Expression("y")

        numeric_let = pymzm.Expression.let(["int: y = 3"], y + 1)
        boolean_let = pymzm.Expression.let("int: y = 3", y >= 1)

        self.assertEqual(str(numeric_let), "let { int: y = 3; } in ((y + 1))")
        self.assertEqual(str(boolean_let), "let { int: y = 3; } in ((y >= 1))")
        self.assertIsInstance(numeric_let, pymzm.Expression)
        self.assertIsInstance(boolean_let, pymzm.ExpressionBool)

    def test_let_expression_validates_declarations_and_body(self):
        self.assertRaises(pymzm.PymzmNoValues, pymzm.Expression.let, [], pymzm.Expression("x"))
        self.assertRaises(pymzm.PymzmValueIsNotExpression, pymzm.Expression.let, [""], pymzm.Expression("x"))
        self.assertRaises(pymzm.PymzmValueIsNotExpression, pymzm.Expression.let, ["int: y = 1"], object())

    def test_conditional_supports_chained_elseif(self):
        x = pymzm.Expression("x")
        y = pymzm.Expression("y")

        expr = pymzm.Expression.conditional(
            [
                (x >= 5, x + 1),
                (x >= 2, y + 3),
            ],
            0,
        )

        self.assertEqual(
            str(expr),
            "(if (x >= 5) then (x + 1) elseif (x >= 2) then (y + 3) else 0 endif)",
        )
        self.assertIsInstance(expr, pymzm.Expression)

    def test_conditional_returns_bool_expression_for_bool_bodies(self):
        x = pymzm.Expression("x")

        expr = pymzm.Expression.conditional(
            [
                (x >= 1, x >= 2),
                (False, True),
            ],
            False,
        )

        self.assertEqual(
            str(expr),
            "(if (x >= 1) then (x >= 2) elseif false then true else false endif)",
        )
        self.assertIsInstance(expr, pymzm.ExpressionBool)

    def test_conditional_validates_branches_and_else(self):
        x = pymzm.Expression("x")
        self.assertRaises(pymzm.PymzmNoValues, pymzm.Expression.conditional, [], 0)
        self.assertRaises(pymzm.PymzmValueIsNotExpression, pymzm.Expression.conditional, ["bad"], 0)
        self.assertRaises(pymzm.PymzmValueIsNotCondition, pymzm.Expression.conditional, [(x, 1)], 0)
        self.assertRaises(pymzm.PymzmValueIsNotExpression, pymzm.Expression.conditional, [(x >= 1, object())], 0)
        self.assertRaises(pymzm.PymzmValueIsNotExpression, pymzm.Expression.conditional, [(x >= 1, 1)], object())

    def test_expression_render_is_valid_mzn_when_embedded_in_model(self):
        model = pymzm.Model()
        x = model.add_variable("x", val_min=0, val_max=10)

        y_expr = pymzm.Expression.let(["int: y = x + 1"], pymzm.Expression("y"))
        guard = pymzm.Expression.conditional([(x >= 5, True), (x >= 2, x >= 3)], False)
        q = pymzm.Expression.forall("i", range(1, 4), lambda i: x >= i)

        model.add_constraint(guard)
        model.add_constraint(q)
        model.add_constraint(y_expr >= 1)
        model.set_solve_criteria(pymzm.SOLVE_MAXIMIZE, y_expr)
        model.generate()

        assert_valid_mzn(self, model.model_mzn_str)

    def test_array_and_set_comprehension_render_with_filters(self):
        arr = pymzm.Expression.array_comprehension(
            lambda i: i + 1,
            [("i", range(1, 4), lambda i: i >= 2)],
        )
        s = pymzm.Expression.set_comprehension(
            lambda i, j: i + j,
            [("i", "1..2"), ("j", [1, 2, 3], lambda j: j >= 2)],
        )

        self.assertEqual(str(arr), "[(i + 1) | i in 1..3 where (i >= 2)]")
        self.assertEqual(str(s), "{(i + j) | i in 1..2, j in {1, 2, 3} where (j >= 2)}")

    def test_comprehensions_can_be_used_in_model_constraints(self):
        model = pymzm.Model()
        x = model.add_variable("x", val_min=0, val_max=10)

        arr = pymzm.Expression.array_comprehension(lambda i: i + x, [("i", range(1, 3))])
        s = pymzm.Expression.set_comprehension(lambda i: i, [("i", [1, 2, 3], lambda i: i >= 2)])

        model.add_constraint(x >= 0)
        model.add_constraint(pymzm.Expression._func("sum", [arr]) >= 0)
        model.add_constraint(pymzm.Expression._func("card", [s]) >= 1)
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        model.generate()

        self.assertIn("sum([", model.model_mzn_str)
        self.assertIn("{i | i in {1, 2, 3} where (i >= 2)}", model.model_mzn_str)
        assert_valid_mzn(self, model.model_mzn_str)

    def test_comprehensions_validate_inputs(self):
        self.assertRaises(pymzm.PymzmNoValues, pymzm.Expression.array_comprehension, 1, [])
        self.assertRaises(pymzm.PymzmValueIsNotExpression, pymzm.Expression.array_comprehension, object(), [("i", [1])])
        self.assertRaises(pymzm.PymzmValueIsNotExpression, pymzm.Expression.array_comprehension, 1, ["bad"])
        self.assertRaises(pymzm.PymzmValueIsNotCondition, pymzm.Expression.array_comprehension, 1, [("i", [1], 7)])

        self.assertRaises(pymzm.PymzmNoValues, pymzm.Expression.set_comprehension, 1, [])
        self.assertRaises(pymzm.PymzmValueIsNotExpression, pymzm.Expression.set_comprehension, object(), [("i", [1])])


if __name__ == "__main__":
    unittest.main()
