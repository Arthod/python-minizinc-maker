import unittest
import pymzm
import minizinc
import math
import sys
import os

class TestExamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "\\..")

    @classmethod
    def tearDownClass(cls):
        sys.path.pop()

    def setUp(self):
        self.model = pymzm.Model()
        self.gecode = minizinc.Solver.lookup("gecode")

    def test_australia(self):
        # https://www.minizinc.org/doc-2.5.5/en/modelling.html
        model = self.model
        nc = 3
        states = ["wa", "nsw", "nt", "v", "sa", "t", "q"]
        s = model.add_variables("state", states, val_min=1, val_max=nc)
        model.add_constraint(s["wa"] != s["nt"])
        model.add_constraint(s["wa"] != s["sa"])
        model.add_constraint(s["nt"] != s["sa"])
        model.add_constraint(s["nt"] != s["q"])
        model.add_constraint(s["sa"] != s["q"])
        model.add_constraint(s["sa"] != s["nsw"])
        model.add_constraint(s["sa"] != s["v"])
        model.add_constraint(s["q"] != s["nsw"])
        model.add_constraint(s["nsw"] != s["v"])
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        model.generate()

        result = minizinc.Instance(self.gecode, model).solve(all_solutions=True)
        
        # Assert that solution is correct
        self.assertTrue(result.solution is not None)
        self.assertEqual(18, len(result))

    def test_integer_factorization(self):
        from examples.intfact import intfact
        n1 = 7829
        n2 = 6907
        result = intfact(self.model, self.gecode, n1, n2)

        # Assert that solution is correct
        self.assertTrue(result.solution is not None)
        self.assertEqual(result[0].x, n1)
        self.assertEqual(result[0].y, n2)

    def test_nqueens(self):
        from examples.nqueens import nqueens
        n = 8
        result = nqueens(self.model, self.gecode, n)

        # Assert that solution is correct
        self.assertTrue(result.solution is not None)
        self.assertEqual(92, len(result))

    def test_711(self):
        from examples.pr711 import pr711
        n = 4
        result = pr711(self.model, self.gecode, n)

        # Assert that solution is correct
        self.assertTrue(result.solution is not None)
        rs = [result[f"item_{i}"] / 100 for i in range(n)]
        self.assertTrue(sum(rs) == 7.11)
        self.assertTrue(math.prod(rs) == 7.11)

    def test_bibd(self):
        from examples.bibd import bibd
        # BIBD generation is described in most standard textbooks on combinatorics. 
        # A BIBD is defined as an arrangement of v  distinct objects into b blocks 
        # such that each block contains exactly k distinct objects, each object 
        # occurs in exactly r different blocks, and every two distinct objects 
        # occur together in exactly λ blocks.
        v = 7
        b = 7
        r = 3
        k = 3
        l = 1

        result = bibd(self.model, self.gecode, v, b, r, k, l)

        # Assert that solution is correct
        self.assertTrue(result.solution is not None)
        for j in range(b):
            self.assertTrue(sum(result[f"x_{i}_{j}"] for i in range(v)) == r)
        for i in range(v):
            self.assertTrue(sum(result[f"x_{i}_{j}"] for j in range(b)) == r)
        for i in range(b):
            for j in range(i):
                self.assertTrue(sum(result[f"x_{i}_{k}"] * result[f"x_{j}_{k}"] for k in range(v)) == l)

    def test_magicsquare(self):
        from examples.magicsquare import magicsquare
        n = 3
        result = magicsquare(self.model, self.gecode, n)

        # Assert that solution is correct
        y_sol = int(n * (n * n + 1) / 2)
        self.assertEqual(result["y"], y_sol)
        self.assertEqual(sum(result[f"x_{i}_{i}"] for i in range(n)), y_sol)
        self.assertEqual(sum(result[f"x_{i}_{n - 1 - i}"] for i in range(n)), y_sol)
        for i in range(n):
            self.assertEqual(sum(result[f"x_{i}_{j}"] for j in range(n)), y_sol)
        for j in range(n):
            self.assertEqual(sum(result[f"x_{i}_{j}"] for i in range(n)), y_sol)

    def test_sudoku(self):
        pass

    def test_sat(self):
        pass

if __name__ == "__main__":
    unittest.main()