
from typing import List

from .exceptions import *
from .expression import *

class AnnotationConstraint:
    ANNOTATIONS = [
        ANNOTATION_BOUNDS,
        ANNOTATION_BOUNDS_Z,
        ANNOTATION_BOUNDS_R,
        ANNOTATION_BOUNDS_D,
        ANNOTATION_DOMAIN,
        ANNOTATION_VALUE_PROPAGATION,
        # Priority(k)
    ] = [
        "bounds",
        "boundsZ",
        "boundsR",
        "boundsD",
        "domain",
        "value_propagation",
    ]

class Constraint:
    CTYPES = [
        CTYPE_NORMAL,
        CTYPE_ALLDIFFERENT,
        CTYPE_AMONG,
        CTYPE_ALL_EQUAL,
        CTYPE_COUNT,
        CTYPE_INCREASING,
        CTYPE_DECREASING,
        CTYPE_DISJUNCTIVE,
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
        "decreasing",
        "disjunctive",
        "arg_sort",
        "diffn",
        "connected",
        "reachable"
    ]
    def __init__(self, cstr: ExpressionBool, ctype: str=CTYPE_NORMAL, annotation: str=None, is_redundant=False):
        self.cstr = cstr
        if (not isinstance(self.cstr, (ExpressionBool, bool, str))):
            raise PymzmValueIsNotCondition("cstr", self.cstr)

        self.ctype = ctype # This variable shouldn't be changed by the user
        if (self.ctype not in Constraint.CTYPES):
            raise PymzmInvalidConstraintType("ctype")

        self.annotation = annotation
        if (self.annotation is not None):
            if (self.annotation not in AnnotationConstraint.ANNOTATIONS):
                raise PymzmInvalidConstraintAnnotation("annotation")
            
        self.is_redundant = is_redundant

    def __str__(self):
        return self.cstr
    
    def _to_mz(self):
        if (self.is_redundant):
            return f"constraint redundant_constraint({self.cstr});\n"
        else:
            return f"constraint {self.cstr};\n"

    @staticmethod
    def _from_global_constraint(func: str, ctype: str, *args):
        return Constraint(f"{func}({', '.join(str(a) for a in args)})", ctype)

    @staticmethod
    def alldifferent(exprs: List[Expression]) -> "Constraint":
        """Constrain the elements in the passed List to be pairwise different.

        Args:
            variables (List[Expression]): Passed List of expressions

        Returns:
            Constraint: Alldifferent constraint
        """
        return Constraint._from_global_constraint("alldifferent", Constraint.CTYPE_ALLDIFFERENT, exprs)
    
    @staticmethod
    def among(n: int, exprs: List[Expression], values: List[int]):
        return Constraint._from_global_constraint("among", Constraint.CTYPE_AMONG, n, exprs, values)
    
    @staticmethod
    def all_equal(exprs: List[Expression]):
        return Constraint._from_global_constraint("all_equal", Constraint.CTYPE_ALL_EQUAL, exprs)
    
    @staticmethod
    def count(exprs: List[Expression], val: int, count: int):
        return Constraint._from_global_constraint("count", Constraint.CTYPE_COUNT, exprs, val, count)
    
    @staticmethod
    def increasing(exprs: List[Expression]):
        # Requires that the array x is in (non-strictly) increasing order (duplicates are allowed).
        return Constraint._from_global_constraint("increasing", Constraint.CTYPE_INCREASING, exprs)

    @staticmethod
    def decreasing(exprs: List[Expression]):
        # Requires that the array x is in (non-strictly) decreasing order (duplicates are allowed).
        return Constraint._from_global_constraint("decreasing", Constraint.CTYPE_DECREASING, exprs)
    
    @staticmethod
    def disjunctive(s: List[Expression], d: List[Expression]):
        # Requires that a set of tasks given by start times s and durations d do not overlap in time. 
        # Tasks with duration 0 can be scheduled at any time, even in the middle of other tasks.
        return Constraint._from_global_constraint("disjunctive", Constraint.CTYPE_DISJUNCTIVE, s, d)
    
    @staticmethod
    def disjunctive_strict(s: List[Expression], d: List[Expression]):
        # Requires that a set of tasks given by start times s and durations d do not overlap in time. 
        # Tasks with duration 0 CANNOT be scheduled at any time, but only when no other task is running.
        return Constraint._from_global_constraint("disjunctive_strict", Constraint.CTYPE_DISJUNCTIVE, s, d)
    
    @staticmethod
    def arg_sort(x: List[Expression], p: List[Expression]):
        # Constrains p to be the permutation which causes x to be in sorted order hence x[p[i]] <= x[p[i+1]].
        return Constraint._from_global_constraint("arg_sort", Constraint.CTYPE_ARG_SORT, x, p)
    
    @staticmethod
    def diffn(x: List[Expression], y: List[Expression], dx: List[Expression], dy: List[Expression]):
        # Constrains rectangles i, given by their origins (x[i], y[i]) and sizes (dx[i], dy[i]),
        # to be non-overlapping. Zero-width rectangles can still not overlap with any other rectangle.
        return Constraint._from_global_constraint("diffn", Constraint.CTYPE_DIFFN, x, y, dx, dy)
    
    @staticmethod
    def connected(node_from: List[int], node_to: List[int], ns: List[ExpressionBool], es: List[ExpressionBool]):
        # Constrains the subgraph ns and es of a given undirected graph to be connected.
        return Constraint._from_global_constraint("connected", Constraint.CTYPE_CONNECTED, node_from, node_to, ns, es)
    
    @staticmethod
    def reachable(node_from: List[int], node_to: List[int], r: List[Expression], ns: List[ExpressionBool], es: List[ExpressionBool]):
        # Constrains the subgraph ns and es of a given undirected graph to be reachable from r.
        # TODO: this can have other parameters.
        return Constraint._from_global_constraint("reachable", Constraint.CTYPE_REACHABLE, node_from, node_to, r, ns, es)