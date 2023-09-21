import math
import minizinc
import chess
import sympy
from collections.abc import Iterable

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


class Method:
    def __init__(self, s: str):
        self.s = s

    def __str__(self):
        return self.s

    @staticmethod
    def int_search(arr: list[str], varchoice: str, constrainchoice: str):
        method = Method(f"int_search({arr}, {varchoice}, {constrainchoice})")
        return method

class Expression:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @staticmethod
    def product(exprs: list["Expression"]) -> "Expression":
        return Expression._func("product", [exprs])

    @staticmethod
    def sum(exprs: list["Expression"]) -> "Expression":
        return Expression._func("sum", [exprs])

    @staticmethod
    def min(exprs: list["Expression"]) -> "Expression":
        return Expression._func("min", [exprs])

    @staticmethod
    def max(exprs: list["Expression"]) -> "Expression":
        return Expression._func("max", [exprs])

    @classmethod
    def _operator(cls, symbol: str, exprs, bracket=False):
        exprs = [expr.name if isinstance(expr, Expression) else expr for expr in exprs]
        out = f" {symbol} ".join(str(a) for a in exprs)

        if (bracket or True):
            out = f"({out})"

        return cls(out)

    @classmethod
    def _func(cls, func_symbol: str, exprs):
        exprs = [expr.name if isinstance(expr, Expression) else expr for expr in exprs]
        out = f", ".join(str(a) for a in exprs)
        return cls(f"{func_symbol}({out})")

    @staticmethod
    def OR(arr: Iterable) -> "ExpressionBool":  return ExpressionBool._operator("\/", arr, bracket=True)
    @staticmethod
    def AND(arr: Iterable) -> "ExpressionBool": return ExpressionBool._operator("/\\", arr, bracket=True)
    @staticmethod
    def onlyIf(arr: Iterable) -> "ExpressionBool":  return ExpressionBool._operator("<-", arr, bracket=True)
    @staticmethod
    def implies(arr: Iterable) -> "ExpressionBool": return ExpressionBool._operator("->", arr, bracket=True)
    @staticmethod
    def iff(arr: Iterable) -> "ExpressionBool": return ExpressionBool._operator("<->", arr, bracket=True)
    @staticmethod
    def NOT(expr: "ExpressionBool") -> "ExpressionBool":    return ExpressionBool._func("not", [expr])
    @staticmethod
    def xor(arr: Iterable) -> "ExpressionBool": return ExpressionBool._operator("xor", arr, bracket=True)

    def __add__(self, other: str): return Expression._operator("+", [self, other])
    def __radd__(self, other: str): return Expression._operator("+", [other, self])
    def __sub__(self, other: str): return Expression._operator("-", [self, other])
    def __rsub__(self, other: str): return Expression._operator("-", [other, self])
    def __mul__(self, other: str): return Expression._operator("*", [self, other])
    def __rmul__(self, other: str): return Expression._operator("*", [other, self])
    def __truediv__(self, other: str): return Expression._operator("/", [self, other])
    def __rtruediv__(self, other: str): return Expression._operator("/", [other, self])
    def __floordiv__(self, other: str): return Expression._operator("div", [self, other])
    def __rfloordiv__(self, other: str): return Expression._operator("div", [other, self])
    def __mod__(self, other: str): return Expression._operator("mod", [self, other])
    def __rmod__(self, other: str): return Expression._operator("mod", [other, self])
    def __neg__(self): return 0 - self#Expression._func("-", [self])
    #def __pos__(self): return Expression._func("+", [self]) TODO: not allowed in minizinc example: +x == v
    
    def __eq__(self, other: str): return ExpressionBool._operator("==", [self, other], bracket=True)
    def __ne__(self, other: str): return ExpressionBool._operator("!=", [self, other], bracket=True)
    def __lt__(self, other: str): return ExpressionBool._operator("<", [self, other], bracket=True)
    def __le__(self, other: str): return ExpressionBool._operator("<=", [self, other], bracket=True)
    def __gt__(self, other: str): return ExpressionBool._operator(">", [self, other], bracket=True)
    def __ge__(self, other: str): return ExpressionBool._operator(">=", [self, other], bracket=True)
    
    def __and__(self, other): return Expression.AND([self, other])
    def __rand__(self, other): return Expression.AND([other, self])
    def __or__(self, other): return Expression.OR([self, other])
    def __ror__(self, other): return Expression.OR([other, self])
    def __xor__(self, other): return Expression.xor([self, other])
    def __rxor__(self, other): return Expression.xor([other, self])
    def __invert__(self): return Expression.NOT(self)

    def __pow__(self, other: str): return Expression._func("pow", [self, other])
    def __rpow__(self, other: str): return Expression._func("pow", [other, self])
    def __abs__(self):  return Expression._func("abs", [self])
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
        "integer",
        "float",
        "bool",
        "string",
    ]
    def __init__(self, name: str, val_min: int=None, val_max: int=None, vtype=VTYPE_INTEGER):
        self.name = name
        self.vtype = vtype

        if (vtype == Variable.VTYPE_INTEGER or vtype == Variable.VTYPE_FLOAT):
            assert val_min is not None
            assert val_max is not None
            self.val_min = val_min
            self.val_max = val_max

        elif (vtype == Variable.VTYPE_BOOL):
            self.val_min = 0
            self.val_max = 1
            self.__class__ = VariableBool
    
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
    def __init__(self, name: str, value: int=None):
        self.name = name
        self.value = value
    
    def __str__(self):
        return self.name

    def _to_mz(self):
        if (self.value is not None):
            return f"int: {self.name} = {self.value};\n"
        else:
            return f"int: {self.name};\n"
    
