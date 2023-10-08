
from .variable import *
from .misc import *

import numpy as np

class Constant:
    def __init__(self, name: str, value, vtype=Variable.VTYPE_INTEGER):
        self.name = name
        self.value = value
        if (self.value is None):
            raise Exception("Non-initialized constant is not supported by pymzm.")
        
        self.vtype = vtype        
        if (self.vtype not in [Variable.VTYPE_INTEGER, Variable.VTYPE_BOOL]):
            raise Exception("Invalid vtype for constant. Currently only integer and boolean types are supported")
        
        arr = np.array(value)
        if (arr.shape):
            # Is nd array
            self.shape = arr.shape

        else:
            # is single value
            self.shape = None
        
    def __getitem__(self, other: Expression):
        # TODO boolean expression
        if (self.shape is None):
            raise Exception("Constant cant be indexed as it is a single value")
        
        if (len(self.shape) == 1):
            return Expression(f"{self.name}[{str(other)} + 1]")
        
        else:
            return Expression(f"{self.name}[{', '.join(f'{o} + 1' for o in other)}]")

    def __str__(self):
        return self.name
    
    def _to_mz(self):
        if (self.shape is None):
            return f"{self.vtype}: {self.name} = {self.value};\n"
        
        else:
            mz_array = array_py2mz(self.value, self.shape)
            return f"array[{','.join(f'1..{d}' for d in self.shape)}] of {self.vtype}: {self.name} = {mz_array};\n"
        
        