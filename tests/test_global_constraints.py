import unittest
import pytest

import pymzm
from tests.mzn_verifier import assert_valid_mzn


pytestmark = [pytest.mark.unit, pytest.mark.snapshot]


class TestGlobalConstraints(unittest.TestCase):
    def test_ordering_element_and_table_wrappers_render_with_includes(self):
        model = pymzm.Model()
        x = model.add_variable("x", val_min=1, val_max=3)
        y = model.add_variable("y", val_min=1, val_max=3)
        z = model.add_variable("z", val_min=1, val_max=3)
        idx = model.add_variable("idx", val_min=1, val_max=3)
        picked = model.add_variable("picked", val_min=1, val_max=9)

        model.add_constraint(pymzm.Constraint.all_different([x, y, z]))
        model.add_constraint(pymzm.Constraint.strictly_increasing([x, y, z]))
        model.add_constraint(pymzm.Constraint.strictly_decreasing([z, y, x]))
        model.add_constraint(pymzm.Constraint.element(idx, [2, 4, 9], picked))
        model.add_constraint(pymzm.Constraint.table([x, y], [[1, 2], [2, 3], [3, 1]]))
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        model.generate()

        lines = model.model_mzn_str.splitlines()
        self.assertIn('include "alldifferent.mzn";', lines)
        self.assertIn('include "strictly_increasing.mzn";', lines)
        self.assertIn('include "strictly_decreasing.mzn";', lines)
        self.assertIn('include "element.mzn";', lines)
        self.assertIn('include "table.mzn";', lines)
        self.assertIn('constraint alldifferent([x, y, z]);', lines)
        self.assertIn('constraint strictly_increasing([x, y, z]);', lines)
        self.assertIn('constraint strictly_decreasing([z, y, x]);', lines)
        self.assertIn('constraint element(idx, [2, 4, 9], picked);', lines)
        self.assertIn('constraint table([x, y], [[1, 2], [2, 3], [3, 1]]);', lines)
        assert_valid_mzn(self, model.model_mzn_str)

    def test_scheduling_graph_and_other_wrapper_families_render(self):
        model = pymzm.Model()
        s1 = model.add_variable("s1", val_min=0, val_max=5)
        s2 = model.add_variable("s2", val_min=0, val_max=5)
        n1 = model.add_variable("n1", val_min=1, val_max=3)
        n2 = model.add_variable("n2", val_min=1, val_max=3)
        n3 = model.add_variable("n3", val_min=1, val_max=3)
        p1 = model.add_variable("p1", val_min=1, val_max=3)
        p2 = model.add_variable("p2", val_min=1, val_max=3)
        p3 = model.add_variable("p3", val_min=1, val_max=3)
        b1 = model.add_variable("b1", val_min=1, val_max=2)
        b2 = model.add_variable("b2", val_min=1, val_max=2)
        left1 = model.add_variable("left1", val_min=0, val_max=3)
        left2 = model.add_variable("left2", val_min=0, val_max=3)
        right1 = model.add_variable("right1", val_min=0, val_max=3)
        right2 = model.add_variable("right2", val_min=0, val_max=3)
        sel1 = model.add_variable("sel1", vtype=pymzm.Variable.VTYPE_BOOL)
        sel2 = model.add_variable("sel2", vtype=pymzm.Variable.VTYPE_BOOL)
        edge1 = model.add_variable("edge1", vtype=pymzm.Variable.VTYPE_BOOL)
        edge2 = model.add_variable("edge2", vtype=pymzm.Variable.VTYPE_BOOL)

        model.add_constraint(pymzm.Constraint.cumulative([s1, s2], [2, 3], [1, 1], 2))
        model.add_constraint(pymzm.Constraint.disjunctive([s1, s2], [2, 3]))
        model.add_constraint(pymzm.Constraint.disjunctive_strict([s1, s2], [2, 3]))
        model.add_constraint(pymzm.Constraint.circuit([n1, n2, n3]))
        model.add_constraint(pymzm.Constraint.path([p1, p2, p3], 1, 3))
        model.add_constraint(pymzm.Constraint.bin_packing(5, [b1, b2], [2, 3]))
        model.add_constraint(pymzm.Constraint.inverse([n1, n2, n3], [p1, p2, p3]))
        model.add_constraint(pymzm.Constraint.lex_lesseq([left1, left2], [right1, right2]))
        model.add_constraint(pymzm.Constraint.lex_less([left1, left2], [right1, right2]))
        model.add_constraint(pymzm.Constraint.regular([b1, b2], 2, 2, [[1, 2], [2, 1]], 1, {1}))
        model.add_constraint(pymzm.Constraint.connected([1, 2], [2, 3], [sel1, sel2], [edge1, edge2]))
        model.add_constraint(pymzm.Constraint.reachable([1, 2], [2, 3], 1, [sel1, sel2], [edge1, edge2]))
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        ir = model.to_ir()

        self.assertEqual(
            ir.includes,
            (
                "bin_packing.mzn",
                "circuit.mzn",
                "connected.mzn",
                "cumulative.mzn",
                "disjunctive.mzn",
                "inverse.mzn",
                "lex_less.mzn",
                "lex_lesseq.mzn",
                "path.mzn",
                "reachable.mzn",
                "regular.mzn",
            ),
        )
        self.assertIn('constraint cumulative([s1, s2], [2, 3], [1, 1], 2);', ir.constraints)
        self.assertIn('constraint disjunctive([s1, s2], [2, 3]);', ir.constraints)
        self.assertIn('constraint disjunctive_strict([s1, s2], [2, 3]);', ir.constraints)
        self.assertIn('constraint circuit([n1, n2, n3]);', ir.constraints)
        self.assertIn('constraint path([p1, p2, p3], 1, 3);', ir.constraints)
        self.assertIn('constraint bin_packing(5, [b1, b2], [2, 3]);', ir.constraints)
        self.assertIn('constraint inverse([n1, n2, n3], [p1, p2, p3]);', ir.constraints)
        self.assertIn('constraint lex_lesseq([left1, left2], [right1, right2]);', ir.constraints)
        self.assertIn('constraint lex_less([left1, left2], [right1, right2]);', ir.constraints)
        self.assertIn('constraint regular([b1, b2], 2, 2, [[1, 2], [2, 1]], 1, {1});', ir.constraints)
        self.assertIn('constraint connected([1, 2], [2, 3], [sel1, sel2], [edge1, edge2]);', ir.constraints)
        self.assertIn('constraint reachable([1, 2], [2, 3], 1, [sel1, sel2], [edge1, edge2]);', ir.constraints)


if __name__ == "__main__":
    unittest.main()
