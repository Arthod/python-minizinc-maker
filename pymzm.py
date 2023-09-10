import minizinc
import chess
import sympy


class Method:
    def __init__(self, s: str):
        self.s = s

    def __repr__(self):
        return self.s

    @staticmethod
    def int_search(arr: list[str], varchoice: str, constrainchoice: str):
        method = Method(f"int_search({arr}, {varchoice}, {constrainchoice})")
        return method

class Expression:
    def __init__(self, name):
        self.name = name
    
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
    def __init__(self, name: str, val_min: int, val_max: int):
        self.name = name#super().__init__(name)
        self.val_min = val_min
        self.val_max = val_max
    
    def __repr__(self):
        return f"var {self.val_min}..{self.val_max}: {self.name};\n"
    
        

    
class Constant:
    def __init__(self, name: str, value: int=None):
        self.name = name
        self.value = value
    
    def __repr__(self):
        if (self.value is not None):
            return f"int: {self.name} = {self.value};"
        else:
            return f"int: {self.name};\n"
    
class Constraint:
    CTYPE_NORMAL = 0
    CTYPE_ALLDIFFERENT = 1
    def __init__(self, cstr: str, ctype: int=CTYPE_NORMAL):
        self.cstr = cstr
        self.ctype = ctype

    @staticmethod
    def alldifferent(variables: list[Variable]):
        arr_str = str([v.name if type(v) is Variable else v for v in variables ]).replace("'", "")
        cstr = Constraint(f"alldifferent({arr_str})", Constraint.CTYPE_ALLDIFFERENT)
        return cstr

    def __repr__(self):
        return f"constraint {self.cstr};\n"
    

    
class Model(minizinc.Model):
    def __init__(self):
        self.variables = []
        self.constants = []
        self.constraints = []
        self.solve_criteria = None
        self.solve_method = None

        self.gcstr_alldifferent = False

        super().__init__()

    def set_solve_criteria(self, criteria: str):
        self.solve_criteria = criteria

    def set_solve_method(self, method: Method):
        self.solve_method = method

    def add_variable(self, name: str, val_min: int, val_max: int):
        variable = Variable(name, val_min, val_max)
        self.variables.append(variable)
        return variable
    
    def add_variables(self, indices: list[int], name: str, val_min: int, val_max: int):
        variables = []
        for idx in indices:
            variable = Variable(f"{name}_{idx}", val_min, val_max)
            self.variables.append(variable)
            variables.append(variable)

        return variables

    def add_constraint(self, cstr: str):
        if (isinstance(cstr, Constraint)):
            constraint = cstr
            if (constraint.ctype == Constraint.CTYPE_ALLDIFFERENT):
                self.gcstr_alldifferent = True

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

    def generate(self, debug=False):
        self.model_str = ""
        if (self.gcstr_alldifferent):
            self.model_str += f'include \"alldifferent.mzn\";\n'

        self.model_str += "".join(str(v) for v in self.variables + self.constants + self.constraints)
        
        if (self.solve_method is None):
            self.model_str += f"solve {self.solve_criteria};\n"
        else:
            self.model_str += f"solve :: {self.solve_method} {self.solve_criteria};\n"
            
        self.add_string(self.model_str)
        if (debug):
            print(self.model_str)

    def write(self, fn: str):
        with open(fn, "w") as f:
            f.write(self.model_str)