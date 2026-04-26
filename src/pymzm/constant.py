
from .expression import Expression
from .variable import *
from .misc import *


class Constant(Expression):
    def __init__(self, name: str, value, vtype=Variable.VTYPE_INTEGER):
        super().__init__(name)
        self.name = name
        self.value = value
        if (self.value is None):
            raise Exception("Non-initialized constant is not supported by pymzm.")
        
        self.vtype = vtype
        self.is_enum_type = (
            isinstance(self.vtype, str)
            and self.vtype not in [Variable.VTYPE_INTEGER, Variable.VTYPE_BOOL, Variable.VTYPE_FLOAT, Variable.VTYPE_STRING]
        )
        if (not self.is_enum_type and self.vtype not in [Variable.VTYPE_INTEGER, Variable.VTYPE_BOOL, Variable.VTYPE_FLOAT, Variable.VTYPE_STRING]):
            raise Exception("Invalid vtype for constant. Supported scalar types are int, bool, float, string, and enum type names")
        
        self.shape = self._infer_shape(value)

    @staticmethod
    def _infer_shape(value):
        if (hasattr(value, "shape")):
            shape = tuple(int(d) for d in value.shape)
            return shape if len(shape) > 0 else None

        def _shape_of(v):
            if (isinstance(v, (list, tuple))):
                if (len(v) == 0):
                    return (0,)
                first_shape = _shape_of(v[0])
                return (len(v), *first_shape)
            return ()

        shape = _shape_of(value)
        return shape if len(shape) > 0 else None
        
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
        if (self.is_enum_type):
            if (hasattr(value, "_to_mz_token")):
                return value._to_mz_token()
            if (isinstance(value, str)):
                return value
            return str(value)

        if (self.vtype == Variable.VTYPE_BOOL):
            return "true" if bool(value) else "false"

        if (self.vtype == Variable.VTYPE_STRING):
            escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'

        return str(value)


class Parameter(Constant):
    def __init__(self, name: str, value=None, vtype=Variable.VTYPE_INTEGER):
        self.has_value = value is not None
        if (self.has_value):
            super().__init__(name, value, vtype)
            return

        Expression.__init__(self, name)
        self.name = name
        self.value = None
        self.vtype = vtype
        self.is_enum_type = (
            isinstance(self.vtype, str)
            and self.vtype not in [Variable.VTYPE_INTEGER, Variable.VTYPE_BOOL, Variable.VTYPE_FLOAT, Variable.VTYPE_STRING]
        )
        if (not self.is_enum_type and self.vtype not in [Variable.VTYPE_INTEGER, Variable.VTYPE_BOOL, Variable.VTYPE_FLOAT, Variable.VTYPE_STRING]):
            raise Exception("Invalid vtype for parameter. Supported scalar types are int, bool, float, string, and enum type names")
        self.shape = None

    def _to_mz(self):
        if (not self.has_value):
            return f"{self.vtype}: {self.name};\n"
        return super()._to_mz()
        
        