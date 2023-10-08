import inspect
import unittest

import pymzm
import minizinc

import equiv
from functools import partial


class TestExpression(unittest.TestCase):
    def setUp(self):
        self.solver = minizinc.Solver.lookup("gecode")
        self.val_min = -100
        self.val_max = 100

        self.model = pymzm.Model()
        self.x = self.model.add_variable("x", val_min=self.val_min, val_max=self.val_max)
        self.xs = self.model.add_variables("xs", range(10), val_min=self.val_min, val_max=self.val_max)
        self.y = self.model.add_variable("y", vtype=pymzm.Variable.VTYPE_BOOL)

    def _operator_case_single(self, func, positive_only=False, val_max: int=None):
        model = pymzm.Model()
        val_min = 0 if positive_only else self.val_min
        val_max = self.val_max if val_max is None else val_max
        
        x = model.add_variable("x", vtype=pymzm.Variable.VTYPE_INTEGER, val_min=val_min, val_max=val_max)
        model.add_constraint(func(x))
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        model.generate()

        sols = []
        for i in range(val_min, val_max + 1):
            try:
                if (func(i)):
                    sols.append(i)
            except ZeroDivisionError:
                pass
        #if (len(sols) == 0): print(inspect.getsource(func))

        results = minizinc.Instance(self.solver, model).solve(all_solutions=True)

        self.assertTrue(results.solution is not None)
        self.assertEqual(len(sols), len(results), f"{sols}, {results}")
        for i in range(len(results)):
            self.assertTrue(func(results[i, "x"]))
    
    def _operator_case_multiple(self, func_expr, method_mz, method_py=None, var_count: int=5, is_solveable=True):
        model = pymzm.Model()
        
        xs = model.add_variables("x", range(var_count), vtype=pymzm.Variable.VTYPE_INTEGER, val_min=self.val_min, val_max=self.val_max)

        func_mz = partial(func_expr, method_mz)
        func_py = partial(func_expr, method_py) if method_py is not None else None

        model.add_constraint(func_mz(xs))
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        model.generate()

        result = minizinc.Instance(self.solver, model).solve(all_solutions=False)

        if (is_solveable):
            self.assertTrue(result.solution is not None)
            if (func_py is None):
                func_py = func_mz
            answ = func_py([result[f"x_{i}"] for i in range(var_count)])
            self.assertIsInstance(answ, bool) # for some reason non bools evaluate to true
            self.assertTrue(answ)

    def test_native_sum(self):
        # Valid
        sum(x for x in self.xs)
        sum([x for x in self.xs])
        sum(self.xs)
        #sum(self.xs[0], self.xs[1], self.y)

        self._operator_case_multiple(lambda f, xs: 0 + f(xs) == 27, sum, var_count=5)
        self._operator_case_multiple(lambda f, xs: 0 - f(xs) == 31, sum, var_count=5)
        self._operator_case_multiple(lambda f, xs: 5 * f(xs) == 30, sum, var_count=5)
        self._operator_case_multiple(lambda f, xs: f(xs) * f(xs) == 25, sum, var_count=2)
        self._operator_case_multiple(lambda f, xs: - f(xs) == 14, sum, var_count=5)

        expr = sum(self.xs)
        self.assertIsInstance(expr, pymzm.Expression)
        
        # Invalid
        #self.assertRaises(pymzm.PymzmValueIsNotExpression,
        #    sum,
        #    ["test", self.xs[0]])
        #self.assertRaises(pymzm.PymzmValueIsNotExpression,
        #    sum,
        #    [[self.xs[1]], self.xs[0]])
        #self.assertRaises(pymzm.PymzmValueIsNotExpression,
        #    sum,
        #    self.xs[0])
        #self.assertRaises(pymzm.PymzmValueIsNotExpression,
        #    sum,
        #    "test")
        #self.assertRaises(pymzm.PymzmNoValues,
        #    sum,
        #    [])

    def test_sum(self):
        # Valid
        pymzm.Expression.sum(x for x in self.xs)
        pymzm.Expression.sum([x for x in self.xs])
        pymzm.Expression.sum(self.xs)
        #pymzm.Expression.sum(self.xs[0], self.xs[1], self.y)

        self._operator_case_multiple(lambda f, xs: 0 + f(xs) == 27, pymzm.Expression.sum, sum, var_count=5)
        self._operator_case_multiple(lambda f, xs: 0 - f(xs) == 31, pymzm.Expression.sum, sum, var_count=5)
        self._operator_case_multiple(lambda f, xs: 5 * f(xs) == 30, pymzm.Expression.sum, sum, var_count=5)
        self._operator_case_multiple(lambda f, xs: f(xs) * f(xs) == 25, pymzm.Expression.sum, sum, var_count=2)
        self._operator_case_multiple(lambda f, xs: - f(xs) == 14, pymzm.Expression.sum, sum, var_count=5)

        expr = pymzm.Expression.sum(self.xs)
        self.assertIsInstance(expr, pymzm.Expression)
        
        # Invalid
        self.assertRaises(pymzm.PymzmValueIsNotExpression,
            pymzm.Expression.sum,
            ["test", self.xs[0]])
        self.assertRaises(pymzm.PymzmValueIsNotExpression,
            pymzm.Expression.sum,
            [[self.xs[1]], self.xs[0]])
        self.assertRaises(pymzm.PymzmValueIsNotExpression,
            pymzm.Expression.sum,
            self.xs[0])
        self.assertRaises(pymzm.PymzmValueIsNotExpression,
            pymzm.Expression.sum,
            "test")
        self.assertRaises(pymzm.PymzmNoValues,
            pymzm.Expression.sum,
            [])

    def test_product(self):
        # Valid
        pymzm.Expression.product(x for x in self.xs)
        pymzm.Expression.product([x for x in self.xs])
        pymzm.Expression.product(self.xs)
        #pymzm.Expression.product(self.xs[0], self.xs[1], self.y)

        self._operator_case_multiple(lambda f, xs: 0 + f(xs) == 2*1*1, pymzm.Expression.product, equiv.Expression.product, var_count=3)
        self._operator_case_multiple(lambda f, xs: 0 - f(xs) == 5*6*(-3), pymzm.Expression.product, equiv.Expression.product, var_count=3)
        self._operator_case_multiple(lambda f, xs: 5 * f(xs) == 11*5*1, pymzm.Expression.product, equiv.Expression.product, var_count=3)
        self._operator_case_multiple(lambda f, xs: f(xs) + f(xs) == 2*11*6*2, pymzm.Expression.product, equiv.Expression.product, var_count=3)
        self._operator_case_multiple(lambda f, xs: - f(xs) == 5*5*5, pymzm.Expression.product, equiv.Expression.product, var_count=3)

        expr = pymzm.Expression.product(self.xs)
        self.assertIsInstance(expr, pymzm.Expression)
        
        # Invalid
        self.assertRaises(pymzm.PymzmValueIsNotExpression,
            pymzm.Expression.product,
            ["test", self.xs[0]])
        self.assertRaises(pymzm.PymzmValueIsNotExpression,
            pymzm.Expression.product,
            [[self.xs[1]], self.xs[0]])
        self.assertRaises(pymzm.PymzmValueIsNotExpression,
            pymzm.Expression.product,
            self.xs[0])
        self.assertRaises(pymzm.PymzmValueIsNotExpression,
            pymzm.Expression.product,
            "test")
        self.assertRaises(pymzm.PymzmNoValues,
            pymzm.Expression.product,
            [])

    def test_min(self):
        # Valid
        pymzm.Expression.min(x for x in self.xs)
        pymzm.Expression.min([x for x in self.xs])
        pymzm.Expression.min(self.xs)

        self._operator_case_multiple(lambda f, xs: f([*xs, 5]) == 5, pymzm.Expression.min, min, var_count=5)
        self._operator_case_multiple(lambda f, xs: f([*xs, 2]) == 5, pymzm.Expression.min, min, var_count=5, is_solveable=False)
        self._operator_case_multiple(lambda f, xs: f([*xs, 7]) == 5, pymzm.Expression.min, min, var_count=5)
        self._operator_case_multiple(lambda f, xs: f([*xs, -5]) == 5, pymzm.Expression.min, min, var_count=5, is_solveable=False)

        expr = pymzm.Expression.min(self.xs)
        self.assertIsInstance(expr, pymzm.Expression)
        
        # Invalid
        self.assertRaises(pymzm.PymzmValueIsNotExpression,
            pymzm.Expression.min,
            ["test", self.xs[0]])
        self.assertRaises(pymzm.PymzmValueIsNotExpression,
            pymzm.Expression.min,
            [[self.xs[1]], self.xs[0]])
        self.assertRaises(pymzm.PymzmValueIsNotExpression,
            pymzm.Expression.min,
            self.xs[0])
        self.assertRaises(pymzm.PymzmValueIsNotExpression,
            pymzm.Expression.min,
            "test")
        self.assertRaises(pymzm.PymzmNoValues,
            pymzm.Expression.min,
            [])

    def test_max(self):
        # Valid
        pymzm.Expression.max(x for x in self.xs)
        pymzm.Expression.max([x for x in self.xs])
        pymzm.Expression.max(self.xs)

        self._operator_case_multiple(lambda f, xs: f([*xs, 5]) == 5, pymzm.Expression.max, max, var_count=5)
        self._operator_case_multiple(lambda f, xs: f([*xs, 2]) == 5, pymzm.Expression.max, max, var_count=5, is_solveable=False)
        self._operator_case_multiple(lambda f, xs: f([*xs, 7]) == 5, pymzm.Expression.max, max, var_count=5, is_solveable=False)
        self._operator_case_multiple(lambda f, xs: f([*xs, -5]) == 5, pymzm.Expression.max, max, var_count=5, is_solveable=False)

        expr = pymzm.Expression.max(self.xs)
        self.assertIsInstance(expr, pymzm.Expression)
        
        # Invalid
        self.assertRaises(pymzm.PymzmValueIsNotExpression,
            pymzm.Expression.max,
            ["test", self.xs[0]])
        self.assertRaises(pymzm.PymzmValueIsNotExpression,
            pymzm.Expression.max,
            [[self.xs[1]], self.xs[0]])
        self.assertRaises(pymzm.PymzmValueIsNotExpression,
            pymzm.Expression.max,
            self.xs[0])
        self.assertRaises(pymzm.PymzmValueIsNotExpression,
            pymzm.Expression.max,
            "test")
        self.assertRaises(pymzm.PymzmNoValues,
            pymzm.Expression.max,
            [])

    def test_funcs_pow(self):
        self._operator_case_single(lambda x: pow(x, 2) == 81)
        self._operator_case_single(lambda x: pow(x, 2) == 5)
        self._operator_case_single(lambda x: pow(x, 3) == 27)
        self._operator_case_single(lambda x: pow(2, x) == 64, val_max=10)
        self._operator_case_single(lambda x: x ** 2 == 81)
        self._operator_case_single(lambda x: x ** 2 == 5)
        self._operator_case_single(lambda x: x ** 3 == 27)
        self._operator_case_single(lambda x: 3 ** x == 243, val_max=10)
        
        expr = pymzm.Expression.product(self.xs)
        self.assertIsInstance(expr, pymzm.Expression)

    def test_funcs_abs(self):
        self._operator_case_single(lambda x: abs(-x) == 81)
        self._operator_case_single(lambda x: -abs(x) == 5)
        self._operator_case_single(lambda x: abs(x) == 27)
        self._operator_case_single(lambda x: abs(x) == -27)

        expr = pymzm.Expression.product(self.xs)
        self.assertIsInstance(expr, pymzm.Expression)

    def test_add(self):
        self._operator_case_single(lambda x: x + x == 4)
        self._operator_case_single(lambda x: 5 + x == 4)
        self._operator_case_single(lambda x: x + 4 == 4)
        
        self.assertIsInstance(self.x + self.x, pymzm.Expression)
        self.assertIsInstance(5 + self.x, pymzm.Expression)
        self.assertIsInstance(self.x + 5, pymzm.Expression)

    def test_sub(self):
        self._operator_case_single(lambda x: x - x == 4)
        self._operator_case_single(lambda x: 5 - x == 4)
        self._operator_case_single(lambda x: x - 4 == 4)
        
        self.assertIsInstance(self.x - self.x, pymzm.Expression)
        self.assertIsInstance(5 - self.x, pymzm.Expression)
        self.assertIsInstance(self.x - 5, pymzm.Expression)

    def test_mul(self):
        self._operator_case_single(lambda x: x * x == 16)
        self._operator_case_single(lambda x: 5 * x == 10)
        self._operator_case_single(lambda x: x * 4 == 4)
        
        self.assertIsInstance(self.x * self.x, pymzm.Expression)
        self.assertIsInstance(5 * self.x, pymzm.Expression)
        self.assertIsInstance(self.x * 5, pymzm.Expression)

    def test_truediv(self):
        self._operator_case_single(lambda x: x / x == 1)
        self._operator_case_single(lambda x: 20 / x == 10)
        self._operator_case_single(lambda x: x / 2 == 4)
        
        self.assertIsInstance(self.x / self.x, pymzm.Expression)
        self.assertIsInstance(2 / self.x, pymzm.Expression)
        self.assertIsInstance(self.x / 2, pymzm.Expression)

    def test_floordiv(self):
        self._operator_case_single(lambda x: x // x == 1)
        self._operator_case_single(lambda x: 30 // x == 10)
        self._operator_case_single(lambda x: x // 4 == 4)
        
        self.assertIsInstance(self.x // self.x, pymzm.Expression)
        self.assertIsInstance(5 // self.x, pymzm.Expression)
        self.assertIsInstance(self.x // 5, pymzm.Expression)

    def test_mod(self):
        self._operator_case_single(lambda x: x % x == 0, positive_only=True)
        self._operator_case_single(lambda x: 5 % x == 2, positive_only=True)
        self._operator_case_single(lambda x: x % 4 == 3, positive_only=True)
        
        self.assertIsInstance(self.x % self.x, pymzm.Expression)
        self.assertIsInstance(5 % self.x, pymzm.Expression)
        self.assertIsInstance(self.x % 5, pymzm.Expression)

    def test_neg(self):
        self._operator_case_single(lambda x: - x == 16)
        self._operator_case_single(lambda x: - x == -3)
        
        self.assertIsInstance(-self.x, pymzm.Expression)

    def test_ifthenelse(self):
        # Invalid
        self.assertRaises(pymzm.PymzmValueIsNotCondition, 
            pymzm.Expression.ifthenelse,
            self.xs[0] + self.xs[1], self.xs[3], self.xs[4])
        self.assertRaises(pymzm.PymzmValueIsNotExpression, 
            pymzm.Expression.ifthenelse,
            self.y, "test", self.xs[4])
        self.assertRaises(pymzm.PymzmValueIsNotExpression, 
            pymzm.Expression.ifthenelse,
            self.y, self.xs[4], "test")
        self.assertRaises(pymzm.PymzmValueIsNotExpression, 
            pymzm.Expression.ifthenelse,
            self.y > self.xs[1], self.xs[4], "test")
        
        # Valid
        pymzm.Expression.ifthenelse(self.y, self.y, self.xs[4])
        pymzm.Expression.ifthenelse(self.xs[0] >= self.xs[1], self.y, self.xs[4])
        pymzm.Expression.ifthenelse(self.xs[1] >= self.y, self.y, self.xs[4])

        expr = pymzm.Expression.ifthenelse(self.xs[1] >= self.y, self.y, self.xs[4])
        self.assertIsInstance(expr, pymzm.Expression)

if __name__ == "__main__":
    t = TestExpression()
    t.setUpClass()
    t.setUp()
    t.test_ifthenelse()

    unittest.main()