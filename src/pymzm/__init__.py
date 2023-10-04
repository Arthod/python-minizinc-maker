import math
import minizinc
import sympy
from collections.abc import Iterable
import types
from typing import Generator, Iterator, List, Tuple

SOLVE_MAXIMIZE = "maximize"
SOLVE_MINIMIZE = "minimize"
SOLVE_SATISFY = "satisfy"

class ValueDict(dict):
    def __iter__(self):
        for v in self.values():
            yield v

    def __str__(self):
        return _variableIterable2Str(self)
    
    def __invert__(self):
        raise NotImplementedError()
    def __add__(self, other):
        raise NotImplementedError()
    def __sub__(self, other):
        raise NotImplementedError()

    def __eq__(self, other: "Expression") -> "ExpressionBool":
        assert isinstance(other, (int, float, Expression))
        return [s == other for s in self]
    
    def __ne__(self, other: "Expression") -> "ExpressionBool":
        assert isinstance(other, (int, float, Expression))
        return [s != other for s in self]
    
    def __lt__(self, other: "Expression") -> "ExpressionBool":
        assert isinstance(other, (int, float, Expression))
        return [s < other for s in self]
    
    def __le__(self, other: "Expression") -> "ExpressionBool":
        assert isinstance(other, (int, float, Expression))
        return [s <= other for s in self]
    
    def __gt__(self, other: "Expression") -> "ExpressionBool":
        assert isinstance(other, (int, float, Expression))
        return [s > other for s in self]
    
    def __ge__(self, other: "Expression") -> "ExpressionBool":
        assert isinstance(other, (int, float, Expression))
        return [s >= other for s in self]

class Method:
    def __init__(self, s: str):
        self.s = s

    def __str__(self):
        return self.s

    @staticmethod
    def int_search(arr: List[str], varchoice: str, constrainchoice: str):
        method = Method(f"int_search({arr}, {varchoice}, {constrainchoice})")
        return method

