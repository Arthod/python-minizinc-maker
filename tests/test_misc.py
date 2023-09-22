import unittest

import pymzm
import minizinc

class TestMisc(unittest.TestCase):
    def setUp(self):
        self.model = pymzm.Model()
        self.gecode = minizinc.Solver.lookup("gecode")

    def test_misc1(self):
        model = self.model
        # Negative summation
        xs = model.add_variables("x", range(10), 0, 1, vtype=pymzm.Variable.VTYPE_BOOL)
        ys = model.add_variables("y", range(10), 9, 10, vtype=pymzm.Variable.VTYPE_INTEGER)
        model.set_solve_criteria(pymzm.SOLVE_MAXIMIZE, pymzm.Expression.sum(xs) - pymzm.Expression.sum(ys))
        model.generate()
        
        result = minizinc.Instance(self.gecode, model).solve(all_solutions=False)

        self.assertTrue(result.solution is not None)
        self.assertTrue(result.objective < 0)
