import unittest
from unittest.mock import MagicMock, patch
import pytest

import pymzm
from tests.solver_utils import (
    DEFAULT_RANDOM_SEED,
    DEFAULT_SOLVER_TAG,
    DEFAULT_THREADS,
    deterministic_instance_solve,
    deterministic_solver_config,
    lookup_default_solver,
)


pytestmark = [pytest.mark.unit]


class TestSolverUtils(unittest.TestCase):
    @patch("tests.solver_utils.minizinc.Solver.lookup")
    def test_lookup_default_solver_uses_gecode(self, lookup_mock):
        sentinel = object()
        lookup_mock.return_value = sentinel

        solver = lookup_default_solver()

        self.assertIs(solver, sentinel)
        lookup_mock.assert_called_once_with(DEFAULT_SOLVER_TAG)

    def test_deterministic_solver_config_defaults(self):
        config = deterministic_solver_config()

        self.assertIsInstance(config, pymzm.SolverConfig)
        self.assertEqual(config.solver, DEFAULT_SOLVER_TAG)
        self.assertEqual(config.random_seed, DEFAULT_RANDOM_SEED)
        self.assertEqual(config.threads, DEFAULT_THREADS)
        self.assertFalse(config.all_solutions)
        self.assertFalse(config.free_search)

    def test_deterministic_solver_config_overrides(self):
        config = deterministic_solver_config(
            solver="chuffed",
            all_solutions=True,
            random_seed=99,
            threads=4,
            intermediate_solutions=True,
        )

        self.assertEqual(config.solver, "chuffed")
        self.assertTrue(config.all_solutions)
        self.assertEqual(config.random_seed, 99)
        self.assertEqual(config.threads, 4)
        self.assertEqual(config.extra_solve_args["intermediate_solutions"], True)

    def test_deterministic_instance_solve_passes_stable_options(self):
        instance = MagicMock()
        expected_result = object()
        instance.solve.return_value = expected_result

        result = deterministic_instance_solve(instance, all_solutions=True)

        self.assertIs(result, expected_result)
        instance.solve.assert_called_once_with(
            all_solutions=True,
            random_seed=DEFAULT_RANDOM_SEED,
            processes=DEFAULT_THREADS,
            free_search=False,
        )


if __name__ == "__main__":
    unittest.main()
