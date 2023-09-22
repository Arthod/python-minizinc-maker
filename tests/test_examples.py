import unittest
import pymzm
import minizinc
import math
import sys

class TestExamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.append("../")

    @classmethod
    def tearDownClass(cls):
        sys.path.pop()

    def setUp(self):
        self.model = pymzm.Model()
        self.gecode = minizinc.Solver.lookup("gecode")

    def test_australia(self):
        # https://www.minizinc.org/doc-2.5.5/en/modelling.html
        model = self.model
        nc = model.add_constant("nc", value=3)
        states = ["wa", "nsw", "nt", "v", "sa", "t", "q"]
        for state in states:
            model.add_variable(state, 1, nc.value)
        model.add_constraint("wa != nt")
        model.add_constraint("wa != sa")
        model.add_constraint("nt != sa")
        model.add_constraint("nt != q")
        model.add_constraint("sa != q")
        model.add_constraint("sa != nsw")
        model.add_constraint("sa != v")
        model.add_constraint("q != nsw")
        model.add_constraint("nsw != v")
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        model.generate()

        result = minizinc.Instance(self.gecode, model).solve(all_solutions=True)
        
        self.assertTrue(result.solution is not None)
        self.assertEqual(18, len(result))

    def test_integer_factorization(self):
        model = self.model
        model.add_variable("x", 1, 99999999)
        model.add_variable("y", 1, 99999999)
        model.add_constraint(f"x * y = {7829 * 6907}")
        model.add_constraint("y > 1")
        model.add_constraint("x > y")
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        model.generate()

        result = minizinc.Instance(self.gecode, model).solve(all_solutions=True)

        self.assertTrue(result.solution is not None)
        self.assertEqual(result[0].x, 7829)
        self.assertEqual(result[0].y, 6907)

    def test_nqueens(self):
        model = self.model
        n = 8
        q = model.add_variables("q", range(n), val_min=0, val_max=n-1)
        model.add_constraint(pymzm.Constraint.alldifferent(q))
        model.add_constraint(pymzm.Constraint.alldifferent([q[i] + i for i in range(n)]))
        model.add_constraint(pymzm.Constraint.alldifferent([q[i] - i for i in range(n)]))
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        model.generate()

        result = minizinc.Instance(self.gecode, model).solve(all_solutions=True)

        self.assertTrue(result.solution is not None)
        self.assertEqual(92, len(result))

    def test_711(self):
        model = self.model
        n = 4
        items = model.add_variables("item", range(n), val_min=0, val_max=999)
        model.add_constraint(pymzm.Expression.sum(items) == 711)
        model.add_constraint(pymzm.Expression.product(items) == 711 * 100 * 100 * 100)
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        model.generate()
        
        result = minizinc.Instance(self.gecode, model).solve(all_solutions=False)

        self.assertTrue(result.solution is not None)
        rs = [result[f"item_{i}"] / 100 for i in range(n)]
        self.assertTrue(sum(rs) == 7.11)
        self.assertTrue(math.prod(rs) == 7.11)

    def test_bibd(self):
        model = self.model
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

        # Create a MiniZinc model
        xs = model.add_variables("x", indices=[(i, j) for i in range(v) for j in range(b)], vtype=pymzm.Variable.VTYPE_BOOL, val_min=0, val_max=1) # bool if object v is in block b

        for i in range(b):
            model.add_constraint(pymzm.Expression.sum(xs[i, j] for j in range(v)) == r)
        for i in range(v):
            model.add_constraint(pymzm.Expression.sum(xs[j, i] for j in range(b)) == k)

        for i in range(b):
            for j in range(i):
                model.add_constraint(pymzm.Expression.sum(xs[i, k] * xs[j, k] for k in range(v)) == l)

        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        model.generate()
        
        result = minizinc.Instance(self.gecode, model).solve(all_solutions=False)

        self.assertTrue(result.solution is not None)

        for j in range(b):
            self.assertTrue(sum(result[f"x_{i}_{j}"] for i in range(v)) == r)
        for i in range(v):
            self.assertTrue(sum(result[f"x_{i}_{j}"] for j in range(b)) == r)
        for i in range(b):
            for j in range(i):
                self.assertTrue(sum(result[f"x_{i}_{k}"] * result[f"x_{j}_{k}"] for k in range(v)) == l)

    def test_magicsquare(self):
        from pymzmaker.examples.magicsquare import magicsquare
        n = 3
        result = magicsquare(self.model, n)

        # Assert that constrains are correct
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