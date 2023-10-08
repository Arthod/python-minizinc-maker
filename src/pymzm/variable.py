
from .expression import *
from .exceptions import *
from .misc import *

class ValueDict(dict):
    def __iter__(self):
        for v in self.values():
            yield v

    def __str__(self):
        return variableIterable2Str(self)
    
    
    def __invert__(self):
        raise NotImplementedError()
    def __add__(self, other):
        raise NotImplementedError()
    def __sub__(self, other):
        raise NotImplementedError()

    def __eq__(self, other: "Expression") -> "ExpressionBool":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return [s == other for s in self]
    
    def __ne__(self, other: "Expression") -> "ExpressionBool":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return [s != other for s in self]
    
    def __lt__(self, other: "Expression") -> "ExpressionBool":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return [s < other for s in self]
    
    def __le__(self, other: "Expression") -> "ExpressionBool":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return [s <= other for s in self]
    
    def __gt__(self, other: "Expression") -> "ExpressionBool":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return [s > other for s in self]
    
    def __ge__(self, other: "Expression") -> "ExpressionBool":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return [s >= other for s in self]
    
class Variable(Expression):
    VTYPES = [
        VTYPE_INTEGER,
        VTYPE_FLOAT,
        VTYPE_BOOL,
        VTYPE_STRING,
    ] = [
        "int",
        "float",
        "bool",
        "string",
    ]
    def __init__(self, name: str, vtype: int=VTYPE_INTEGER, val_min: int=None, val_max: int=None):
        self.name = name
        self.vtype = vtype
        self.val_min = val_min
        self.val_max = val_max

        if (vtype == Variable.VTYPE_INTEGER or vtype == Variable.VTYPE_FLOAT):
            assert self.val_min is not None
            assert self.val_max is not None

        elif (vtype == Variable.VTYPE_BOOL):
            assert self.val_min is None or self.val_min == 0
            assert self.val_max is None or self.val_max == 1
            self.val_min = 0
            self.val_max = 1
            self.__class__ = VariableBool
        elif (vtype == Variable.VTYPE_STRING):
            raise NotImplementedError()
        else:
            raise Exception(f"Invalid variable type vtype={vtype}")
    
    def __str__(self):
        return self.name

    def _to_mz(self):
        if (self.vtype == Variable.VTYPE_BOOL):
            return f"var bool: {self.name};\n"
        else:
            return f"var {self.val_min}..{self.val_max}: {self.name};\n"
    
class VariableBool(ExpressionBool, Variable):
    pass