class Expression:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __bool__(self):
        return False

    @staticmethod
    def ifthenelse(condition: "ExpressionBool", expr1: "Expression", expr2: "Expression") -> "Expression":
        """ifelse: if (condition) then expr1 else expr2:

        Args:
            condition (Expression): condition of expression
            expr1 (Expression): expression if condition
            expr2 (Expression): expression else

        Returns:
            Expression: the main if then else expression 
        """
        if (not isinstance(condition, (ExpressionBool, bool))):
            raise PymzmValueIsNotCondition("condition", condition)
        
        if (not isinstance(expr1, (Expression, int, float))):
            raise PymzmValueIsNotExpression("expr1", expr1)
        
        if (not isinstance(expr2, (Expression, int, float))):
            raise PymzmValueIsNotExpression("expr2", expr2)
        
        return Expression(f"(if {condition} then {expr1} else {expr2} endif)")

    @staticmethod
    def sum(exprs: List["Expression"]) -> "Expression":
        if (not isinstance(exprs, Iterable)):
            raise PymzmValueIsNotExpression("exprs", exprs)
        
        exprs = list(exprs)
        if (not len(exprs)):
            raise PymzmNoValues("exprs")

        for expr in exprs:
            if (not isinstance(expr, (Expression, int, float))):
                raise PymzmValueIsNotExpression("exprs", exprs)

        assert all(isinstance(expr, (Expression, int, float)) for expr in exprs)
        return Expression._func("sum", [exprs])
    
    @staticmethod
    def product(exprs) -> "Expression":
        if (not isinstance(exprs, Iterable)):
            raise PymzmValueIsNotExpression("exprs", exprs)
        
        exprs = list(exprs)
        if (not len(exprs)):
            raise PymzmNoValues("exprs")

        for expr in exprs:
            if (not isinstance(expr, (Expression, int, float))):
                raise PymzmValueIsNotExpression("exprs", exprs)

        assert all(isinstance(expr, (Expression, int, float)) for expr in exprs)
        return Expression._func("product", [exprs])

    @staticmethod
    def min(exprs: List["Expression"]) -> "Expression":
        if (not isinstance(exprs, Iterable)):
            raise PymzmValueIsNotExpression("exprs", exprs)
        
        exprs = list(exprs)
        if (not len(exprs)):
            raise PymzmNoValues("exprs")

        for expr in exprs:
            if (not isinstance(expr, (Expression, int, float))):
                raise PymzmValueIsNotExpression("exprs", exprs)

        assert all(isinstance(expr, (Expression, int, float)) for expr in exprs)
        return Expression._func("min", [exprs])

    @staticmethod
    def max(exprs: List["Expression"]) -> "Expression":
        if (not isinstance(exprs, Iterable)):
            raise PymzmValueIsNotExpression("exprs", exprs)
        
        exprs = list(exprs)
        if (not len(exprs)):
            raise PymzmNoValues("exprs")

        for expr in exprs:
            if (not isinstance(expr, (Expression, int, float))):
                raise PymzmValueIsNotExpression("exprs", exprs)

        assert all(isinstance(expr, (Expression, int, float)) for expr in exprs)
        return Expression._func("max", [exprs])

    @classmethod
    def _operator(cls, symbol: str, exprs):
        exprs = [expr.name if isinstance(expr, Expression) else expr for expr in exprs]
        out = f" {symbol} ".join(str(a) for a in exprs)
        out = f"({out})"

        return cls(out)

    @classmethod
    def _func(cls, func_symbol: str, exprs):
        exprs2 = []
        for expr in exprs:
            if (isinstance(expr, Expression)):
                exprs2.append(expr.name)
            else:
                exprs2.append(expr)
        out = f", ".join(str(a) for a in exprs2)
        return cls(f"{func_symbol}({out})")

    @staticmethod
    def OR(exprs: List["ExpressionBool"]) -> "ExpressionBool":
        assert all(isinstance(expr, ExpressionBool) for expr in exprs)
        return ExpressionBool._operator("\/", exprs)
    
    @staticmethod
    def AND(exprs: List["ExpressionBool"]) -> "ExpressionBool":
        assert all(isinstance(expr, ExpressionBool) for expr in exprs)
        return ExpressionBool._operator("/\\", exprs)
    
    @staticmethod
    def onlyIf(exprs: List["ExpressionBool"]) -> "ExpressionBool":
        assert all(isinstance(expr, ExpressionBool) for expr in exprs)
        return ExpressionBool._operator("<-", exprs)
    
    @staticmethod
    def implies(exprs: List["ExpressionBool"]) -> "ExpressionBool":
        assert all(isinstance(expr, ExpressionBool) for expr in exprs)
        return ExpressionBool._operator("->", exprs)
    
    @staticmethod
    def iff(exprs: List["ExpressionBool"]) -> "ExpressionBool":
        # <->
        assert all(isinstance(expr, ExpressionBool) for expr in exprs)
        return ExpressionBool._operator("<->", exprs)
    
    @staticmethod
    def xor(exprs: List["ExpressionBool"]) -> "ExpressionBool":
        assert all(isinstance(expr, ExpressionBool) for expr in exprs)
        return ExpressionBool._operator("xor", exprs)
    
    @staticmethod
    def NOT(expr: "ExpressionBool") -> "ExpressionBool":
        assert isinstance(expr, ExpressionBool)
        return ExpressionBool._func("not", [expr])

    def __add__(self, other: "Expression") -> "Expression":
        assert isinstance(other, (int, float, Expression))
        return Expression._operator("+", [self, other])
    
    def __radd__(self, other: "Expression") -> "Expression":
        assert isinstance(other, (int, float, Expression))
        return Expression._operator("+", [other, self])
    
    def __sub__(self, other: "Expression") -> "Expression":
        assert isinstance(other, (int, float, Expression))
        return Expression._operator("-", [self, other])
    
    def __rsub__(self, other: "Expression") -> "Expression":
        assert isinstance(other, (int, float, Expression))
        return Expression._operator("-", [other, self])
    
    def __mul__(self, other: "Expression") -> "Expression":
        assert isinstance(other, (int, float, Expression))
        return Expression._operator("*", [self, other])
    
    def __rmul__(self, other: "Expression") -> "Expression":
        assert isinstance(other, (int, float, Expression))
        return Expression._operator("*", [other, self])
    
    def __truediv__(self, other: "Expression") -> "Expression":
        assert isinstance(other, (int, float, Expression))
        return Expression._operator("/", [self, other])
    
    def __rtruediv__(self, other: "Expression") -> "Expression":
        assert isinstance(other, (int, float, Expression))
        return Expression._operator("/", [other, self])
    
    def __floordiv__(self, other: "Expression") -> "Expression":
        assert isinstance(other, (int, float, Expression))
        return Expression._operator("div", [self, other])
    
    def __rfloordiv__(self, other: "Expression") -> "Expression":
        assert isinstance(other, (int, float, Expression))
        return Expression._operator("div", [other, self])
    
    def __mod__(self, other: "Expression") -> "Expression":
        assert isinstance(other, (int, Expression))
        return Expression._operator("mod", [self, other])
    
    def __rmod__(self, other: "Expression") -> "Expression":
        assert isinstance(other, (int, Expression))
        return Expression._operator("mod", [other, self])
    
    def __neg__(self) -> "Expression":
        return 0 - self
    #def __pos__(self): return Expression._func("+", [self]) TODO: not allowed in minizinc example: +x == v
    
    def __eq__(self, other: "Expression") -> "ExpressionBool":
        assert isinstance(other, (int, float, Expression))
        return ExpressionBool._operator("==", [self, other])
    
    def __ne__(self, other: "Expression") -> "ExpressionBool":
        assert isinstance(other, (int, float, Expression))
        return ExpressionBool._operator("!=", [self, other])
    
    def __lt__(self, other: "Expression") -> "ExpressionBool":
        assert isinstance(other, (int, float, Expression))
        return ExpressionBool._operator("<", [self, other])
    
    def __le__(self, other: "Expression") -> "ExpressionBool":
        assert isinstance(other, (int, float, Expression))
        return ExpressionBool._operator("<=", [self, other])
    
    def __gt__(self, other: "Expression") -> "ExpressionBool":
        assert isinstance(other, (int, float, Expression))
        return ExpressionBool._operator(">", [self, other])
    
    def __ge__(self, other: "Expression") -> "ExpressionBool":
        assert isinstance(other, (int, float, Expression))
        return ExpressionBool._operator(">=", [self, other])
    
    
    def __and__(self, other: "ExpressionBool") -> "ExpressionBool":
        assert isinstance(other, (bool, Expression))
        return Expression.AND([self, other])
    
    def __rand__(self, other: "ExpressionBool") -> "ExpressionBool":
        assert isinstance(other, (bool, Expression))
        return Expression.AND([other, self])
    
    def __or__(self, other: "ExpressionBool") -> "ExpressionBool":
        assert isinstance(other, (bool, Expression))
        return Expression.OR([self, other])
    
    def __ror__(self, other: "ExpressionBool") -> "ExpressionBool":
        assert isinstance(other, (bool, Expression))
        return Expression.OR([other, self])
    
    def __xor__(self, other: "ExpressionBool") -> "ExpressionBool":
        assert isinstance(other, (bool, Expression))
        return Expression.xor([self, other])
    
    def __rxor__(self, other: "ExpressionBool") -> "ExpressionBool":
        assert isinstance(other, (bool, Expression))
        return Expression.xor([other, self])
    
    def __invert__(self) -> "ExpressionBool":
        return Expression.NOT(self)

    def __pow__(self, other: "Expression") -> "Expression":
        assert isinstance(other, (int, float, Expression))
        return Expression._func("pow", [self, other])
    
    def __rpow__(self, other: "Expression") -> "Expression":
        assert isinstance(other, (int, float, Expression))
        return Expression._func("pow", [other, self])
    
    def __abs__(self) -> "Expression":
        return Expression._func("abs", [self])
    # TODO: https://www.minizinc.org/doc-2.7.6/en/lib-stdlib-builtins.html
    # arg max, arg min
    # max, min
    # count
    # exp(x)
    # log_x, log_2, log_10, ln
    # trinonometric functions
    # ..and more!

