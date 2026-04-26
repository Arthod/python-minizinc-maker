import unittest
import pytest
from tests.solver_utils import deterministic_instance_solve, lookup_default_solver

import pymzm
import minizinc


pytestmark = [pytest.mark.integration]

class TestMisc(unittest.TestCase):
    def setUp(self):
        self.model = pymzm.Model()
        self.gecode = lookup_default_solver()

    def test_misc1(self):
        model = self.model
        # Negative summation
        xs = model.add_variables("x", range(10), pymzm.Variable.VTYPE_BOOL, 0, 1)
        ys = model.add_variables("y", range(10), pymzm.Variable.VTYPE_INTEGER, 9, 10)
        model.set_solve_criteria(pymzm.SOLVE_MAXIMIZE, pymzm.Expression.sum(xs) - pymzm.Expression.sum(ys))
        model.generate()
        
        result = deterministic_instance_solve(minizinc.Instance(self.gecode, model), all_solutions=False)

        self.assertTrue(result.solution is not None)
        self.assertTrue(result.objective < 0)
