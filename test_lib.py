import unittest

import pymzm
import minizinc
import math

class TestPMZM(unittest.TestCase):
    def setUp(self):
        self.model = pymzm.Model()


    def test_ex1(self):
        model = self.model
        model.add_variable("x", -100, 100)

        model.add_constant("a")
        model.add_constant("b")
        model.add_constant("c")

        model.add_constraint("a*(x*x) + b*x = c")

        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        model.generate()

        # Transform Model into a instance
        gecode = minizinc.Solver.lookup("gecode")
        inst = minizinc.Instance(gecode, model)
        inst["a"] = 1
        inst["b"] = 4
        inst["c"] = 0

        # Solve the instance
        result = inst.solve(all_solutions=True)
        self.assertEqual(result[0, "x"], -4)
        self.assertEqual(result[1, "x"], 0)

    def test_ex2(self):
        model = self.model
        model.add_variable("x", 1, 10)
        model.add_constraint("(x mod 2) = 1")
        model.set_solve_method(pymzm.Method.int_search(["x"], "first_fail", "indomain_min"))
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        ####
        model.generate()

        # Transform Model into a instance
        gecode = minizinc.Solver.lookup("gecode")
        inst = minizinc.Instance(gecode, model)

        # Solve the instance
        result = inst.solve(all_solutions=True)
        vals_expected = [1, 3, 5, 7, 9]
        for i in range(len(result)):
            self.assertEqual(vals_expected[i], result[i, "x"])

    def test_ex3(self):
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


        # Transform Model into a instance
        gecode = minizinc.Solver.lookup("gecode")
        inst = minizinc.Instance(gecode, model)

        # Solve the instance
        result = inst.solve(all_solutions=True)
        
        self.assertEqual(18, len(result))

    def test_ex4_integer_factorization(self):
        model = self.model

        model.add_variable("x", 1, 99999999)
        model.add_variable("y", 1, 99999999)

        model.add_constraint(f"x * y = {7829 * 6907}")
        model.add_constraint("y > 1")
        model.add_constraint("x > y")

        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        model.generate()

        # Transform Model into a instance
        gecode = minizinc.Solver.lookup("gecode")
        inst = minizinc.Instance(gecode, model)

        # Solve the instance
        result = inst.solve(all_solutions=True)

        self.assertEqual(result[0].x, 7829)
        self.assertEqual(result[0].y, 6907)

    def test_ex5_nqueens(self):
        model = self.model

        n = 8
        q = model.add_variables("q", range(n), val_min=0, val_max=n-1)

        model.add_constraint(pymzm.Constraint.alldifferent(q))
        model.add_constraint(pymzm.Constraint.alldifferent([q[i] + i for i in range(n)]))
        model.add_constraint(pymzm.Constraint.alldifferent([q[i] - i for i in range(n)]))

        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        model.generate()

        # Transform Model into a instance
        gecode = minizinc.Solver.lookup("gecode")
        inst = minizinc.Instance(gecode, model)

        # Solve the instance
        result = inst.solve(all_solutions=True)

        self.assertEqual(92, len(result))

    def test_ex6_711(self):
        model = self.model
        n = 4
        items = model.add_variables("item", range(n), val_min=0, val_max=999)

        model.add_constraint(sum(items[a] for a in items) == 711)
        model.add_constraint(pymzm.Expression.product(items) == 711 * 100 * 100 * 100)

        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        model.generate()

        gecode = minizinc.Solver.lookup("gecode")
        inst = minizinc.Instance(gecode, model)

        result = inst.solve(all_solutions=False)

        rs = [result[f"item_{i}"] / 100 for i in range(n)]
        self.assertTrue(sum(rs) == 7.11)
        self.assertTrue(math.prod(rs) == 7.11)

    def test_ex7_bibd(self):
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
            model.add_constraint(sum(xs[i, j] for j in range(v)) == r)
        for i in range(v):
            model.add_constraint(sum(xs[j, i] for j in range(b)) == k)

        for i in range(b):
            for j in range(i):
                model.add_constraint(sum(xs[i, k] * xs[j, k] for k in range(v)) == l)

        model.set_solve_criteria("satisfy")
        model.generate()

        gecode = minizinc.Solver.lookup("gecode")
        inst = minizinc.Instance(gecode, model)
        result = inst.solve(all_solutions=False)


        for j in range(b):
            self.assertTrue(sum(result[f"x_{i}_{j}"] for i in range(v)) == r)
        for i in range(v):
            self.assertTrue(sum(result[f"x_{i}_{j}"] for j in range(b)) == r)
        # TODO add product between any pairs of rows
        for i in range(b):
            for j in range(i):
                self.assertTrue(sum(result[f"x_{i}_{k}"] * result[f"x_{j}_{k}"] for k in range(v)) == l)




if __name__ == "__main__":
    unittest.main()