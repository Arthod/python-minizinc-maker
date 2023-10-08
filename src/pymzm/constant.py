
from .variable import *

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
        
        