
from typing import List, Callable
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
    def _ensure_expression_operand(value, arg_name: str="value"):
        if (not isinstance(value, (int, float, Expression))):
            raise PymzmValueIsNotExpression(arg_name, value)

    @staticmethod
    def _ensure_condition_operand(value, arg_name: str="value"):
        if (not isinstance(value, (bool, Expression))):
            raise PymzmValueIsNotCondition(arg_name, value)

    @staticmethod
    def _normalize_numeric_exprs(exprs, arg_name: str="exprs"):
        if (not isinstance(exprs, Iterable)):
            raise PymzmValueIsNotExpression(arg_name, exprs)

        expr_list = list(exprs)
        if (not len(expr_list)):
            raise PymzmNoValues(arg_name)

        for expr in expr_list:
            Expression._ensure_expression_operand(expr, arg_name)
        return expr_list

    @staticmethod
    def _normalize_condition_exprs(exprs, arg_name: str="exprs"):
        if (not isinstance(exprs, Iterable)):
            raise PymzmValueIsNotCondition(arg_name, exprs)

        expr_list = list(exprs)
        for expr in expr_list:
            if (not isinstance(expr, ExpressionBool)):
                raise PymzmValueIsNotCondition(arg_name, expr)
        return expr_list

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
    def _domain_to_mz(domain) -> str:
        if (isinstance(domain, range)):
            if (domain.step != 1):
                raise PymzmValueIsNotExpression("domain", domain)
            if (len(domain) == 0):
                raise PymzmNoValues("domain")
            return f"{domain.start}..{domain.stop - 1}"

        if (isinstance(domain, Expression)):
            return str(domain)

        if (isinstance(domain, str)):
            if (not domain.strip()):
                raise PymzmValueIsNotExpression("domain", domain)
            return domain

        if (isinstance(domain, Iterable)):
            values = list(domain)
            if (not len(values)):
                raise PymzmNoValues("domain")
            return f"{{{', '.join(str(v) for v in values)}}}"

        raise PymzmValueIsNotExpression("domain", domain)

    @staticmethod
    def _predicate_to_mz(var_name: str, predicate) -> str:
        if (isinstance(predicate, Callable)):
            predicate = predicate(Expression(var_name))

        if (isinstance(predicate, bool)):
            return "true" if predicate else "false"

        if (isinstance(predicate, ExpressionBool)):
            return str(predicate)

        raise PymzmValueIsNotCondition("predicate", predicate)

    @staticmethod
    def forall(var_name: str, domain, predicate: "ExpressionBool") -> "ExpressionBool":
        if (not isinstance(var_name, str) or not var_name.strip()):
            raise PymzmValueIsNotExpression("var_name", var_name)

        domain_mz = Expression._domain_to_mz(domain)
        predicate_mz = Expression._predicate_to_mz(var_name, predicate)
        return ExpressionBool(f"forall ({var_name} in {domain_mz}) ({predicate_mz})")

    @staticmethod
    def exists(var_name: str, domain, predicate: "ExpressionBool") -> "ExpressionBool":
        if (not isinstance(var_name, str) or not var_name.strip()):
            raise PymzmValueIsNotExpression("var_name", var_name)

        domain_mz = Expression._domain_to_mz(domain)
        predicate_mz = Expression._predicate_to_mz(var_name, predicate)
        return ExpressionBool(f"exists ({var_name} in {domain_mz}) ({predicate_mz})")

    @staticmethod
    def sum(exprs: List["Expression"]) -> "Expression":
        exprs = Expression._normalize_numeric_exprs(exprs, "exprs")
        return Expression._func("sum", [exprs])
    
    @staticmethod
    def product(exprs) -> "Expression":
        exprs = Expression._normalize_numeric_exprs(exprs, "exprs")
        return Expression._func("product", [exprs])

    @staticmethod
    def min(exprs: List["Expression"]) -> "Expression":
        exprs = Expression._normalize_numeric_exprs(exprs, "exprs")
        return Expression._func("min", [exprs])

    @staticmethod
    def max(exprs: List["Expression"]) -> "Expression":
        exprs = Expression._normalize_numeric_exprs(exprs, "exprs")
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
        exprs = Expression._normalize_condition_exprs(exprs, "exprs")
        return ExpressionBool._operator("\\/", exprs)
    
    @staticmethod
    def AND(exprs: List["ExpressionBool"]) -> "ExpressionBool":
        exprs = Expression._normalize_condition_exprs(exprs, "exprs")
        return ExpressionBool._operator("/\\", exprs)
    
    @staticmethod
    def onlyIf(exprs: List["ExpressionBool"]) -> "ExpressionBool":
        exprs = Expression._normalize_condition_exprs(exprs, "exprs")
        return ExpressionBool._operator("<-", exprs)
    
    @staticmethod
    def implies(exprs: List["ExpressionBool"]) -> "ExpressionBool":
        exprs = Expression._normalize_condition_exprs(exprs, "exprs")
        return ExpressionBool._operator("->", exprs)
    
    @staticmethod
    def iff(exprs: List["ExpressionBool"]) -> "ExpressionBool":
        # <->
        exprs = Expression._normalize_condition_exprs(exprs, "exprs")
        return ExpressionBool._operator("<->", exprs)
    
    @staticmethod
    def xor(exprs: List["ExpressionBool"]) -> "ExpressionBool":
        exprs = Expression._normalize_condition_exprs(exprs, "exprs")
        return ExpressionBool._operator("xor", exprs)
    
    @staticmethod
    def NOT(expr: "ExpressionBool") -> "ExpressionBool":
        if (not isinstance(expr, ExpressionBool)):
            raise PymzmValueIsNotCondition("exprs", expr)

        return ExpressionBool._func("not", [expr])

    def __add__(self, other: "Expression") -> "Expression":
        Expression._ensure_expression_operand(other, "other")

        return Expression._operator("+", [self, other])
    
    def __radd__(self, other: "Expression") -> "Expression":
        Expression._ensure_expression_operand(other, "other")

        return Expression._operator("+", [other, self])
    
    def __sub__(self, other: "Expression") -> "Expression":
        Expression._ensure_expression_operand(other, "other")

        return Expression._operator("-", [self, other])
    
    def __rsub__(self, other: "Expression") -> "Expression":
        Expression._ensure_expression_operand(other, "other")

        return Expression._operator("-", [other, self])
    
    def __mul__(self, other: "Expression") -> "Expression":
        Expression._ensure_expression_operand(other, "other")

        return Expression._operator("*", [self, other])
    
    def __rmul__(self, other: "Expression") -> "Expression":
        Expression._ensure_expression_operand(other, "other")

        return Expression._operator("*", [other, self])
    
    def __truediv__(self, other: "Expression") -> "Expression":
        Expression._ensure_expression_operand(other, "other")

        return Expression._operator("/", [self, other])
    
    def __rtruediv__(self, other: "Expression") -> "Expression":
        Expression._ensure_expression_operand(other, "other")

        return Expression._operator("/", [other, self])
    
    def __floordiv__(self, other: "Expression") -> "Expression":
        Expression._ensure_expression_operand(other, "other")

        return Expression._operator("div", [self, other])
    
    def __rfloordiv__(self, other: "Expression") -> "Expression":
        Expression._ensure_expression_operand(other, "other")

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
        Expression._ensure_expression_operand(other, "other")

        return ExpressionBool._operator("==", [self, other])
    
    def __ne__(self, other: "Expression") -> "ExpressionBool":
        Expression._ensure_expression_operand(other, "other")

        return ExpressionBool._operator("!=", [self, other])
    
    def __lt__(self, other: "Expression") -> "ExpressionBool":
        Expression._ensure_expression_operand(other, "other")

        return ExpressionBool._operator("<", [self, other])
    
    def __le__(self, other: "Expression") -> "ExpressionBool":
        Expression._ensure_expression_operand(other, "other")

        return ExpressionBool._operator("<=", [self, other])
    
    def __gt__(self, other: "Expression") -> "ExpressionBool":
        Expression._ensure_expression_operand(other, "other")

        return ExpressionBool._operator(">", [self, other])
    
    def __ge__(self, other: "Expression") -> "ExpressionBool":
        Expression._ensure_expression_operand(other, "other")

        return ExpressionBool._operator(">=", [self, other])
    
    
    def __and__(self, other: "ExpressionBool") -> "ExpressionBool":
        Expression._ensure_condition_operand(other, "other")

        return Expression.AND([self, other])
    
    def __rand__(self, other: "ExpressionBool") -> "ExpressionBool":
        Expression._ensure_condition_operand(other, "other")

        return Expression.AND([other, self])
    
    def __or__(self, other: "ExpressionBool") -> "ExpressionBool":
        Expression._ensure_condition_operand(other, "other")

        return Expression.OR([self, other])
    
    def __ror__(self, other: "ExpressionBool") -> "ExpressionBool":
        Expression._ensure_condition_operand(other, "other")

        return Expression.OR([other, self])
    
    def __xor__(self, other: "ExpressionBool") -> "ExpressionBool":
        Expression._ensure_condition_operand(other, "other")

        return Expression.xor([self, other])
    
    def __rxor__(self, other: "ExpressionBool") -> "ExpressionBool":
        Expression._ensure_condition_operand(other, "other")

        return Expression.xor([other, self])
    
    def __invert__(self) -> "ExpressionBool":
        return Expression.NOT(self)

    def __pow__(self, other: "Expression") -> "Expression":
        Expression._ensure_expression_operand(other, "other")

        return Expression._func("pow", [self, other])
    
    def __rpow__(self, other: "Expression") -> "Expression":
        Expression._ensure_expression_operand(other, "other")
        
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