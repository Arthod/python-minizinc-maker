import unittest

import pytest

import pymzm


pytestmark = [pytest.mark.unit]


class TestBuilderRefactorRegression(unittest.TestCase):
    def test_expression_comprehension_and_quantifier_outputs_unchanged(self):
        arr = pymzm.Expression.array_comprehension(lambda i: i + 1, [("i", range(1, 4))])
        s = pymzm.Expression.set_comprehension(lambda i: i, [("i", [1, 2, 3], lambda i: i >= 2)])
        q_forall = pymzm.Expression.forall_over([("i", range(1, 4))], lambda i: i >= 1)
        q_exists = pymzm.Expression.exists_over([("i", [1, 2, 3])], lambda i: i == 2)

        self.assertEqual(str(arr), "[(i + 1) | i in 1..3]")
        self.assertEqual(str(s), "{i | i in {1, 2, 3} where (i >= 2)}")
        self.assertEqual(str(q_forall), "forall (i in 1..3) ((i >= 1))")
        self.assertEqual(str(q_exists), "exists (i in {1, 2, 3}) ((i == 2))")

    def test_constraint_pairwise_validators_still_raise_on_length_mismatch(self):
        with self.assertRaises(AssertionError):
            pymzm.Constraint.lex_less([1, 2], [1])

        with self.assertRaises(AssertionError):
            pymzm.Constraint.inverse([1, 2], [1])

        with self.assertRaises(AssertionError):
            pymzm.Constraint.bin_packing(10, [1, 2], [4])


if __name__ == "__main__":
    unittest.main()