class Constraint:
    CTYPES = [
        CTYPE_NORMAL,
        CTYPE_ALLDIFFERENT,
        CTYPE_AMONG,
        CTYPE_ALL_EQUAL,
        CTYPE_COUNT,
        CTYPE_INCREASING,
        CTYPE_DECREASING
    ] = [
        "normal",
        "alldifferent",
        "among",
        "all_equal",
        "count",
        "increasing",
        "decreasing"
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
    def alldifferent(exprs: Iterable[Expression]) -> "Constraint":
        """Constrain the elements in the passed Iterable to be pairwise different.

        Args:
            variables (Iterable[Expression]): Passed Iterable of expressions

        Returns:
            Constraint: Alldifferent constraint
        """
        return Constraint.from_global_constraint("alldifferent", Constraint.CTYPE_ALLDIFFERENT, exprs)
    
    @staticmethod
    def among(n: int, exprs: Iterable[Expression], values: list[int]):
        return Constraint.from_global_constraint("among", Constraint.CTYPE_AMONG, n, exprs, values)
    
    @staticmethod
    def all_equal(exprs: Iterable[Expression]):
        return Constraint.from_global_constraint("all_equal", Constraint.CTYPE_ALL_EQUAL, exprs)
    
    @staticmethod
    def count(exprs: Iterable[Expression], val: int, count: int):
        return Constraint.from_global_constraint("count", Constraint.CTYPE_COUNT, exprs, val, count)
    
    @staticmethod
    def increasing(exprs: Iterable[Expression]):
        # Requires that the array x is in increasing order (duplicates are allowed).
        return Constraint.from_global_constraint("increasing", Constraint.CTYPE_INCREASING, exprs)

    @staticmethod
    def decreasing(exprs: Iterable[Expression]):
        # Requires that the array x is in decreasing order (duplicates are allowed).
        return Constraint.from_global_constraint("decreasing", Constraint.CTYPE_DECREASING, exprs)

    
class Model(minizinc.Model):
    def __init__(self):
        self.variables = []
        self.constants = []
        self.constraints = []
        self.solve_criteria = None
        self.solve_expression = None
        self.solve_method = None

        self.global_constraints = set()

        super().__init__()

    def set_solve_criteria(self, criteria: str, expr: Expression=None):
        self.solve_criteria = criteria
        self.solve_expression = expr

        if (criteria == SOLVE_MAXIMIZE or criteria == SOLVE_MINIMIZE):
            assert expr is not None
        else:
            assert expr is None

    def set_solve_method(self, method: Method):
        self.solve_method = method

    def add_variable(self, name: str, val_min: int, val_max: int):
        variable = Variable(name, val_min, val_max)
        self.variables.append(variable)
        return variable
    
    def add_variables(self, name: str, indices: list[tuple[int]], val_min: int=None, val_max: int=None, vtype=Variable.VTYPE_INTEGER) -> ValueDict:
        variables = ValueDict()
        for idx in indices:
            idx_str = str(idx).replace(", ", "_").replace("(", "").replace(")", "")
            variable = Variable(f"{name}_{idx_str}", val_min, val_max, vtype)
            self.variables.append(variable)
            variables[idx] = variable

        return variables

    def add_constraint(self, cstr: str):
        if (isinstance(cstr, Constraint)):
            constraint = cstr
            if (constraint.ctype != Constraint.CTYPE_NORMAL):
                self.global_constraints.add(constraint.ctype)

        elif (isinstance(cstr, Expression)):
            assert isinstance(cstr, ExpressionBool)
            constraint = Constraint(cstr.name)

        elif (type(cstr) is str):
            constraint = Constraint(cstr)

        self.constraints.append(constraint)
        return constraint

    def add_constant(self, name: str, value: int=None):
        constant = Constant(name, value)
        self.constants.append(constant)
        return constant

    def generate(self, debug=False):
        self.model_mzn_str = ""
        for gconst in self.global_constraints:
            self.model_mzn_str += f'include \"{gconst}.mzn\";\n'

        self.model_mzn_str += "".join(a._to_mz() for a in self.variables + self.constants + self.constraints)
        
        assert self.solve_criteria is not None
        if (self.solve_method is None):
            if (self.solve_expression is None):
                self.model_mzn_str += f"solve {self.solve_criteria};\n"
            else:
                self.model_mzn_str += f"solve {self.solve_criteria} {self.solve_expression};\n"
        else:
            self.model_mzn_str += f"solve :: {self.solve_method} {self.solve_criteria};\n"
            
        self.add_string(self.model_mzn_str)
        if (debug):
            print(self.model_mzn_str)

    def write(self, fn: str):
        if (self.model_mzn_str is None):
            self.generate()
        with open(fn, "w") as f:
            f.write(self.model_mzn_str)

def _variableIterable2Str(variables: Iterable[Variable]) -> str:
    return str([v.name if isinstance(v, Expression) else v for v in variables]).replace("'", "")

if __name__ == "__main__":
    pass