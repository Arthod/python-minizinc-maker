import unittest
import pytest

import pymzm


pytestmark = [pytest.mark.unit, pytest.mark.snapshot, pytest.mark.no_mzn_verify]


class TestIncludes(unittest.TestCase):
    def test_user_controlled_includes_render_and_deduplicate(self):
        model = pymzm.Model()
        x = model.add_variable("x", val_min=1, val_max=3)
        y = model.add_variable("y", val_min=1, val_max=3)

        model.add_include("custom/helpers.mzn")
        model.add_includes(["globals.mzn", "custom/helpers.mzn"])
        model.add_constraint(pymzm.Constraint.alldifferent([x, y]))
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        model.generate()

        lines = model.model_mzn_str.splitlines()
        self.assertEqual(lines[0], 'include "alldifferent.mzn";')
        self.assertEqual(lines[1], 'include "custom/helpers.mzn";')
        self.assertEqual(lines[2], 'include "globals.mzn";')
        self.assertEqual(lines.count('include "custom/helpers.mzn";'), 1)

    def test_architecture_ir_contains_manual_and_auto_includes(self):
        model = pymzm.Model()
        x = model.add_variable("x", val_min=1, val_max=3)
        y = model.add_variable("y", val_min=1, val_max=3)

        model.add_include("custom/path/lib.mzn")
        model.add_constraint(pymzm.Constraint.alldifferent([x, y]))
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        model_ir = model.to_ir()
        self.assertEqual(model_ir.includes, ("alldifferent.mzn", "custom/path/lib.mzn"))


if __name__ == "__main__":
    unittest.main()
