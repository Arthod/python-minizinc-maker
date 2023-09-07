import minizinc

class Variable:
    def __init__(self, name: str, val_min: int, val_max: int):
        self.name = name
        self.val_min = val_min
        self.val_max = val_max

    def __repr__(self):
        return f"var {self.val_min}..{self.val_max}: {self.name};\n"
    
class Constant:
    def __init__(self, name: str):
        self.name = name
    
    def __repr__(self):
        return f"int: {self.name};\n"
    
class Constraint:
    def __init__(self, cstr: str):
        self.cstr = cstr

    def __repr__(self):
        return f"constraint {self.cstr};\n"
    

    
class SDULibModel(minizinc):
    def __init__(self):
        self.model = minizinc.Model()
        self.variables = []
        self.constants = []
        self.constraints = []
        self.solve_method = None

    def set_solve_method(self, method: str):
        self.solve_method = f"solve {method};"

    def add_variable(self, variable: Variable):
        self.variables.append(variable)

    def add_constraint(self, constraint: Constraint):
        self.constraints.append(constraint)

    def add_constant(self, constant: Constant):
        self.constants.append(constant)

    def generate(self):
        model_str = "".join(v for v in self.variables + self.constants + self.constraints)
        self.model.add_string(model_str)
        #return "".join(v for v in self.variables + self.constants + self.constraints)