import unittest
import pytest

import pymzm


pytestmark = [pytest.mark.unit]


class TestOperatorOverloadsAndPrecedence(unittest.TestCase):
    def setUp(self):
        self.x = pymzm.Expression("x")
        self.y = pymzm.Expression("y")
        self.z = pymzm.Expression("z")

    def test_arithmetic_operator_overloads(self):
        self.assertEqual(str(self.x + self.y), "(x + y)")
        self.assertEqual(str(3 + self.x), "(3 + x)")
        self.assertEqual(str(self.x - self.y), "(x - y)")
        self.assertEqual(str(3 - self.x), "(3 - x)")
        self.assertEqual(str(self.x * self.y), "(x * y)")
        self.assertEqual(str(3 * self.x), "(3 * x)")
        self.assertEqual(str(self.x / self.y), "(x / y)")
        self.assertEqual(str(3 / self.x), "(3 / x)")
        self.assertEqual(str(self.x // self.y), "(x div y)")
        self.assertEqual(str(3 // self.x), "(3 div x)")
        self.assertEqual(str(self.x % self.y), "(x mod y)")
        self.assertEqual(str(3 % self.x), "(3 mod x)")
        self.assertEqual(str(self.x ** self.y), "pow(x, y)")
        self.assertEqual(str(3 ** self.x), "pow(3, x)")
        self.assertEqual(str(-self.x), "(0 - x)")
        self.assertEqual(str(abs(self.x)), "abs(x)")

    def test_comparison_operator_overloads(self):
        self.assertEqual(str(self.x == self.y), "(x == y)")
        self.assertEqual(str(self.x != self.y), "(x != y)")
        self.assertEqual(str(self.x < self.y), "(x < y)")
        self.assertEqual(str(self.x <= self.y), "(x <= y)")
        self.assertEqual(str(self.x > self.y), "(x > y)")
        self.assertEqual(str(self.x >= self.y), "(x >= y)")

    def test_boolean_operator_overloads(self):
        a = self.x >= 1
        b = self.y <= 2

        self.assertEqual(str(a & b), "((x >= 1) /\\ (y <= 2))")
        self.assertEqual(str(a | b), "((x >= 1) \\/ (y <= 2))")
        self.assertEqual(str(a ^ b), "((x >= 1) xor (y <= 2))")
        self.assertEqual(str(~a), "not((x >= 1))")

        self.assertRaises(pymzm.PymzmValueIsNotCondition, lambda: True & a)
        self.assertRaises(pymzm.PymzmValueIsNotCondition, lambda: False | a)
        self.assertRaises(pymzm.PymzmValueIsNotCondition, lambda: True ^ a)

    def test_operator_precedence_edges(self):
        expr1 = self.x + self.y * self.z
        self.assertEqual(str(expr1), "(x + (y * z))")

        expr2 = (self.x + self.y) * self.z
        self.assertEqual(str(expr2), "((x + y) * z)")

        expr3 = (self.x >= 1) & ((self.y <= 2) | (self.z == 3))
        self.assertEqual(str(expr3), "((x >= 1) /\\ ((y <= 2) \\/ (z == 3)))")

        expr4 = self.x ** self.y ** self.z
        self.assertEqual(str(expr4), "pow(x, pow(y, z))")

        expr5 = -self.x + self.y
        self.assertEqual(str(expr5), "((0 - x) + y)")

    def test_value_dict_comparison_overloads(self):
        model = pymzm.Model()
        xs = model.add_variables("x", range(3), val_min=0, val_max=1)

        eqs = xs == 1
        nes = xs != 0
        lts = xs < 2
        les = xs <= 1
        gts = xs > -1
        ges = xs >= 0

        self.assertEqual(len(eqs), 3)
        self.assertTrue(all(str(e) == f"(x_{i} == 1)" for i, e in enumerate(eqs)))
        self.assertTrue(all(str(e) == f"(x_{i} != 0)" for i, e in enumerate(nes)))
        self.assertTrue(all(str(e) == f"(x_{i} < 2)" for i, e in enumerate(lts)))
        self.assertTrue(all(str(e) == f"(x_{i} <= 1)" for i, e in enumerate(les)))
        self.assertTrue(all(str(e) == f"(x_{i} > -1)" for i, e in enumerate(gts)))
        self.assertTrue(all(str(e) == f"(x_{i} >= 0)" for i, e in enumerate(ges)))

    def test_invalid_operands_raise(self):
        self.assertRaises(pymzm.PymzmValueIsNotExpression, lambda: self.x + "bad")
        self.assertRaises(pymzm.PymzmValueIsNotExpression, lambda: self.x / None)
        self.assertRaises(pymzm.PymzmValueIsNotExpression, lambda: self.x ** object())
        self.assertRaises(pymzm.PymzmValueIsNotCondition, lambda: (self.x >= 1) & 3)
        self.assertRaises(pymzm.PymzmValueIsNotCondition, lambda: (self.x >= 1) | "bad")

    def test_set_operators_and_membership_helpers(self):
        a = pymzm.Expression("a")
        b = pymzm.Expression("b")

        self.assertEqual(str(a.union(b)), "(a union b)")
        self.assertEqual(str(a.intersection(b)), "(a intersect b)")
        self.assertEqual(str(a.set_diff(b)), "(a diff b)")
        self.assertEqual(str(a.symdiff(b)), "((a diff b) union (b diff a))")

        self.assertEqual(str(self.x.in_([1, 2, 3])), "(x in {1, 2, 3})")
        self.assertEqual(str(self.x.not_in([1, 2, 3])), "(x not in {1, 2, 3})")
        self.assertEqual(str(a.subset_of(b)), "(a subset b)")
        self.assertEqual(str(a.superset_of(b)), "(a superset b)")

    def test_array_indexing_semantics(self):
        arr = pymzm.Expression("arr")

        self.assertEqual(str(arr[0]), "arr[1]")
        self.assertEqual(str(arr[self.x]), "arr[x + 1]")
        self.assertEqual(str(arr[0, self.y]), "arr[1, y + 1]")
        self.assertRaises(pymzm.PymzmValueIsNotExpression, lambda: arr[None])


if __name__ == "__main__":
    unittest.main()
