import unittest
import pytest

import pymzm
from pymzm.backends import MznTextBackend
from tests.mzn_verifier import assert_valid_mzn


pytestmark = [pytest.mark.unit, pytest.mark.snapshot]


class TestOutputSections(unittest.TestCase):
    def test_output_items_render_after_solve(self):
        model = pymzm.Model()
        x = model.add_variable("x", val_min=1, val_max=3)
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        model.add_output(["x=", x, "\n"])

        rendered = MznTextBackend().render_model(model.to_ir())

        self.assertIn("solve satisfy;\noutput [\"x=\", show(x), \"\\n\"];\n", rendered)
        self.assertIn('output ["x=", show(x), "\\n"];', rendered)

    def test_output_sections_and_json_sections_render(self):
        model = pymzm.Model()
        x = model.add_variable("x", val_min=1, val_max=3)
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        model.add_output(["plain=", x])
        model.add_output(["sec=", x], section="custom_section")
        model.add_output(["json=", x], json_section="api")

        ir = model.to_ir()

        self.assertEqual(
            ir.output_items,
            (
                'output ["plain=", show(x)];',
                'output ["sec=", show(x)] :: "custom_section";',
                'output ["json=", show(x)] :: json_section("api");',
            ),
        )

    def test_output_helper_api_and_valid_mzn(self):
        model = pymzm.Model()
        x = model.add_variable("x", val_min=0, val_max=5)
        model.add_constraint(x >= 0)
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        model.add_output_kv("x", x, "\n")
        model.generate()

        self.assertIn('output ["x=", show(x), "\\n"];', model.model_mzn_str)
        assert_valid_mzn(self, model.model_mzn_str)


if __name__ == "__main__":
    unittest.main()
