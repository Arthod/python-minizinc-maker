
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
        if (self.vtype not in [Variable.VTYPE_INTEGER, Variable.VTYPE_BOOL, Variable.VTYPE_FLOAT, Variable.VTYPE_STRING]):
            raise Exception("Invalid vtype for constant. Supported scalar types are int, bool, float, and string")
        
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
            return f"{self.vtype}: {self.name} = {self._scalar_to_mz(self.value)};\n"
        
        else:
            mz_array = array_py2mz(self.value, self.shape, self._scalar_to_mz)
            return f"array[{','.join(f'1..{d}' for d in self.shape)}] of {self.vtype}: {self.name} = {mz_array};\n"

    def _scalar_to_mz(self, value):
        if (self.vtype == Variable.VTYPE_BOOL):
            return "true" if bool(value) else "false"

        if (self.vtype == Variable.VTYPE_STRING):
            escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'

        return str(value)
        
        