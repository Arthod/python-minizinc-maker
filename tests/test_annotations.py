import unittest
import pytest

import pymzm


pytestmark = [pytest.mark.unit]


class TestAnnotations(unittest.TestCase):
    def test_expression_level_annotations_in_constraint_and_objective(self):
        model = pymzm.Model()
        x = model.add_variable("x", val_min=0, val_max=10)

        annotated_constraint = (x >= 0).annotate("domain")
        annotated_objective = (x + 1).annotate("promise_total")

        model.add_constraint(annotated_constraint)
        model.set_solve_criteria(pymzm.SOLVE_MAXIMIZE, annotated_objective)

        rendered = pymzm.MznTextBackend().render_model(model.to_ir())

        self.assertIn("constraint (x >= 0) :: domain;", rendered)
        self.assertIn("solve maximize (x + 1) :: promise_total;", rendered)

    def test_variable_annotations_render_in_declarations(self):
        model = pymzm.Model()

        x = model.add_variable(
            "x",
            val_min=0,
            val_max=1,
            annotations=["is_defined_var", pymzm.Annotation("output_var")],
        )
        x.annotate("var_is_introduced")

        model.set_solve_criteria(pymzm.SOLVE_SATISFY)
        ir = model.to_ir()

        self.assertIn(
            "var 0..1: x :: is_defined_var :: output_var :: var_is_introduced;",
            ir.declarations,
        )

    def test_add_variables_accepts_annotation_mapping(self):
        model = pymzm.Model()

        vars_by_idx = model.add_variables(
            "x",
            indices=[0, 1],
            val_min=0,
            val_max=2,
            annotations={0: "output_var", 1: ["is_defined_var", "var_is_introduced"]},
        )
        model.add_constraint(vars_by_idx[0] >= 0)
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        ir = model.to_ir()
        self.assertIn("var 0..2: x_0 :: output_var;", ir.declarations)
        self.assertIn("var 0..2: x_1 :: is_defined_var :: var_is_introduced;", ir.declarations)

    def test_solve_annotations_render_with_search_and_restart(self):
        model = pymzm.Model()
        x = model.add_variable("x", val_min=0, val_max=2)

        method = pymzm.IntSearch(
            [x],
            pymzm.AnnotationVariableChoice.VARCHOICE_INPUT_ORDER,
            pymzm.AnnotationValueChoice.VALCHOICE_INDOMAIN_MIN,
        )
        model.set_solve_method(method, pymzm.RestartLuby(100))
        model.set_solve_annotations(["complete", pymzm.Annotation("warm_start", "[x]", "[1]")])
        model.set_solve_criteria(pymzm.SOLVE_SATISFY)

        rendered = pymzm.MznTextBackend().render_model(model.to_ir())

        self.assertIn(
            "solve :: int_search([x], input_order, indomain_min) :: restart_luby(100) :: complete :: warm_start([x], [1]) satisfy;",
            rendered,
        )


if __name__ == "__main__":
    unittest.main()
