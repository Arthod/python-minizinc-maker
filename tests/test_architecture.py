import unittest
import pytest

import pymzm

from pymzm.backends import MznTextBackend


pytestmark = [pytest.mark.unit]


class TestArchitecture(unittest.TestCase):
    def test_model_to_ir_and_backend_render(self):
        model = pymzm.Model()
        x = model.add_variable("x", val_min=1, val_max=3)
        y = model.add_variable("y", val_min=1, val_max=3)
        model.add_constraint(pymzm.Constraint.alldifferent([x, y]))
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        model_ir = model.to_ir()

        self.assertEqual(model_ir.includes, ("alldifferent.mzn",))
        self.assertTrue(any(line.startswith("var 1..3: x;") for line in model_ir.declarations))
        self.assertTrue(any(line.startswith("var 1..3: y;") for line in model_ir.declarations))
        self.assertTrue(any(line.startswith("constraint alldifferent") for line in model_ir.constraints))

        expected = MznTextBackend().render_model(model_ir)
        model.generate()
        self.assertEqual(model.model_mzn_str, expected)


if __name__ == "__main__":
    unittest.main()
