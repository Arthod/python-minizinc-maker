import unittest
import pytest

import pymzm


pytestmark = [pytest.mark.unit, pytest.mark.snapshot]


class TestDeterministicGeneration(unittest.TestCase):
    def _build_model_variant_a(self):
        model = pymzm.Model()
        model.add_constant("b", 2)
        model.add_constant("a", 1)

        y = model.add_variable("y", val_min=1, val_max=3)
        x = model.add_variable("x", val_min=1, val_max=3)

        model.add_constraint(pymzm.Constraint.count([x, y], 1, 1))
        model.add_constraint(pymzm.Constraint.alldifferent([x, y]))
        model.add_function_declaration("function int: my_f(int: v) = v + 1")
        model.add_predicate_declaration("predicate my_p(int: v) = v >= 1")
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        return model

    def _build_model_variant_b(self):
        model = pymzm.Model()
        model.add_constant("a", 1)
        model.add_constant("b", 2)

        x = model.add_variable("x", val_min=1, val_max=3)
        y = model.add_variable("y", val_min=1, val_max=3)

        model.add_constraint(pymzm.Constraint.count([x, y], 1, 1))
        model.add_constraint(pymzm.Constraint.alldifferent([x, y]))
        model.add_function_declaration("function int: my_f(int: v) = v + 1;")
        model.add_predicate_declaration("predicate my_p(int: v) = v >= 1;")
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        return model

    def test_generate_is_deterministic_for_symbols_and_includes(self):
        model_a = self._build_model_variant_a()
        model_b = self._build_model_variant_b()

        model_a.generate()
        model_b.generate()

        self.assertEqual(model_a.model_mzn_str, model_b.model_mzn_str)

        lines = model_a.model_mzn_str.splitlines()
        self.assertEqual('include "alldifferent.mzn";', lines[0])
        self.assertEqual('include "count.mzn";', lines[1])
        self.assertIn('int: a = 1;', lines)
        self.assertIn('int: b = 2;', lines)
        self.assertLess(lines.index('int: a = 1;'), lines.index('int: b = 2;'))
        self.assertLess(lines.index('var 1..3: x;'), lines.index('var 1..3: y;'))


if __name__ == "__main__":
    unittest.main()
