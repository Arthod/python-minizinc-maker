import unittest
import pytest

import pymzm
from tests.mzn_verifier import assert_valid_mzn


pytestmark = [pytest.mark.integration]


class TestGlobalConstraintsIntegration(unittest.TestCase):
    def _mk_int_vars(self, model, prefix, count, val_min=1, val_max=5):
        return [
            model.add_variable(f"{prefix}{i}", val_min=val_min, val_max=val_max)
            for i in range(count)
        ]

    def test_all_global_wrappers_emit_valid_mzn(self):
        cases = []

        def add_case(name, builder):
            cases.append((name, builder))

        add_case(
            "alldifferent",
            lambda m: pymzm.Constraint.alldifferent(self._mk_int_vars(m, "x", 3, 1, 3)),
        )
        add_case(
            "all_different",
            lambda m: pymzm.Constraint.all_different(self._mk_int_vars(m, "x", 3, 1, 3)),
        )
        add_case(
            "among",
            lambda m: pymzm.Constraint.among(2, self._mk_int_vars(m, "x", 3, 1, 3), [1]),
        )
        add_case(
            "all_equal",
            lambda m: pymzm.Constraint.all_equal(self._mk_int_vars(m, "x", 3, 1, 3)),
        )
        add_case(
            "count",
            lambda m: pymzm.Constraint.count(self._mk_int_vars(m, "x", 3, 1, 3), 1, 1),
        )
        add_case(
            "increasing",
            lambda m: pymzm.Constraint.increasing(self._mk_int_vars(m, "x", 3, 1, 5)),
        )
        add_case(
            "strictly_increasing",
            lambda m: pymzm.Constraint.strictly_increasing(self._mk_int_vars(m, "x", 3, 1, 5)),
        )
        add_case(
            "decreasing",
            lambda m: pymzm.Constraint.decreasing(self._mk_int_vars(m, "x", 3, 1, 5)),
        )
        add_case(
            "strictly_decreasing",
            lambda m: pymzm.Constraint.strictly_decreasing(self._mk_int_vars(m, "x", 3, 1, 5)),
        )
        add_case(
            "element",
            lambda m: pymzm.Constraint.element(
                m.add_variable("idx", val_min=1, val_max=3),
                [1, 2, 3],
                m.add_variable("picked", val_min=1, val_max=3),
            ),
        )
        add_case(
            "table",
            lambda m: pymzm.Constraint.table(
                self._mk_int_vars(m, "x", 2, 1, 3),
                [[1, 2], [2, 3], [3, 1]],
            ),
        )
        add_case(
            "cumulative",
            lambda m: pymzm.Constraint.cumulative(
                self._mk_int_vars(m, "s", 2, 0, 5), [2, 3], [1, 1], 2
            ),
        )
        add_case(
            "disjunctive",
            lambda m: pymzm.Constraint.disjunctive(self._mk_int_vars(m, "s", 2, 0, 5), [2, 3]),
        )
        add_case(
            "disjunctive_strict",
            lambda m: pymzm.Constraint.disjunctive_strict(self._mk_int_vars(m, "s", 2, 0, 5), [2, 3]),
        )
        add_case(
            "circuit",
            lambda m: pymzm.Constraint.circuit(self._mk_int_vars(m, "n", 3, 1, 3)),
        )
        add_case(
            "path",
            lambda m: pymzm.Constraint.path(self._mk_int_vars(m, "p", 3, 1, 3), 1, 3),
        )
        add_case(
            "bin_packing",
            lambda m: pymzm.Constraint.bin_packing(5, self._mk_int_vars(m, "b", 2, 1, 2), [2, 3]),
        )
        add_case(
            "inverse",
            lambda m: pymzm.Constraint.inverse(
                self._mk_int_vars(m, "f", 3, 1, 3),
                self._mk_int_vars(m, "g", 3, 1, 3),
            ),
        )
        add_case(
            "lex_less",
            lambda m: pymzm.Constraint.lex_less(
                self._mk_int_vars(m, "l", 2, 0, 3),
                self._mk_int_vars(m, "r", 2, 0, 3),
            ),
        )
        add_case(
            "lex_lesseq",
            lambda m: pymzm.Constraint.lex_lesseq(
                self._mk_int_vars(m, "l", 2, 0, 3),
                self._mk_int_vars(m, "r", 2, 0, 3),
            ),
        )
        add_case(
            "lex_greater",
            lambda m: pymzm.Constraint.lex_greater(
                self._mk_int_vars(m, "l", 2, 0, 3),
                self._mk_int_vars(m, "r", 2, 0, 3),
            ),
        )
        add_case(
            "lex_greatereq",
            lambda m: pymzm.Constraint.lex_greatereq(
                self._mk_int_vars(m, "l", 2, 0, 3),
                self._mk_int_vars(m, "r", 2, 0, 3),
            ),
        )
        add_case(
            "regular",
            lambda m: pymzm.Constraint.regular(
                self._mk_int_vars(m, "x", 2, 1, 2),
                2,
                2,
                [[1, 2], [2, 1]],
                1,
                {1},
            ),
        )
        add_case(
            "arg_sort",
            lambda m: pymzm.Constraint.arg_sort(
                self._mk_int_vars(m, "x", 3, 1, 3),
                self._mk_int_vars(m, "p", 3, 1, 3),
            ),
        )
        add_case(
            "diffn",
            lambda m: pymzm.Constraint.diffn(
                self._mk_int_vars(m, "x", 2, 0, 2),
                self._mk_int_vars(m, "y", 2, 0, 2),
                [1, 1],
                [1, 1],
            ),
        )
        add_case(
            "connected",
            lambda m: pymzm.Constraint.connected(
                [1, 2],
                [2, 3],
                [
                    m.add_variable("ns1", vtype=pymzm.Variable.VTYPE_BOOL),
                    m.add_variable("ns2", vtype=pymzm.Variable.VTYPE_BOOL),
                    m.add_variable("ns3", vtype=pymzm.Variable.VTYPE_BOOL),
                ],
                [
                    m.add_variable("es1", vtype=pymzm.Variable.VTYPE_BOOL),
                    m.add_variable("es2", vtype=pymzm.Variable.VTYPE_BOOL),
                ],
            ),
        )
        add_case(
            "reachable",
            lambda m: pymzm.Constraint.reachable(
                [1, 2],
                [2, 3],
                1,
                [
                    m.add_variable("ns1", vtype=pymzm.Variable.VTYPE_BOOL),
                    m.add_variable("ns2", vtype=pymzm.Variable.VTYPE_BOOL),
                    m.add_variable("ns3", vtype=pymzm.Variable.VTYPE_BOOL),
                ],
                [
                    m.add_variable("es1", vtype=pymzm.Variable.VTYPE_BOOL),
                    m.add_variable("es2", vtype=pymzm.Variable.VTYPE_BOOL),
                ],
            ),
        )

        for name, builder in cases:
            with self.subTest(wrapper=name):
                model = pymzm.Model()
                model.add_constraint(builder(model))
                model.set_solve_criteria(pymzm.SOLVE_SATISFY)
                model.generate()
                assert_valid_mzn(self, model.model_mzn_str)


if __name__ == "__main__":
    unittest.main()
