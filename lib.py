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



class Variable:
    def __init__(self, name: str, val_min: int, val_max: int):
        self.name = name
        self.val_min = val_min
        self.val_max = val_max

    def __repr__(self):
        return f"var {self.val_min}..{self.val_max}: {self.name};\n"
    
    def __add__(self, other):
        return sympy.Symbol(self.name) + other
    
    def __sub__(self, other):
        return sympy.Symbol(self.name) - other
    
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
    

    
class SDUMZModel(minizinc.Model):
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
        if (type(cstr) is Constraint):
            constraint = cstr
            if (constraint.ctype == Constraint.CTYPE_ALLDIFFERENT):
                self.gcstr_alldifferent = True

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