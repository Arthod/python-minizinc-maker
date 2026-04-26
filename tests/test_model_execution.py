import unittest
from enum import Enum
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

        self.assertIs(out.raw_result, result)
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

        self.assertIs(result.raw_result, expected_result)
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

    @patch("pymzm.model.minizinc.Instance")
    @patch("pymzm.model.minizinc.Solver.lookup")
    def test_solver_config_routes_options(self, solver_lookup_mock, instance_cls_mock):
        model = self._build_satisfy_model()
        solver_lookup_mock.return_value = "solver-object"

        instance_mock = MagicMock()
        instance_mock.solve.return_value = object()
        instance_cls_mock.return_value = instance_mock

        config = pymzm.SolverConfig(
            solver="gecode",
            timeout=5,
            random_seed=9,
            threads=2,
            free_search=True,
            all_solutions=True,
            extra_solve_args={"intermediate_solutions": True},
        )

        model.solve_with(config)

        instance_mock.solve.assert_called_once_with(
            timeout=5,
            random_seed=9,
            processes=2,
            free_search=True,
            all_solutions=True,
            intermediate_solutions=True,
        )

    @patch("pymzm.model.minizinc.Instance")
    @patch("pymzm.model.minizinc.Solver.lookup")
    def test_solver_config_disallows_mixed_overrides(self, solver_lookup_mock, instance_cls_mock):
        model = self._build_satisfy_model()
        solver_lookup_mock.return_value = "solver-object"
        instance_cls_mock.return_value = MagicMock()

        config = pymzm.SolverConfig(solver="gecode")

        with self.assertRaises(ValueError):
            model.solve(solver=config, timeout=1)

    @patch("pymzm.model.minizinc.Instance")
    @patch("pymzm.model.minizinc.Solver.lookup")
    def test_last_solve_info_exposes_status_and_statistics(self, solver_lookup_mock, instance_cls_mock):
        model = self._build_satisfy_model()
        solver_lookup_mock.return_value = "solver-object"

        result_obj = SimpleNamespace(status=minizinc.Status.SATISFIED, statistics={"nodes": 12})
        instance_mock = MagicMock()
        instance_mock.solve.return_value = result_obj
        instance_cls_mock.return_value = instance_mock

        model.solve(solver="gecode")
        last = model.get_last_solve_info()

        self.assertEqual(last["solver"], "solver-object")
        self.assertEqual(last["status"], minizinc.Status.SATISFIED)
        self.assertEqual(last["statistics"], {"nodes": 12})
        self.assertIsInstance(last["result"], pymzm.SolveResult)
        self.assertIs(last["result"].raw_result, result_obj)

    @patch("pymzm.model.minizinc.Instance")
    @patch("pymzm.model.minizinc.Solver.lookup")
    def test_normalized_result_supports_dict_and_attribute_access(self, solver_lookup_mock, instance_cls_mock):
        model = self._build_satisfy_model()
        solver_lookup_mock.return_value = "solver-object"

        class FakeEnum(Enum):
            RED = 1

        raw_solution = SimpleNamespace(
            x=2,
            is_ok=True,
            ratio=1.5,
            picks={1, 2},
            arr=[1, 2, 3],
            color=FakeEnum.RED,
        )
        raw_result = SimpleNamespace(
            status=minizinc.Status.SATISFIED,
            statistics={"nodes": 3},
            solution=raw_solution,
        )

        instance_mock = MagicMock()
        instance_mock.solve.return_value = raw_result
        instance_cls_mock.return_value = instance_mock

        result = model.solve(solver="gecode")

        self.assertEqual(result["x"], 2)
        self.assertEqual(result.x, 2)
        self.assertEqual(result["is_ok"], True)
        self.assertEqual(result["ratio"], 1.5)
        self.assertEqual(result["picks"], {1, 2})
        self.assertEqual(result["arr"], [1, 2, 3])
        self.assertEqual(result["color"], "RED")
        self.assertEqual(result.status_code, "SAT")
        self.assertEqual(result.statistics, {"nodes": 3})

    @patch("pymzm.model.minizinc.Instance")
    @patch("pymzm.model.minizinc.Solver.lookup")
    def test_normalized_result_supports_all_solution_index_access(self, solver_lookup_mock, instance_cls_mock):
        model = self._build_satisfy_model()
        solver_lookup_mock.return_value = "solver-object"

        raw_result = SimpleNamespace(
            status=minizinc.Status.ALL_SOLUTIONS,
            statistics={"nodes": 10},
            solution=[SimpleNamespace(x=1), SimpleNamespace(x=2)],
        )

        instance_mock = MagicMock()
        instance_mock.solve.return_value = raw_result
        instance_cls_mock.return_value = instance_mock

        result = model.solve(solver="gecode", all_solutions=True)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].x, 1)
        self.assertEqual(result[1]["x"], 2)
        self.assertEqual(result.status_code, "SAT")

    def test_status_code_normalization_covers_unsat_unknown_error_optimal(self):
        unsat = pymzm.SolveResult(SimpleNamespace(status=minizinc.Status.UNSATISFIABLE, solution=None))
        unknown = pymzm.SolveResult(SimpleNamespace(status=minizinc.Status.UNKNOWN, solution=None))
        error = pymzm.SolveResult(SimpleNamespace(status=minizinc.Status.ERROR, solution=None))
        optimal = pymzm.SolveResult(SimpleNamespace(status=minizinc.Status.OPTIMAL_SOLUTION, solution=SimpleNamespace(x=1)))

        self.assertEqual(unsat.status_code, "UNSAT")
        self.assertEqual(unknown.status_code, "UNKNOWN")
        self.assertEqual(error.status_code, "ERROR")
        self.assertEqual(optimal.status_code, "OPTIMAL")
        self.assertTrue(optimal.is_optimal)


if __name__ == "__main__":
    unittest.main()
