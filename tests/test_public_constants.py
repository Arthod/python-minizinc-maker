import unittest

import pytest

import pymzm


pytestmark = [pytest.mark.unit]


class TestPublicConstants(unittest.TestCase):
    def test_solve_constants_are_grouped_and_consistent(self):
        self.assertEqual(
            set(pymzm.SOLVE_CRITERIA),
            {pymzm.SOLVE_SATISFY, pymzm.SOLVE_MINIMIZE, pymzm.SOLVE_MAXIMIZE},
        )

    def test_constraint_type_alias_is_consistent(self):
        self.assertEqual(
            pymzm.Constraint.CTYPE_ALL_DIFFERENT,
            pymzm.Constraint.CTYPE_ALLDIFFERENT,
        )
        self.assertIn(pymzm.Constraint.CTYPE_ALL_DIFFERENT, pymzm.Constraint.PUBLIC_CTYPES)

    def test_public_constraint_types_have_no_duplicates(self):
        public_ctypes = pymzm.Constraint.PUBLIC_CTYPES
        self.assertEqual(len(public_ctypes), len(set(public_ctypes)))


if __name__ == "__main__":
    unittest.main()
