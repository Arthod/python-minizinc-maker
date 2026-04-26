import inspect
import unittest

import pytest

import pymzm


pytestmark = [pytest.mark.unit]


class TestApiTypeHints(unittest.TestCase):
    def test_model_public_methods_have_parameter_and_return_annotations(self):
        methods = [
            "add_constant",
            "add_parameter",
            "add_parameters",
            "add_variable",
            "add_variables",
            "add_constraint",
            "add_output",
            "solve",
            "solve_with",
            "solve_with_data",
            "optimize",
            "check_satisfiable",
            "to_ir",
        ]

        for method_name in methods:
            method = getattr(pymzm.Model, method_name)
            sig = inspect.signature(method)

            self.assertIsNot(sig.return_annotation, inspect._empty, method_name)
            for name, param in sig.parameters.items():
                if (name in {"self", "kwargs", "args"}):
                    continue
                self.assertIsNot(param.annotation, inspect._empty, f"{method_name}.{name}")

    def test_solver_config_with_updates_is_typed(self):
        sig = inspect.signature(pymzm.SolverConfig.with_updates)
        self.assertIsNot(sig.return_annotation, inspect._empty)


if __name__ == "__main__":
    unittest.main()