class ExpressionBool(Expression):
    pass

    

class Variable(Expression):
    VTYPES = [
        VTYPE_INTEGER,
        VTYPE_FLOAT,
        VTYPE_BOOL,
        VTYPE_STRING,
    ] = [
        "int",
        "float",
        "bool",
        "string",
    ]
    def __init__(self, name: str, vtype: int=VTYPE_INTEGER, val_min: int=None, val_max: int=None):
        self.name = name
        self.vtype = vtype
        self.val_min = val_min
        self.val_max = val_max

        if (vtype == Variable.VTYPE_INTEGER or vtype == Variable.VTYPE_FLOAT):
            assert self.val_min is not None
            assert self.val_max is not None

        elif (vtype == Variable.VTYPE_BOOL):
            assert self.val_min is None or self.val_min == 0
            assert self.val_max is None or self.val_max == 1
            self.val_min = 0
            self.val_max = 1
            self.__class__ = VariableBool
        elif (vtype == Variable.VTYPE_STRING):
            raise NotImplementedError()
        else:
            raise Exception(f"Invalid variable type vtype={vtype}")
    
    def __str__(self):
        return self.name

    def _to_mz(self):
        if (self.vtype == Variable.VTYPE_BOOL):
            return f"var bool: {self.name};\n"
        else:
            return f"var {self.val_min}..{self.val_max}: {self.name};\n"
    
