import unittest
from types import SimpleNamespace
from unittest.mock import ANY, MagicMock, patch

import minizinc
import pymzm


class TestModelExecution(unittest.TestCase):
    def _build_satisfy_model(self):
        model = pymzm.Model()
        x = model.add_variable("x", val_min=1, val_max=2)
        model.add_constraint(x >= 1)
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        return model

    def _build_optimize_model(self):
        model = pymzm.Model()
        x = model.add_variable("x", val_min=1, val_max=3)
        model.set_solve_criteria(pymzm.SOLVE_MAXIMIZE, x)
        return model

    @patch("pymzm.model.minizinc.Instance")
    @patch("pymzm.model.minizinc.Solver.lookup")
    def test_solve_routes_to_instance(self, solver_lookup_mock, instance_cls_mock):
        model = self._build_satisfy_model()
        solver_lookup_mock.return_value = "solver-object"

        result = object()
        instance_mock = MagicMock()
        instance_mock.solve.return_value = result
        instance_cls_mock.return_value = instance_mock

        out = model.solve(solver="gecode", timeout=123, random_seed=7, threads=3, free_search=True)

        self.assertIs(out, result)
        solver_lookup_mock.assert_called_once_with("gecode")
        instance_cls_mock.assert_called_once_with("solver-object", ANY)
        instance_mock.solve.assert_called_once_with(
            timeout=123,
            random_seed=7,
            processes=3,
            free_search=True,
            all_solutions=False,
        )

    @patch("pymzm.model.minizinc.Instance")
    @patch("pymzm.model.minizinc.Solver.lookup")
    def test_solve_all_forces_all_solutions(self, solver_lookup_mock, instance_cls_mock):
        model = self._build_satisfy_model()
        solver_lookup_mock.return_value = "solver-object"

        instance_mock = MagicMock()
        instance_mock.solve.return_value = object()
        instance_cls_mock.return_value = instance_mock

        model.solve_all(solver="gecode")

        instance_mock.solve.assert_called_once_with(
            timeout=None,
            random_seed=None,
            processes=None,
            free_search=False,
            all_solutions=True,
        )

    def test_optimize_requires_optimization_criteria(self):
        model = self._build_satisfy_model()
        with self.assertRaises(ValueError):
            model.optimize()

    @patch.object(pymzm.Model, "solve")
    def test_check_satisfiable_status_mapping(self, solve_mock):
        model = self._build_satisfy_model()

        solve_mock.return_value = SimpleNamespace(status=minizinc.Status.SATISFIED)
        self.assertTrue(model.check_satisfiable())

        solve_mock.return_value = SimpleNamespace(status=minizinc.Status.UNSATISFIABLE)
        self.assertFalse(model.check_satisfiable())


if __name__ == "__main__":
    unittest.main()
