import unittest
import pytest

import pymzm
from pymzm.backends import MznTextBackend
from tests.mzn_verifier import assert_valid_mzn


pytestmark = [pytest.mark.unit, pytest.mark.snapshot]


class TestOptionalConstraints(unittest.TestCase):
    def test_disabled_constraint_is_omitted_until_enabled(self):
        model = pymzm.Model()
        x = model.add_variable("x", val_min=0, val_max=3)
        active = model.add_constraint(x >= 1)
        optional = model.add_optional_constraint(x <= 2)
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        disabled_render = MznTextBackend().render_model(model.to_ir())
        self.assertIn("constraint (x >= 1);", disabled_render)
        self.assertNotIn("constraint (x <= 2);", disabled_render)

        model.enable_constraint(optional)
        enabled_render = MznTextBackend().render_model(model.to_ir())
        self.assertIn("constraint (x >= 1);", enabled_render)
        self.assertIn("constraint (x <= 2);", enabled_render)
        self.assertIs(active.enabled, True)
        assert_valid_mzn(self, enabled_render)

    def test_disabled_global_constraint_does_not_emit_include(self):
        model = pymzm.Model()
        x = model.add_variable("x", val_min=1, val_max=3)
        y = model.add_variable("y", val_min=1, val_max=3)
        optional = model.add_optional_constraint(pymzm.Constraint.alldifferent([x, y]))
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        disabled_render = MznTextBackend().render_model(model.to_ir())
        self.assertNotIn('include "alldifferent.mzn";', disabled_render)
        self.assertNotIn("constraint alldifferent", disabled_render)

        model.enable_constraint(optional)
        enabled_render = MznTextBackend().render_model(model.to_ir())
        self.assertIn('include "alldifferent.mzn";', enabled_render)
        self.assertIn("constraint alldifferent([x, y]);", enabled_render)

    def test_add_assumption_alias_can_be_disabled(self):
        model = pymzm.Model()
        x = model.add_variable("x", val_min=0, val_max=2)
        assumption = model.add_assumption(x >= 0)
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        self.assertTrue(assumption.enabled)
        model.disable_constraint(assumption)

        rendered = MznTextBackend().render_model(model.to_ir())
        self.assertNotIn("constraint (x >= 0);", rendered)


if __name__ == "__main__":
    unittest.main()
