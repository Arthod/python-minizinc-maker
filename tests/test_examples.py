import unittest
import pymzm
import minizinc
import math
import sys
import os
from pathlib import Path
import pytest

repo_root = Path(__file__).resolve().parents[1]
if (str(repo_root) not in sys.path):
    sys.path.insert(0, str(repo_root))

from tests.solver_utils import deterministic_instance_solve, lookup_default_solver


pytestmark = [pytest.mark.integration]

class TestExamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "\\..")

    @classmethod
    def tearDownClass(cls):
        sys.path.pop()

    def setUp(self):
        self.model = pymzm.Model()
        self.gecode = lookup_default_solver()

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

        result = deterministic_instance_solve(minizinc.Instance(self.gecode, model), all_solutions=True)
        
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
        self.assertAlmostEqual(sum(rs), 7.11, places=2)
        self.assertAlmostEqual(math.prod(rs), 7.11, places=2)

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
        from examples.sudoku import sudoku
        result = sudoku(self.model, self.gecode)

        # Assert that solution is correct
        self.assertTrue(result.solution is not None)
        digits = set(range(1, 10))

        for i in range(9):
            row = {result[f"x_{i}_{j}"] for j in range(9)}
            self.assertEqual(row, digits)
        for j in range(9):
            col = {result[f"x_{i}_{j}"] for i in range(9)}
            self.assertEqual(col, digits)

        clues = {
            (0, 1): 4,
            (0, 2): 3,
            (0, 4): 8,
            (0, 6): 2,
            (0, 7): 5,
            (1, 0): 6,
            (2, 5): 1,
            (2, 7): 9,
            (2, 8): 4,
            (3, 0): 9,
            (3, 5): 4,
            (3, 7): 7,
            (4, 3): 6,
            (4, 5): 8,
            (5, 1): 1,
            (5, 3): 2,
            (5, 8): 3,
            (6, 0): 8,
            (6, 1): 2,
            (6, 3): 5,
            (7, 8): 5,
            (8, 1): 3,
            (8, 2): 4,
            (8, 4): 9,
            (8, 6): 7,
            (8, 7): 1,
        }
        for (i, j), val in clues.items():
            self.assertEqual(result[f"x_{i}_{j}"], val)

    def test_sat(self):
        from examples.sat import sat
        result = sat(self.model, self.gecode)

        # Assert that solution is correct
        self.assertTrue(result.solution is not None)
        x0 = bool(result["x_0"])
        x1 = bool(result["x_1"])
        x2 = bool(result["x_2"])
        x3 = bool(result["x_3"])

        self.assertTrue(x0 or x1 or (not x2))
        self.assertTrue(x1 or x2 or (not x3))
        self.assertTrue(x0 or (not x1) or x3)

    def test_bin_packing(self):
        from examples.bin_packing import bin_packing
        cap = 10
        sizes = [6, 6, 6, 5, 3, 3, 2, 2, 2, 2, 2]

        result = bin_packing(self.model, self.gecode, cap, sizes)

        # Assert that solution is correct
        self.assertTrue(result.solution is not None)

        bins_ub = len(sizes)
        for i in range(bins_ub):
            load = result[f"bin_load_{i}"]
            self.assertGreaterEqual(load, 0)
            self.assertLessEqual(load, cap)

        for j in range(len(sizes)):
            assigned = sum(int(result[f"bin_item_{i}_{j}"]) for i in range(bins_ub))
            self.assertEqual(assigned, 1)

    def test_wedding_seating(self):
        from examples.wedding_seating import (
            wedding_seating,
            guests,
            males,
            females,
            bride,
            groom,
            ed,
        )
        result = wedding_seating(self.model, self.gecode)

        # Assert that solution is correct
        self.assertTrue(result.solution is not None)

        seat_values = [result[f"seat_{guest}"] for guest in guests]
        self.assertEqual(len(set(seat_values)), len(guests))

        for male in males:
            self.assertEqual(result[f"seat_{male}"] % 2, 1)
        for female in females:
            self.assertEqual(result[f"seat_{female}"] % 2, 0)

        self.assertNotIn(result[f"seat_{ed}"], {1, 6, 7, 12})

        seat_bride = result[f"seat_{bride}"]
        seat_groom = result[f"seat_{groom}"]
        self.assertEqual(abs(seat_groom - seat_bride), 1)
        self.assertEqual(seat_groom <= 6, seat_bride <= 6)

if __name__ == "__main__":
    unittest.main()