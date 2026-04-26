import unittest

import pytest

import pymzm


pytestmark = [pytest.mark.unit]


class TestExceptionsHierarchy(unittest.TestCase):
    def test_exception_hierarchy_is_structured(self):
        self.assertTrue(issubclass(pymzm.PymzmValidationError, pymzm.PymzmException))
        self.assertTrue(issubclass(pymzm.PymzmArgumentError, pymzm.PymzmValidationError))
        self.assertTrue(issubclass(pymzm.PymzmConfigurationError, pymzm.PymzmValidationError))
        self.assertTrue(issubclass(pymzm.PymzmModelStateError, pymzm.PymzmValidationError))

    def test_invalid_solve_criteria_message_is_actionable(self):
        model = pymzm.Model()

        with self.assertRaises(pymzm.PymzmInvalidSolveCriteria) as ctx:
            model.set_solve_criteria("solve_fast")

        self.assertIn("Expected one of", str(ctx.exception))
        self.assertIn("solve_fast", str(ctx.exception))

    def test_constant_none_uses_specific_exception(self):
        with self.assertRaises(pymzm.PymzmNonInitializedConstant) as ctx:
            pymzm.Constant("c", None)

        self.assertIn("not initialized", str(ctx.exception))
        self.assertIn("add_parameter(..., value=None)", str(ctx.exception))

    def test_invalid_constraint_input_uses_constraint_type_exception(self):
        model = pymzm.Model()

        with self.assertRaises(pymzm.PymzmInvalidConstraintType) as ctx:
            model.add_constraint(object())

        self.assertIn("constraint", str(ctx.exception))
        self.assertIn("expected one of", str(ctx.exception))

    def test_invalid_variable_type_uses_specific_exception(self):
        with self.assertRaises(pymzm.PymzmUnsupportedVariableType) as ctx:
            pymzm.Variable("x", vtype="bad")

        self.assertIn("unsupported variable type", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
