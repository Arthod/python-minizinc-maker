import unittest
import pytest

import pymzm


pytestmark = [pytest.mark.unit]


class TestEnums(unittest.TestCase):
    def test_enum_declarations_and_domain_usage(self):
        model = pymzm.Model()

        color = model.add_enum("Color", ["RED", "GREEN", "BLUE"])
        c = model.add_variable("c", domain=color)
        palette = model.add_variable("palette", vtype=pymzm.Variable.VTYPE_SET, domain=color)

        model.add_constraint(c == color.GREEN)
        model.add_constraint(palette.contains(color.RED))
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        ir = model.to_ir()

        self.assertIn("enum Color = {RED, GREEN, BLUE};", ir.declarations)
        self.assertIn("var Color: c;", ir.declarations)
        self.assertIn("var set of Color: palette;", ir.declarations)
        self.assertTrue(any("constraint (c == GREEN);" in line for line in ir.constraints))

    def test_enum_constants_render_unquoted(self):
        model = pymzm.Model()

        color = model.add_enum("Color", ["RED", "GREEN", "BLUE"])
        model.add_constant("fav", color.RED, vtype="Color")
        model.add_constant("choices", [color.RED, color.BLUE], vtype="Color")

        x = model.add_variable("x", val_min=0, val_max=1)
        model.add_constraint(x >= 0)
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        ir = model.to_ir()

        self.assertIn("Color: fav = RED;", ir.declarations)
        self.assertIn("array[1..2] of Color: choices = [RED, BLUE];", ir.declarations)

    def test_enum_member_access_styles(self):
        model = pymzm.Model()
        color = model.add_enum("Color", ["RED", "GREEN", "BLUE"])

        self.assertEqual(str(color.RED), "RED")
        self.assertEqual(str(color["GREEN"]), "GREEN")
        self.assertEqual([str(v) for v in color], ["RED", "GREEN", "BLUE"])

    def test_enum_validation_rejects_invalid_members(self):
        model = pymzm.Model()

        with self.assertRaises(ValueError):
            model.add_enum("Color", [])
        with self.assertRaises(ValueError):
            model.add_enum("Color", ["RED", "RED"])
        with self.assertRaises(ValueError):
            model.add_enum("", ["RED"])


if __name__ == "__main__":
    unittest.main()
