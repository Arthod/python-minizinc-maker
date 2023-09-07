import unittest

import lib
import minizinc

class TestLib(unittest.TestCase):
    def test_ex1(self):
        model = lib.SDUMZModel()
        model.add_variable("x", -100, 100)

        model.add_constant("a")
        model.add_constant("b")
        model.add_constant("c")

        model.add_constraint("a*(x*x) + b*x = c")

        model.set_solve_criteria("satisfy")

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
        model = lib.SDUMZModel()

        model.add_variable("x", 1, 10)
        model.add_constraint("(x mod 2) = 1")
        model.set_solve_method(lib.Method.int_search(["x"], "first_fail", "indomain_min"))
        model.set_solve_criteria("satisfy")

        ####
        model.generate()
        #model.write("model.mzn")

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
        model = lib.SDUMZModel()

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

        model.set_solve_criteria("satisfy")

    def test_ex4_integer_factorization(self):

        model = lib.SDUMZModel()

        model.add_variable("x", 1, 99999999)
        model.add_variable("y", 1, 99999999)

        model.add_constraint(f"x * y = {7829 * 6907}")
        model.add_constraint("y > 1")
        model.add_constraint("x > y")

        model.set_solve_criteria("satisfy")

if __name__ == "__main__":
    unittest.main()