class VariableBool(ExpressionBool, Variable):
    pass
    
class Constant:
    def __init__(self, name: str, value, vtype=Variable.VTYPE_INTEGER):
        self.name = name
        self.value = value
        self.vtype = vtype
        
        if (self.value is None):
            raise Exception("Non-initialized constant is not supported by pymzm.")
        
    def __getitem__(self, other: Expression):
        # TODO boolean expression
        return Expression(f"{self.name}[{str(other)} + 1]")

    def __str__(self):
        return self.name
    
    def _to_mz(self):
        if (isinstance(self.value, list)):
            return f"array[1..{len(self.value)}] of {self.vtype}: {self.name} = {self.value};\n"

        elif (isinstance(self.value, int)):
            return f"{self.vtype}: {self.name} = {self.value};\n"

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
    ]
    def __init__(self, cstr: str, ctype: str=CTYPE_NORMAL):
        self.cstr = cstr
        self.ctype = ctype

    def __str__(self):
        return self.cstr
    
    def _to_mz(self):
        return f"constraint {self.cstr};\n"

    @staticmethod
    def from_global_constraint(func: str, ctype: str, *args):
        return Constraint(f"{func}({', '.join(str(a) for a in args)})", ctype)

    @staticmethod
    def alldifferent(exprs: List[Expression]) -> "Constraint":
        """Constrain the elements in the passed List to be pairwise different.

        Args:
            variables (List[Expression]): Passed List of expressions

        Returns:
            Constraint: Alldifferent constraint
        """
        return Constraint.from_global_constraint("alldifferent", Constraint.CTYPE_ALLDIFFERENT, exprs)
    
    @staticmethod
    def among(n: int, exprs: List[Expression], values: List[int]):
        return Constraint.from_global_constraint("among", Constraint.CTYPE_AMONG, n, exprs, values)
    
    @staticmethod
    def all_equal(exprs: List[Expression]):
        return Constraint.from_global_constraint("all_equal", Constraint.CTYPE_ALL_EQUAL, exprs)
    
    @staticmethod
    def count(exprs: List[Expression], val: int, count: int):
        return Constraint.from_global_constraint("count", Constraint.CTYPE_COUNT, exprs, val, count)
    
    @staticmethod
    def increasing(exprs: List[Expression]):
        # Requires that the array x is in (non-strictly) increasing order (duplicates are allowed).
        return Constraint.from_global_constraint("increasing", Constraint.CTYPE_INCREASING, exprs)

    @staticmethod
    def decreasing(exprs: List[Expression]):
        # Requires that the array x is in (non-strictly) decreasing order (duplicates are allowed).
        return Constraint.from_global_constraint("decreasing", Constraint.CTYPE_DECREASING, exprs)
    
    @staticmethod
    def disjunctive(s: List[Expression], d: List[Expression]):
        # Requires that a set of tasks given by start times s and durations d do not overlap in time. 
        # Tasks with duration 0 can be scheduled at any time, even in the middle of other tasks.
        return Constraint.from_global_constraint("disjunctive", Constraint.CTYPE_DISJUNCTIVE, s, d)
    
    @staticmethod
    def disjunctive_strict(s: List[Expression], d: List[Expression]):
        # Requires that a set of tasks given by start times s and durations d do not overlap in time. 
        # Tasks with duration 0 CANNOT be scheduled at any time, but only when no other task is running.
        return Constraint.from_global_constraint("disjunctive_strict", Constraint.CTYPE_DISJUNCTIVE, s, d)
    
    @staticmethod
    def arg_sort(x: List[Expression], p: List[Expression]):
        # Constrains p to be the permutation which causes x to be in sorted order hence x[p[i]] <= x[p[i+1]].
        return Constraint.from_global_constraint("arg_sort", Constraint.CTYPE_ARG_SORT, x, p)

    
