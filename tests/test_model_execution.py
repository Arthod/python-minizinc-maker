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
    def test_solve_can_request_all_solutions(self, solver_lookup_mock, instance_cls_mock):
        model = self._build_satisfy_model()
        solver_lookup_mock.return_value = "solver-object"

        instance_mock = MagicMock()
        instance_mock.solve.return_value = object()
        instance_cls_mock.return_value = instance_mock

        model.solve(solver="gecode", all_solutions=True)

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

    @patch("pymzm.model.minizinc.Model")
    @patch("pymzm.model.minizinc.Instance")
    @patch("pymzm.model.minizinc.Solver.lookup")
    def test_solve_creates_runtime_model_in_memory(self, solver_lookup_mock, instance_cls_mock, runtime_model_cls_mock):
        model = self._build_satisfy_model()
        solver_lookup_mock.return_value = "solver-object"

        runtime_model = MagicMock()
        runtime_model_cls_mock.return_value = runtime_model

        expected_result = object()
        instance_mock = MagicMock()
        instance_mock.solve.return_value = expected_result
        instance_cls_mock.return_value = instance_mock

        result = model.solve(solver="gecode")

        self.assertIs(result, expected_result)
        runtime_model.add_string.assert_called_once()
        rendered_text = runtime_model.add_string.call_args.args[0]
        self.assertIsInstance(rendered_text, str)
        self.assertIn("solve satisfy;", rendered_text)
        instance_cls_mock.assert_called_once_with("solver-object", runtime_model)

    @patch.object(pymzm.Model, "solve")
    def test_check_satisfiable_status_mapping(self, solve_mock):
        model = self._build_satisfy_model()

        solve_mock.return_value = SimpleNamespace(status=minizinc.Status.SATISFIED)
        self.assertTrue(model.check_satisfiable())

        solve_mock.return_value = SimpleNamespace(status=minizinc.Status.UNSATISFIABLE)
        self.assertFalse(model.check_satisfiable())


if __name__ == "__main__":
    unittest.main()
