import unittest

import pymzm


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


if __name__ == "__main__":
    unittest.main()