class Model(minizinc.Model):
    def __init__(self):
        self.constants = []
        self.variables = []
        self.constraints = []
        self.solve_criteria = None
        self.solve_expression = None
        self.solve_method = None
        self.model_mzn_str = None

        self.global_constraints = set()

        super().__init__()

    def set_solve_criteria(self, criteria: str, expr: Expression=None):
        self.solve_criteria = criteria
        self.solve_expression = expr

        if (criteria == SOLVE_MAXIMIZE or criteria == SOLVE_MINIMIZE):
            assert expr is not None
        elif (criteria == SOLVE_SATISFY):
            assert expr is None
        else:
            raise Exception(f"Invalid solve criteria: {criteria}")

    def set_solve_method(self, method: Method):
        self.solve_method = method

    def add_constant(self, name: str, value, vtype=Variable.VTYPE_INTEGER):
        constant = Constant(name, value)
        self.constants.append(constant)
        return constant

    def add_variable(self, name: str, vtype: int=Variable.VTYPE_INTEGER, val_min: int=None, val_max: int=None):
        variable = Variable(name, vtype, val_min, val_max)
        self.variables.append(variable)
        return variable
    
    def add_variables(self, name: str, indices: List[Tuple[int]], vtype: int=Variable.VTYPE_INTEGER, val_min: int=None, val_max: int=None) -> ValueDict:
        variables = ValueDict()
        for idx in indices:
            idx_str = str(idx).replace(", ", "_").replace("(", "").replace(")", "")
            variable = Variable(f"{name}_{idx_str}", vtype, val_min, val_max)
            self.variables.append(variable)
            variables[idx] = variable

        return variables

    def add_constraint(self, constraint: ExpressionBool):
        if (isinstance(constraint, Constraint)):
            if (constraint.ctype != Constraint.CTYPE_NORMAL):
                self.global_constraints.add(constraint.ctype)

        elif (isinstance(constraint, ExpressionBool)):
            constraint = Constraint(constraint.name)

        else:
            raise Exception("invalid constraint type")

        self.constraints.append(constraint)
        return constraint

    def add_constraints(self, constraints: List[Constraint]):
        constraints = list(constraints)
        assert all(isinstance(constraint, (Constraint, Expression, str, bool)) for constraint in constraints)
        for constraint in constraints:
            self.add_constraint(constraint)

    def generate(self, debug=False):
        self.model_mzn_str = ""
        for gconst in self.global_constraints:
            self.model_mzn_str += f'include \"{gconst}.mzn\";\n'

        self.model_mzn_str += "".join(a._to_mz() for a in self.constants + self.variables + self.constraints)
        
        assert self.solve_criteria is not None
        # TODO clean this up as to not be spaghetti code.
        if (self.solve_method is None):
            if (self.solve_expression is None):
                self.model_mzn_str += f"solve {self.solve_criteria};\n"
            else:
                self.model_mzn_str += f"solve {self.solve_criteria} {self.solve_expression};\n"
        else:
            if (self.solve_expression is None):
                self.model_mzn_str += f"solve :: {self.solve_method} {self.solve_criteria};\n"
            else:
                self.model_mzn_str += f"solve :: {self.solve_method} {self.solve_criteria} {self.solve_expression};\n"
            
        self.add_string(self.model_mzn_str)
        if (debug):
            print(self.model_mzn_str)

    def write(self, fn: str):
        if (self.model_mzn_str is None):
            self.generate()
        with open(fn, "w") as f:
            f.write(self.model_mzn_str)

def _variableIterable2Str(variables: List[Variable]) -> str:
    return str([v.name if isinstance(v, Expression) else v for v in variables]).replace("'", "")


class PymzmException(Exception):
    pass

class PymzmValueIsNotCondition(PymzmException):
    def __init__(self, argname, expr):
        self.argname = argname
        self.expr = expr

    def __str__(self):
        return f"Argument \"{self.argname}\": {repr(self.expr)} (type={type(self.expr)}) is not valid as a condition."

class PymzmValueIsNotExpression(PymzmException):
    def __init__(self, argname, expr):
        self.argname = argname
        self.expr = expr

    def __str__(self):
        return f"Argument \"{self.argname}\": {repr(self.expr)} (type={type(self.expr)}) is not valid as a expression."

class PymzmNoValues(PymzmException):
    def __init__(self, argname):
        self.argname = argname

    def __str__(self):
        return f"Argument \"{self.argname}, expected iterable but has no values.\""

if __name__ == "__main__":
    pass