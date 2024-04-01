
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
        if (not isinstance(other, ValueDict)):
            raise PymzmValueIsNotExpression("other", other)

        v = ValueDict()
        v.update(other)
        v.update(self)
        
        return v
    
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
        VTYPE_SET,
    ] = [
        "int",
        "float",
        "bool",
        "string",
        "set"
    ]
    def __init__(self, name: str, vtype: int=VTYPE_INTEGER, val_min: int=None, val_max: int=None, domain=None):
        self.name = name
        self.vtype = vtype
        self.val_min = val_min
        self.val_max = val_max
        self.domain = domain

        if (vtype == Variable.VTYPE_INTEGER or vtype == Variable.VTYPE_SET):
            if (domain is None):
                assert self.val_min is not None
                assert self.val_max is not None

            else:
                assert self.val_min is None
                assert self.val_max is None
                #assert isinstance(domain, set)
                self.domain = set(domain)
                assert len(self.domain) > 0

        elif (vtype == Variable.VTYPE_FLOAT):
            assert self.domain is None
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
        
        elif (self.vtype == Variable.VTYPE_INTEGER):
            if (self.domain is None):
                return f"var {self.val_min}..{self.val_max}: {self.name};\n"
            else:
                return f"var {self.domain}: {self.name};\n"
            
        elif (self.vtype == Variable.VTYPE_FLOAT):
            return f"var {self.val_min}..{self.val_max}: {self.name};\n"
            
        elif (self.vtype == Variable.VTYPE_SET):
            if (self.domain is None):
                return f"var set of {self.val_min}..{self.val_max}: {self.name};\n"
            else:
                return f"var set of {self.domain}: {self.name};\n"

    def __len__(self):
        assert self.vtype == Variable.VTYPE_SET
        return Expression._func("card", [self])
    
    @staticmethod
    def min(var):
        assert var.vtype == Variable.VTYPE_SET
        return Expression._func("min", [var])
    
    @staticmethod
    def max(var):
        assert var.vtype == Variable.VTYPE_SET
        return Expression._func("max", [var])
    
    def contains(self, content):
        assert self.vtype == Variable.VTYPE_SET
        return ExpressionBool(f"({content} in {self})")
    
    @staticmethod
    def intersection_length(v1, v2):
        assert v1.vtype == Variable.VTYPE_SET
        assert v2.vtype == Variable.VTYPE_SET
        return Expression(f"(card({v1} intersect {v2}))")
    
class VariableBool(ExpressionBool, Variable):
    pass