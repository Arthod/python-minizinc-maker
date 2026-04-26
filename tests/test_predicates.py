import unittest
import pytest

import pymzm


pytestmark = [pytest.mark.unit]


class TestPredicates(unittest.TestCase):
    def test_predicate_declaration_and_call_render(self):
        model = pymzm.Model()
        model.add_predicate_declaration(
            "predicate leq_plus_one(int: a, int: b) = (a <= b + 1)"
        )

        x = model.add_variable("x", val_min=0, val_max=10)
        y = model.add_variable("y", val_min=0, val_max=10)
        model.add_constraint(model.call_predicate("leq_plus_one", x, y))
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        ir = model.to_ir()

        self.assertIn(
            "predicate leq_plus_one(int: a, int: b) = (a <= b + 1);",
            ir.predicate_declarations,
        )
        self.assertIn("constraint leq_plus_one(x, y);", ir.constraints)

    def test_add_predicate_call_accepts_array_arguments(self):
        model = pymzm.Model()
        model.add_predicate_declaration(
            "predicate at_least_one(array[int] of var bool: xs) = exists(i in index_set(xs))(xs[i])"
        )

        b1 = model.add_variable("b1", vtype=pymzm.Variable.VTYPE_BOOL)
        b2 = model.add_variable("b2", vtype=pymzm.Variable.VTYPE_BOOL)

        model.add_predicate_call("at_least_one", [b1, b2])
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        ir = model.to_ir()
        self.assertIn("constraint at_least_one([b1, b2]);", ir.constraints)

    def test_duplicate_predicate_declarations_are_deduplicated_in_ir(self):
        model = pymzm.Model()
        d1 = "predicate nonnegative(int: a) = (a >= 0)"
        d2 = "predicate nonnegative(int: a) = (a >= 0);"

        model.add_predicate_declaration(d1)
        model.add_predicate_declaration(d2)

        x = model.add_variable("x", val_min=0, val_max=10)
        model.add_predicate_call("nonnegative", x)
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        ir = model.to_ir()

        nonnegative_decls = [
            line for line in ir.predicate_declarations if line.startswith("predicate nonnegative")
        ]
        self.assertEqual(len(nonnegative_decls), 1)


if __name__ == "__main__":
    unittest.main()
