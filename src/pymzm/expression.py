
from typing import List
from collections.abc import Iterable

from .exceptions import *

class Expression:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name

    def __bool__(self):
        return False

    @staticmethod
    def ifthenelse(condition: "ExpressionBool", expr1: "Expression", expr2: "Expression") -> "Expression":
        """ifelse: if (condition) then expr1 else expr2:

        Args:
            condition (Expression): condition of expression
            expr1 (Expression): expression if condition
            expr2 (Expression): expression else

        Returns:
            Expression: the main if then else expression 
        """
        if (not isinstance(condition, (ExpressionBool, bool))):
            raise PymzmValueIsNotCondition("condition", condition)
        
        if (not isinstance(expr1, (Expression, int, float))):
            raise PymzmValueIsNotExpression("expr1", expr1)
        
        if (not isinstance(expr2, (Expression, int, float))):
            raise PymzmValueIsNotExpression("expr2", expr2)
        
        return Expression(f"(if {condition} then {expr1} else {expr2} endif)")

    @staticmethod
    def sum(exprs: List["Expression"]) -> "Expression":
        if (not isinstance(exprs, Iterable)):
            raise PymzmValueIsNotExpression("exprs", exprs)
        
        #exprs = list(exprs)
        if (not len(exprs)):
            return Expression("0")
            raise PymzmNoValues("exprs")

        for expr in exprs:
            if (not isinstance(expr, (Expression, int, float))):
                raise PymzmValueIsNotExpression("exprs", exprs)
            
        return Expression._func("sum", [exprs])
    
    @staticmethod
    def product(exprs) -> "Expression":
        if (not isinstance(exprs, Iterable)):
            raise PymzmValueIsNotExpression("exprs", exprs)
        
        exprs = list(exprs)
        if (not len(exprs)):
            raise PymzmNoValues("exprs")

        for expr in exprs:
            if (not isinstance(expr, (Expression, int, float))):
                raise PymzmValueIsNotExpression("exprs", exprs)
            
        return Expression._func("product", [exprs])

    @staticmethod
    def min(exprs: List["Expression"]) -> "Expression":
        if (not isinstance(exprs, Iterable)):
            raise PymzmValueIsNotExpression("exprs", exprs)
        
        exprs = list(exprs)
        if (not len(exprs)):
            raise PymzmNoValues("exprs")

        for expr in exprs:
            if (not isinstance(expr, (Expression, int, float))):
                raise PymzmValueIsNotExpression("exprs", exprs)
            
        return Expression._func("min", [exprs])

    @staticmethod
    def max(exprs: List["Expression"]) -> "Expression":
        if (not isinstance(exprs, Iterable)):
            raise PymzmValueIsNotExpression("exprs", exprs)
        
        exprs = list(exprs)
        if (not len(exprs)):
            raise PymzmNoValues("exprs")

        for expr in exprs:
            if (not isinstance(expr, (Expression, int, float))):
                raise PymzmValueIsNotExpression("exprs", exprs)
            
        return Expression._func("max", [exprs])

    @classmethod
    def _operator(cls, symbol: str, exprs):
        exprs = [expr.name if isinstance(expr, Expression) else expr for expr in exprs]
        out = f" {symbol} ".join(str(a) for a in exprs)
        out = f"({out})"

        return cls(out)

    @classmethod
    def _func(cls, func_symbol: str, exprs):
        exprs2 = []
        for expr in exprs:
            if (isinstance(expr, Expression)):
                exprs2.append(expr.name)
            else:
                exprs2.append(expr)
        out = f", ".join(str(a) for a in exprs2)
        return cls(f"{func_symbol}({out})")

    @staticmethod
    def OR(exprs: List["ExpressionBool"]) -> "ExpressionBool":
        for expr in exprs:
            if (not isinstance(expr, ExpressionBool)):
                raise PymzmValueIsNotCondition("exprs", expr)

        return ExpressionBool._operator("\/", exprs)
    
    @staticmethod
    def AND(exprs: List["ExpressionBool"]) -> "ExpressionBool":
        for expr in exprs:
            if (not isinstance(expr, ExpressionBool)):
                raise PymzmValueIsNotCondition("exprs", expr)

        return ExpressionBool._operator("/\\", exprs)
    
    @staticmethod
    def onlyIf(exprs: List["ExpressionBool"]) -> "ExpressionBool":
        for expr in exprs:
            if (not isinstance(expr, ExpressionBool)):
                raise PymzmValueIsNotCondition("exprs", expr)

        return ExpressionBool._operator("<-", exprs)
    
    @staticmethod
    def implies(exprs: List["ExpressionBool"]) -> "ExpressionBool":
        for expr in exprs:
            if (not isinstance(expr, ExpressionBool)):
                raise PymzmValueIsNotCondition("exprs", expr)

        return ExpressionBool._operator("->", exprs)
    
    @staticmethod
    def iff(exprs: List["ExpressionBool"]) -> "ExpressionBool":
        # <->
        for expr in exprs:
            if (not isinstance(expr, ExpressionBool)):
                raise PymzmValueIsNotCondition("exprs", expr)

        return ExpressionBool._operator("<->", exprs)
    
    @staticmethod
    def xor(exprs: List["ExpressionBool"]) -> "ExpressionBool":
        for expr in exprs:
            if (not isinstance(expr, ExpressionBool)):
                raise PymzmValueIsNotCondition("exprs", expr)

        return ExpressionBool._operator("xor", exprs)
    
    @staticmethod
    def NOT(expr: "ExpressionBool") -> "ExpressionBool":
        if (not isinstance(expr, ExpressionBool)):
            raise PymzmValueIsNotCondition("exprs", expr)

        return ExpressionBool._func("not", [expr])

    def __add__(self, other: "Expression") -> "Expression":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return Expression._operator("+", [self, other])
    
    def __radd__(self, other: "Expression") -> "Expression":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return Expression._operator("+", [other, self])
    
    def __sub__(self, other: "Expression") -> "Expression":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return Expression._operator("-", [self, other])
    
    def __rsub__(self, other: "Expression") -> "Expression":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return Expression._operator("-", [other, self])
    
    def __mul__(self, other: "Expression") -> "Expression":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return Expression._operator("*", [self, other])
    
    def __rmul__(self, other: "Expression") -> "Expression":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return Expression._operator("*", [other, self])
    
    def __truediv__(self, other: "Expression") -> "Expression":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return Expression._operator("/", [self, other])
    
    def __rtruediv__(self, other: "Expression") -> "Expression":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return Expression._operator("/", [other, self])
    
    def __floordiv__(self, other: "Expression") -> "Expression":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return Expression._operator("div", [self, other])
    
    def __rfloordiv__(self, other: "Expression") -> "Expression":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return Expression._operator("div", [other, self])
    
    def __mod__(self, other: "Expression") -> "Expression":
        if (not isinstance(other, (int, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return Expression._operator("mod", [self, other])
    
    def __rmod__(self, other: "Expression") -> "Expression":
        if (not isinstance(other, (int, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return Expression._operator("mod", [other, self])
    
    def __neg__(self) -> "Expression":
        return 0 - self
    #def __pos__(self): return Expression._func("+", [self]) TODO: not allowed in minizinc example: +x == v
    
    def __eq__(self, other: "Expression") -> "ExpressionBool":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return ExpressionBool._operator("==", [self, other])
    
    def __ne__(self, other: "Expression") -> "ExpressionBool":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return ExpressionBool._operator("!=", [self, other])
    
    def __lt__(self, other: "Expression") -> "ExpressionBool":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return ExpressionBool._operator("<", [self, other])
    
    def __le__(self, other: "Expression") -> "ExpressionBool":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return ExpressionBool._operator("<=", [self, other])
    
    def __gt__(self, other: "Expression") -> "ExpressionBool":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return ExpressionBool._operator(">", [self, other])
    
    def __ge__(self, other: "Expression") -> "ExpressionBool":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return ExpressionBool._operator(">=", [self, other])
    
    
    def __and__(self, other: "ExpressionBool") -> "ExpressionBool":
        if (not isinstance(other, (bool, Expression))):
            raise PymzmValueIsNotCondition("other", other)

        return Expression.AND([self, other])
    
    def __rand__(self, other: "ExpressionBool") -> "ExpressionBool":
        if (not isinstance(other, (bool, Expression))):
            raise PymzmValueIsNotCondition("other", other)

        return Expression.AND([other, self])
    
    def __or__(self, other: "ExpressionBool") -> "ExpressionBool":
        if (not isinstance(other, (bool, Expression))):
            raise PymzmValueIsNotCondition("other", other)

        return Expression.OR([self, other])
    
    def __ror__(self, other: "ExpressionBool") -> "ExpressionBool":
        if (not isinstance(other, (bool, Expression))):
            raise PymzmValueIsNotCondition("other", other)

        return Expression.OR([other, self])
    
    def __xor__(self, other: "ExpressionBool") -> "ExpressionBool":
        if (not isinstance(other, (bool, Expression))):
            raise PymzmValueIsNotCondition("other", other)

        return Expression.xor([self, other])
    
    def __rxor__(self, other: "ExpressionBool") -> "ExpressionBool":
        if (not isinstance(other, (bool, Expression))):
            raise PymzmValueIsNotCondition("other", other)

        return Expression.xor([other, self])
    
    def __invert__(self) -> "ExpressionBool":
        return Expression.NOT(self)

    def __pow__(self, other: "Expression") -> "Expression":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)

        return Expression._func("pow", [self, other])
    
    def __rpow__(self, other: "Expression") -> "Expression":
        if (not isinstance(other, (int, float, Expression))):
            raise PymzmValueIsNotExpression("other", other)
        
        return Expression._func("pow", [other, self])
    
    def __abs__(self) -> "Expression":
        return Expression._func("abs", [self])
    # TODO: https://www.minizinc.org/doc-2.7.6/en/lib-stdlib-builtins.html
    # arg max, arg min
    # max, min
    # count
    # exp(x)
    # log_x, log_2, log_10, ln
    # trinonometric functions
    # ..and more!

class ExpressionBool(Expression):
    pass