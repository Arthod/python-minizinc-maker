
from typing import Sequence, Union

from .exceptions import *
from .expression import *

class AnnotationConstraint:
    ANNOTATIONS = [
        ANNOTATION_BOUNDS,
        ANNOTATION_BOUNDS_PROPAGATION,
        ANNOTATION_BOUNDS_Z,
        ANNOTATION_BOUNDS_R,
        ANNOTATION_BOUNDS_D,
        ANNOTATION_DOMAIN,
        ANNOTATION_DOMAIN_PROPAGATION,
        ANNOTATION_VALUE_PROPAGATION,
        # Priority(k)
    ] = [
        "bounds",
        "bounds_propagation",
        "boundsZ",
        "boundsR",
        "boundsD",
        "domain",
        "domain_propagation",
        "value_propagation",
    ]

class Constraint:
    ExprLike = Union[Expression, int, float, bool, str]

    CTYPES = [
        CTYPE_NORMAL,
        CTYPE_ALLDIFFERENT,
        CTYPE_AMONG,
        CTYPE_ALL_EQUAL,
        CTYPE_COUNT,
        CTYPE_INCREASING,
        CTYPE_STRICTLY_INCREASING,
        CTYPE_DECREASING,
        CTYPE_STRICTLY_DECREASING,
        CTYPE_ELEMENT,
        CTYPE_TABLE,
        CTYPE_CUMULATIVE,
        CTYPE_DISJUNCTIVE,
        CTYPE_CIRCUIT,
        CTYPE_PATH,
        CTYPE_BIN_PACKING,
        CTYPE_INVERSE,
        CTYPE_LEX_LESS,
        CTYPE_LEX_LESSEQ,
        CTYPE_LEX_GREATER,
        CTYPE_LEX_GREATEREQ,
        CTYPE_REGULAR,
        CTYPE_ARG_SORT,
        CTYPE_DIFFN,
        CTYPE_CONNECTED,
        CTYPE_REACHABLE
    ] = [
        "normal",
        "alldifferent",
        "among",
        "all_equal",
        "count",
        "increasing",
        "strictly_increasing",
        "decreasing",
        "strictly_decreasing",
        "element",
        "table",
        "cumulative",
        "disjunctive",
        "circuit",
        "path",
        "bin_packing",
        "inverse",
        "lex_less",
        "lex_lesseq",
        "lex_greater",
        "lex_greatereq",
        "regular",
        "arg_sort",
        "diffn",
        "connected",
        "reachable"
    ]
    # Canonical alias for naming consistency with all_different(...).
    CTYPE_ALL_DIFFERENT = CTYPE_ALLDIFFERENT
    PUBLIC_CTYPES = tuple(CTYPES)

    def __init__(self, cstr: ExpressionBool, ctype: str=CTYPE_NORMAL, annotation: str=None, is_redundant=False, enabled=True):
        self.cstr = cstr
        if (not isinstance(self.cstr, (ExpressionBool, bool, str))):
            raise PymzmValueIsNotCondition("cstr", self.cstr)

        self.ctype = ctype # This variable shouldn't be changed by the user
        if (self.ctype not in Constraint.CTYPES):
            raise PymzmInvalidConstraintType("ctype", self.ctype)

        self.annotation = annotation
        if (self.annotation is not None):
            if (self.annotation not in AnnotationConstraint.ANNOTATIONS):
                raise PymzmInvalidConstraintAnnotation("annotation", self.annotation)
            
        self.is_redundant = is_redundant
        self.enabled = enabled

    def __str__(self):
        return self.cstr
    
    def _to_mz(self):
        annotation_suffix = ""
        if (self.annotation is not None):
            annotation_suffix = f" :: {self.annotation}"

        if (self.is_redundant):
            return f"constraint redundant_constraint({self.cstr}){annotation_suffix};\n"
        else:
            return f"constraint {self.cstr}{annotation_suffix};\n"

    @staticmethod
    def _from_global_constraint(func: str, ctype: str, *args) -> "Constraint":
        return Constraint(f"{func}({', '.join(str(a) for a in args)})", ctype)

    @staticmethod
    def _as_non_empty_list(values, arg_name: str):
        values = list(values)
        assert len(values) > 0, f"{arg_name} cannot be empty"
        return values

    @staticmethod
    def _assert_same_length(arg_name_left: str, left, arg_name_right: str, right):
        assert len(left) == len(right), f"{arg_name_left} and {arg_name_right} must have the same length"

    @staticmethod
    def _normalize_and_match(left_name: str, left, right_name: str, right):
        left = Constraint._as_non_empty_list(left, left_name)
        right = Constraint._as_non_empty_list(right, right_name)
        Constraint._assert_same_length(left_name, left, right_name, right)
        return left, right

    @staticmethod
    def alldifferent(exprs: Sequence[ExprLike]) -> "Constraint":
        exprs = Constraint._as_non_empty_list(exprs, "exprs")
        return Constraint._from_global_constraint("alldifferent", Constraint.CTYPE_ALLDIFFERENT, exprs)

    @staticmethod
    def all_different(exprs: Sequence[ExprLike]) -> "Constraint":
        return Constraint.alldifferent(exprs)
    
    @staticmethod
    def among(n: ExprLike, exprs: Sequence[ExprLike], values: Sequence[ExprLike]) -> "Constraint":
        exprs = Constraint._as_non_empty_list(exprs, "exprs")
        values = Constraint._as_non_empty_list(values, "values")
        return Constraint._from_global_constraint("among", Constraint.CTYPE_AMONG, n, exprs, values)
    
    @staticmethod
    def all_equal(exprs: Sequence[ExprLike]) -> "Constraint":
        exprs = Constraint._as_non_empty_list(exprs, "exprs")
        return Constraint._from_global_constraint("all_equal", Constraint.CTYPE_ALL_EQUAL, exprs)
    
    @staticmethod
    def count(exprs: Sequence[ExprLike], val: ExprLike, count: ExprLike) -> "Constraint":
        exprs = Constraint._as_non_empty_list(exprs, "exprs")
        return Constraint._from_global_constraint("count", Constraint.CTYPE_COUNT, exprs, val, count)
    
    @staticmethod
    def increasing(exprs: Sequence[ExprLike]) -> "Constraint":
        # Requires that the array x is in (non-strictly) increasing order (duplicates are allowed).
        exprs = Constraint._as_non_empty_list(exprs, "exprs")
        return Constraint._from_global_constraint("increasing", Constraint.CTYPE_INCREASING, exprs)

    @staticmethod
    def strictly_increasing(exprs: Sequence[ExprLike]) -> "Constraint":
        exprs = Constraint._as_non_empty_list(exprs, "exprs")
        return Constraint._from_global_constraint("strictly_increasing", Constraint.CTYPE_STRICTLY_INCREASING, exprs)

    @staticmethod
    def decreasing(exprs: Sequence[ExprLike]) -> "Constraint":
        # Requires that the array x is in (non-strictly) decreasing order (duplicates are allowed).
        exprs = Constraint._as_non_empty_list(exprs, "exprs")
        return Constraint._from_global_constraint("decreasing", Constraint.CTYPE_DECREASING, exprs)

    @staticmethod
    def strictly_decreasing(exprs: Sequence[ExprLike]) -> "Constraint":
        exprs = Constraint._as_non_empty_list(exprs, "exprs")
        return Constraint._from_global_constraint("strictly_decreasing", Constraint.CTYPE_STRICTLY_DECREASING, exprs)

    @staticmethod
    def element(index: ExprLike, values: Sequence[ExprLike], value: ExprLike) -> "Constraint":
        values = Constraint._as_non_empty_list(values, "values")
        return Constraint._from_global_constraint("element", Constraint.CTYPE_ELEMENT, index, values, value)

    @staticmethod
    def table(exprs: Sequence[ExprLike], rows: Sequence[Sequence[ExprLike]]) -> "Constraint":
        exprs = Constraint._as_non_empty_list(exprs, "exprs")
        rows = Constraint._as_non_empty_list(rows, "rows")
        assert all(len(row) == len(exprs) for row in rows), "all table rows must match exprs width"
        return Constraint._from_global_constraint("table", Constraint.CTYPE_TABLE, exprs, rows)

    @staticmethod
    def cumulative(s: Sequence[ExprLike], d: Sequence[ExprLike], r: Sequence[ExprLike], b: ExprLike) -> "Constraint":
        s = Constraint._as_non_empty_list(s, "s")
        d = Constraint._as_non_empty_list(d, "d")
        r = Constraint._as_non_empty_list(r, "r")
        Constraint._assert_same_length("s", s, "d", d)
        Constraint._assert_same_length("s", s, "r", r)
        return Constraint._from_global_constraint("cumulative", Constraint.CTYPE_CUMULATIVE, s, d, r, b)
    
    @staticmethod
    def disjunctive(s: Sequence[ExprLike], d: Sequence[ExprLike]) -> "Constraint":
        # Requires that a set of tasks given by start times s and durations d do not overlap in time. 
        # Tasks with duration 0 can be scheduled at any time, even in the middle of other tasks.
        s, d = Constraint._normalize_and_match("s", s, "d", d)
        return Constraint._from_global_constraint("disjunctive", Constraint.CTYPE_DISJUNCTIVE, s, d)
    
    @staticmethod
    def disjunctive_strict(s: Sequence[ExprLike], d: Sequence[ExprLike]) -> "Constraint":
        # Requires that a set of tasks given by start times s and durations d do not overlap in time. 
        # Tasks with duration 0 CANNOT be scheduled at any time, but only when no other task is running.
        s, d = Constraint._normalize_and_match("s", s, "d", d)
        return Constraint._from_global_constraint("disjunctive_strict", Constraint.CTYPE_DISJUNCTIVE, s, d)

    @staticmethod
    def circuit(successors: Sequence[ExprLike]) -> "Constraint":
        successors = Constraint._as_non_empty_list(successors, "successors")
        return Constraint._from_global_constraint("circuit", Constraint.CTYPE_CIRCUIT, successors)

    @staticmethod
    def path(successors: Sequence[ExprLike], start: ExprLike, end: ExprLike) -> "Constraint":
        successors = Constraint._as_non_empty_list(successors, "successors")
        return Constraint._from_global_constraint("path", Constraint.CTYPE_PATH, successors, start, end)

    @staticmethod
    def bin_packing(capacity: ExprLike, bins: Sequence[ExprLike], weights: Sequence[ExprLike]) -> "Constraint":
        bins, weights = Constraint._normalize_and_match("bins", bins, "weights", weights)
        return Constraint._from_global_constraint("bin_packing", Constraint.CTYPE_BIN_PACKING, capacity, bins, weights)

    @staticmethod
    def inverse(forward: Sequence[ExprLike], backward: Sequence[ExprLike]) -> "Constraint":
        forward, backward = Constraint._normalize_and_match("forward", forward, "backward", backward)
        return Constraint._from_global_constraint("inverse", Constraint.CTYPE_INVERSE, forward, backward)

    @staticmethod
    def lex_less(left: Sequence[ExprLike], right: Sequence[ExprLike]) -> "Constraint":
        left, right = Constraint._normalize_and_match("left", left, "right", right)
        return Constraint._from_global_constraint("lex_less", Constraint.CTYPE_LEX_LESS, left, right)

    @staticmethod
    def lex_lesseq(left: Sequence[ExprLike], right: Sequence[ExprLike]) -> "Constraint":
        left, right = Constraint._normalize_and_match("left", left, "right", right)
        return Constraint._from_global_constraint("lex_lesseq", Constraint.CTYPE_LEX_LESSEQ, left, right)

    @staticmethod
    def lex_greater(left: Sequence[ExprLike], right: Sequence[ExprLike]) -> "Constraint":
        left, right = Constraint._normalize_and_match("left", left, "right", right)
        return Constraint._from_global_constraint("lex_greater", Constraint.CTYPE_LEX_GREATER, left, right)

    @staticmethod
    def lex_greatereq(left: Sequence[ExprLike], right: Sequence[ExprLike]) -> "Constraint":
        left, right = Constraint._normalize_and_match("left", left, "right", right)
        return Constraint._from_global_constraint("lex_greatereq", Constraint.CTYPE_LEX_GREATEREQ, left, right)

    @staticmethod
    def regular(
        exprs: Sequence[ExprLike],
        q: ExprLike,
        s: ExprLike,
        d: Sequence[Sequence[ExprLike]],
        q0: ExprLike,
        f: Sequence[ExprLike],
    ) -> "Constraint":
        exprs = Constraint._as_non_empty_list(exprs, "exprs")
        d = Constraint._as_non_empty_list(d, "d")
        if (isinstance(f, set)):
            assert len(f) > 0, "f cannot be empty"
        else:
            f = Constraint._as_non_empty_list(f, "f")
        return Constraint._from_global_constraint("regular", Constraint.CTYPE_REGULAR, exprs, q, s, d, q0, f)
    
    @staticmethod
    def arg_sort(x: Sequence[ExprLike], p: Sequence[ExprLike]) -> "Constraint":
        # Constrains p to be the permutation which causes x to be in sorted order hence x[p[i]] <= x[p[i+1]].
        x, p = Constraint._normalize_and_match("x", x, "p", p)
        return Constraint._from_global_constraint("arg_sort", Constraint.CTYPE_ARG_SORT, x, p)
    
    @staticmethod
    def diffn(x: Sequence[ExprLike], y: Sequence[ExprLike], dx: Sequence[ExprLike], dy: Sequence[ExprLike]) -> "Constraint":
        # Constrains rectangles i, given by their origins (x[i], y[i]) and sizes (dx[i], dy[i]),
        # to be non-overlapping. Zero-width rectangles can still not overlap with any other rectangle.
        x = Constraint._as_non_empty_list(x, "x")
        y = Constraint._as_non_empty_list(y, "y")
        dx = Constraint._as_non_empty_list(dx, "dx")
        dy = Constraint._as_non_empty_list(dy, "dy")
        Constraint._assert_same_length("x", x, "y", y)
        Constraint._assert_same_length("x", x, "dx", dx)
        Constraint._assert_same_length("x", x, "dy", dy)
        return Constraint._from_global_constraint("diffn", Constraint.CTYPE_DIFFN, x, y, dx, dy)
    
    @staticmethod
    def connected(
        node_from: Sequence[int],
        node_to: Sequence[int],
        ns: Sequence[ExprLike],
        es: Sequence[ExprLike],
    ) -> "Constraint":
        # Constrains the subgraph ns and es of a given undirected graph to be connected.
        node_from = Constraint._as_non_empty_list(node_from, "node_from")
        node_to = Constraint._as_non_empty_list(node_to, "node_to")
        ns = Constraint._as_non_empty_list(ns, "ns")
        es = Constraint._as_non_empty_list(es, "es")
        Constraint._assert_same_length("node_from", node_from, "node_to", node_to)
        Constraint._assert_same_length("node_from", node_from, "es", es)
        return Constraint._from_global_constraint("connected", Constraint.CTYPE_CONNECTED, node_from, node_to, ns, es)
    
    @staticmethod
    def reachable(
        node_from: Sequence[int],
        node_to: Sequence[int],
        r: ExprLike,
        ns: Sequence[ExprLike],
        es: Sequence[ExprLike],
    ) -> "Constraint":
        # Constrains the subgraph ns and es of a given undirected graph to be reachable from r.
        node_from = Constraint._as_non_empty_list(node_from, "node_from")
        node_to = Constraint._as_non_empty_list(node_to, "node_to")
        ns = Constraint._as_non_empty_list(ns, "ns")
        es = Constraint._as_non_empty_list(es, "es")
        Constraint._assert_same_length("node_from", node_from, "node_to", node_to)
        Constraint._assert_same_length("node_from", node_from, "es", es)
        return Constraint._from_global_constraint("reachable", Constraint.CTYPE_REACHABLE, node_from, node_to, r, ns, es)