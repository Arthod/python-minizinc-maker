import minizinc
import chess
import sympy
from collections.abc import Iterable



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
    
    def operator(self, symbol: str, other: "Expression", reverse=False):
        if (isinstance(other, Expression)):
            other = other.name

        if (reverse):
            return Expression(f"{other} {symbol} {self.name}")
        else:
            return Expression(f"{self.name} {symbol} {other}")

    def __add__(self, other: "Expression"): return self.operator("+", other)
    def __radd__(self, other: "Expression"): return self.operator("+", other, reverse=True)
    def __sub__(self, other: "Expression"): return self.operator("-", other)
    def __rsub__(self, other: "Expression"): return self.operator("-", other, reverse=True)
    def __mul__(self, other: "Expression"): return self.operator("*", other)
    def __rmul__(self, other: "Expression"): return self.operator("*", other, reverse=True)
    def __truediv__(self, other: "Expression"): return self.operator("/", other)
    def __rtruediv__(self, other: "Expression"): return self.operator("/", other, reverse=True)
    def __mod__(self, other: "Expression"): return self.operator("mod", other)
    def __rmod__(self, other: "Expression"): return self.operator("mod", other, reverse=True)
    
    def __eq__(self, other: "Expression"):  return self.operator("=", other)
    def __ne__(self, other: "Expression"):  return self.operator("!=", other)
    def __lt__(self, other: "Expression"):  return self.operator("<", other)
    def __le__(self, other: "Expression"):  return self.operator("<=", other)
    def __gt__(self, other: "Expression"):  return self.operator(">", other)
    def __ge__(self, other: "Expression"):  return self.operator(">=", other)

    def func(self, func: str, other: "Expression"=None):
        if (other is None):
            return Expression(f"{func}({self.name})")
        else:
            if (isinstance(other, Expression)):
                return Expression(f"{func}({self.name}, {other.name})")
            else:
                return Expression(f"{func}({self.name}, {other})")

    def __pow__(self, other: "Expression"): return self.func("pow", other)
    def __abs__(self):  return self.func("abs")
    # TODO: https://www.minizinc.org/doc-2.7.6/en/lib-stdlib-builtins.html
    # arg max, arg min
    # max, min
    # count
    # exp(x)
    # log_x, log_2, log_10, ln
    # trinonometric functions
    # ..and more!


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
    def __init__(self, name: str, val_min: int, val_max: int, vtype=VTYPE_INTEGER):
        self.name = name#super().__init__(name)
        self.val_min = val_min
        self.val_max = val_max
        self.vtype = vtype
    
    def __str__(self):
        return self.name

    def _to_mz(self):
        return f"var {self.val_min}..{self.val_max}: {self.name};\n"
    
    def _to_fz(self):
        return f"var {self.val_min}..{self.val_max}: {self.name}:: output_var;\n"
    
    def _to_tz(self):
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
        
    def _to_fz(self):
        raise NotImplementedError()
    
class Constraint:
    CTYPES = [
        CTYPE_NORMAL,
        CTYPE_ALLDIFFERENT,
        CTYPE_AMONG,
        CTYPE_ALL_EQUAL,
        CTYPE_COUNT,
    ] = [
        "normal",
        "alldifferent",
        "among",
        "all_equal",
        "count"
    ]
    def __init__(self, cstr: str, ctype: str=CTYPE_NORMAL):
        self.cstr = cstr
        self.ctype = ctype

    def __str__(self):
        return self.cstr
    
    def _to_mz(self):
        return f"constraint {self.cstr};\n"
    
    def _to_fz(self):
        return f"constraint {self.cstr};\n"

    @staticmethod
    def from_global_constraint(func: str, ctype: str, *args):
        return Constraint(f"{func}({', '.join(str(a) for a in args)})", ctype)

    @staticmethod
    def alldifferent(variables: Iterable[Variable]):
        arr_str = _variableIterable2Str(variables)
        return Constraint.from_global_constraint("alldifferent", Constraint.CTYPE_ALLDIFFERENT, arr_str)
    
    @staticmethod
    def among(n: int, variables: Iterable[Variable], values: list[int]):
        arr_str = _variableIterable2Str(variables)
        return Constraint.from_global_constraint("among", Constraint.CTYPE_AMONG, n, arr_str, values)
    
    @staticmethod
    def all_equal(variables: Iterable[Variable]):
        arr_str = _variableIterable2Str(variables)
        return Constraint.from_global_constraint("all_equal", Constraint.CTYPE_ALL_EQUAL, arr_str)
    
    @staticmethod
    def count(variables: Iterable[Variable], val: int, count: int):
        arr_str = _variableIterable2Str(variables)
        return Constraint.from_global_constraint("count", Constraint.CTYPE_COUNT, arr_str, val, count)
    
    

    
class Model(minizinc.Model):
    def __init__(self):
        self.variables = []
        self.constants = []
        self.constraints = []
        self.solve_criteria = None
        self.solve_method = None

        self.global_constraints = set()

        super().__init__()

    def set_solve_criteria(self, criteria: str):
        self.solve_criteria = criteria

    def set_solve_method(self, method: Method):
        self.solve_method = method

    def add_variable(self, name: str, val_min: int, val_max: int):
        variable = Variable(name, val_min, val_max)
        self.variables.append(variable)
        return variable
    
    def add_variables(self, name: str, indices: list[tuple[int]], val_min: int=None, val_max: int=None, vtype=Variable.VTYPE_INTEGER):
        variables = {}
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
            constraint = Constraint(cstr.name)

        elif (type(cstr) is str):
            constraint = Constraint(cstr)

        self.constraints.append(constraint)
        return constraint

    def add_constant(self, name: str, value: int=None):
        constant = Constant(name, value)
        self.constants.append(constant)
        return constant

    def generate_mzn(self, debug=False):
        self.model_mzn_str = ""
        for gconst in self.global_constraints:
            self.model_mzn_str += f'include \"{gconst}.mzn\";\n'

        self.model_mzn_str += "".join(a._to_mz() for a in self.variables + self.constants + self.constraints)
        
        if (self.solve_method is None):
            self.model_mzn_str += f"solve {self.solve_criteria};\n"
        else:
            self.model_mzn_str += f"solve :: {self.solve_method} {self.solve_criteria};\n"
            
        self.add_string(self.model_mzn_str)
        if (debug):
            print(self.model_mzn_str)

    def write_mzn(self, fn: str):
        if (self.model_mzn_str is None):
            self.generate_mzn()
        with open(fn, "w") as f:
            f.write(self.model_mzn_str)

    def generate_fzn(self, debug=False):
        self.model_fzn_str = ""

        self.model_fzn_str += "".join(a._to_fz() for a in self.variables + self.constants + self.constraints)
        
        # TODO
        if (self.solve_method is None):
            self.model_fzn_str += f"solve {self.solve_criteria};\n"
        else:
            self.model_fzn_str += f"solve :: {self.solve_method} {self.solve_criteria};\n"
            
        self.add_string(self.model_fzn_str)
        if (debug):
            print(self.model_fzn_str)

    def write_fzn(self, fn: str):
        if (self.model_fzn_str is None):
            self.generate_mzn()
        with open(fn, "w") as f:
            f.write(self.model_fzn_str)


def _variableIterable2Str(variables: Iterable[Variable]) -> str:
    if (isinstance(variables, dict)):
        variables = variables.values()
    return str([v.name if isinstance(v, Expression) else v for v in variables]).replace("'", "")

if __name__ == "__main__":
    pass