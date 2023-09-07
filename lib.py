import minizinc
import chess

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
    def __init__(self, cstr: str):
        self.cstr = cstr

    def __repr__(self):
        return f"constraint {self.cstr};\n"
    

    
class SDUMZModel(minizinc.Model):
    def __init__(self):
        self.variables = []
        self.constants = []
        self.constraints = []
        self.solve_criteria = None
        self.solve_method = None

        super().__init__()

    def set_solve_criteria(self, criteria: str):
        self.solve_criteria = criteria

    def set_solve_method(self, method: Method):
        self.solve_method = method

    def add_variable(self, name: str, val_min: int, val_max: int):
        variable = Variable(name, val_min, val_max)
        self.variables.append(variable)
        return variable

    def add_constraint(self, cstr: str):
        constraint = Constraint(cstr)
        self.constraints.append(constraint)
        return constraint

    def add_constant(self, name: str, value: int=None):
        constant = Constant(name, value)
        self.constants.append(constant)
        return constant

    def generate(self, debug=False):
        model_str = "".join(str(v) for v in self.variables + self.constants + self.constraints)
        
        if (self.solve_method is None):
            model_str += f"solve {self.solve_criteria};\n"
        else:
            model_str += f"solve :: {self.solve_method} {self.solve_criteria};\n"
        if (debug):
            print(model_str)
        self.add_string(model_str)
        #return "".join(v for v in self.variables + self.constants + self.constraints)