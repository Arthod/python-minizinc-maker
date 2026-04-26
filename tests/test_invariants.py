"""Tests for public-boundary invariants that were previously bare asserts."""

import pytest

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pymzm import (
    Model,
    Variable,
    Constraint,
    PymzmArgumentError,
    PymzmModelStateError,
    PymzmSolveNotConfigured,
    PymzmConstraintNotInModel,
    PymzmVariableTypeError,
)
from pymzm.model import SOLVE_MAXIMIZE, SOLVE_SATISFY, SearchAnnotation, SeqSearch, RestartStrategy


# ---------------------------------------------------------------------------
# Model.to_ir() – solve criteria required
# ---------------------------------------------------------------------------


def test_to_ir_no_solve_criteria_raises():
    m = Model()
    with pytest.raises(PymzmSolveNotConfigured):
        m.to_ir()


# ---------------------------------------------------------------------------
# Model.set_solve_criteria()
# ---------------------------------------------------------------------------


def test_set_solve_criteria_optimize_requires_expr():
    m = Model()
    with pytest.raises(PymzmArgumentError):
        m.set_solve_criteria(SOLVE_MAXIMIZE, expr=None)


def test_set_solve_criteria_satisfy_forbids_expr():
    m = Model()
    v = m.add_variable("x", Variable.VTYPE_INTEGER, 0, 5)
    with pytest.raises(PymzmArgumentError):
        m.set_solve_criteria(SOLVE_SATISFY, expr=v)


# ---------------------------------------------------------------------------
# Model.set_solve_method()
# ---------------------------------------------------------------------------


def test_set_solve_method_wrong_type_raises():
    m = Model()
    with pytest.raises(PymzmArgumentError):
        m.set_solve_method("bad_method")


def test_set_solve_method_wrong_restart_strategy_raises():
    m = Model()
    v = m.add_variable("x", Variable.VTYPE_INTEGER, 0, 5)
    ann = SearchAnnotation("int_search", [v], "input_order", "indomain_min")
    with pytest.raises(PymzmArgumentError):
        m.set_solve_method(ann, restart_strategy="bad")


# ---------------------------------------------------------------------------
# Model.set_constraint_enabled()
# ---------------------------------------------------------------------------


def test_set_constraint_enabled_not_in_model_raises():
    m = Model()
    c = Constraint("x > 0")
    with pytest.raises(PymzmConstraintNotInModel):
        m.set_constraint_enabled(c, True)


# ---------------------------------------------------------------------------
# Model.add_include()
# ---------------------------------------------------------------------------


def test_add_include_empty_string_raises():
    m = Model()
    with pytest.raises(PymzmArgumentError):
        m.add_include("   ")


# ---------------------------------------------------------------------------
# Model.add_function_declaration() / add_predicate_declaration()
# ---------------------------------------------------------------------------


def test_add_function_declaration_empty_raises():
    m = Model()
    with pytest.raises(PymzmArgumentError):
        m.add_function_declaration("  ")


def test_add_predicate_declaration_empty_raises():
    m = Model()
    with pytest.raises(PymzmArgumentError):
        m.add_predicate_declaration("  ")


# ---------------------------------------------------------------------------
# Variable type guards
# ---------------------------------------------------------------------------


def test_variable_len_non_set_raises():
    v = Variable("x", Variable.VTYPE_INTEGER, 0, 5)
    with pytest.raises(PymzmVariableTypeError):
        len(v)


def test_variable_min_non_set_raises():
    v = Variable("x", Variable.VTYPE_INTEGER, 0, 5)
    with pytest.raises(PymzmVariableTypeError):
        Variable.min(v)


def test_variable_max_non_set_raises():
    v = Variable("x", Variable.VTYPE_INTEGER, 0, 5)
    with pytest.raises(PymzmVariableTypeError):
        Variable.max(v)


def test_variable_contains_non_set_raises():
    v = Variable("x", Variable.VTYPE_INTEGER, 0, 5)
    with pytest.raises(PymzmVariableTypeError):
        v.contains(3)


def test_variable_intersection_length_non_set_raises():
    v1 = Variable("x", Variable.VTYPE_INTEGER, 0, 5)
    v2 = Variable("y", Variable.VTYPE_SET, 0, 5)
    with pytest.raises(PymzmVariableTypeError):
        Variable.intersection_length(v1, v2)


def test_variable_intersection_length_second_non_set_raises():
    v1 = Variable("x", Variable.VTYPE_SET, 0, 5)
    v2 = Variable("y", Variable.VTYPE_INTEGER, 0, 5)
    with pytest.raises(PymzmVariableTypeError):
        Variable.intersection_length(v1, v2)
