from .expression import Expression
from .exceptions import (
    PymzmIndexingScalarValue,
    PymzmInvalidScalarType,
    PymzmNonInitializedConstant,
)
from .variable import Variable
from .data_encoder import encode_scalar, encode_array, infer_shape


class Constant(Expression):
    def __init__(self, name: str, value, vtype=Variable.VTYPE_INTEGER):
        super().__init__(name)
        self.name = name
        self.value = value
        if self.value is None:
            raise PymzmNonInitializedConstant(name)

        self.vtype = vtype
        self.is_enum_type = isinstance(self.vtype, str) and self.vtype not in [
            Variable.VTYPE_INTEGER,
            Variable.VTYPE_BOOL,
            Variable.VTYPE_FLOAT,
            Variable.VTYPE_STRING,
        ]
        if not self.is_enum_type and self.vtype not in [
            Variable.VTYPE_INTEGER,
            Variable.VTYPE_BOOL,
            Variable.VTYPE_FLOAT,
            Variable.VTYPE_STRING,
        ]:
            raise PymzmInvalidScalarType("constant", self.vtype)

        self.shape = self._infer_shape(value)

    @staticmethod
    def _infer_shape(value):
        return infer_shape(value)

    def __getitem__(self, other: Expression):
        if self.shape is None:
            raise PymzmIndexingScalarValue(self.name)

        if len(self.shape) == 1:
            return Expression(f"{self.name}[{str(other)} + 1]")

        else:
            return Expression(f"{self.name}[{', '.join(f'{o} + 1' for o in other)}]")

    def __str__(self):
        return self.name

    def _to_mz(self):
        if self.shape is None:
            return f"{self.vtype}: {self.name} = {self._scalar_to_mz(self.value)};\n"

        else:
            mz_array = encode_array(
                self.value, shape=self.shape, scalar_formatter=self._scalar_to_mz
            )
            return f"array[{','.join(f'1..{d}' for d in self.shape)}] of {self.vtype}: {self.name} = {mz_array};\n"

    def _scalar_to_mz(self, value):
        return encode_scalar(value, vtype=self.vtype, is_enum_type=self.is_enum_type)


class Parameter(Constant):
    def __init__(self, name: str, value=None, vtype=Variable.VTYPE_INTEGER):
        self.has_value = value is not None
        if self.has_value:
            super().__init__(name, value, vtype)
            return

        Expression.__init__(self, name)
        self.name = name
        self.value = None
        self.vtype = vtype
        self.is_enum_type = isinstance(self.vtype, str) and self.vtype not in [
            Variable.VTYPE_INTEGER,
            Variable.VTYPE_BOOL,
            Variable.VTYPE_FLOAT,
            Variable.VTYPE_STRING,
        ]
        if not self.is_enum_type and self.vtype not in [
            Variable.VTYPE_INTEGER,
            Variable.VTYPE_BOOL,
            Variable.VTYPE_FLOAT,
            Variable.VTYPE_STRING,
        ]:
            raise PymzmInvalidScalarType("parameter", self.vtype)
        self.shape = None

    def _to_mz(self):
        if not self.has_value:
            return f"{self.vtype}: {self.name};\n"
        return super()._to_mz()
