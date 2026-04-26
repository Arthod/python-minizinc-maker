
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
    def _set_operand_to_mz(value, arg_name: str="value") -> str:
        if (isinstance(value, Expression)):
            return str(value)
        if (isinstance(value, str)):
            if (not value.strip()):
                raise PymzmValueIsNotExpression(arg_name, value)
            return value
        if (isinstance(value, Iterable)):
            values = list(value)
            if (not len(values)):
                raise PymzmNoValues(arg_name)
            return "{" + ", ".join(str(v) for v in values) + "}"
        raise PymzmValueIsNotExpression(arg_name, value)

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
    def _normalize_annotations(annotations, arg_name: str="annotations"):
        if (annotations is None):
            return []

        if (isinstance(annotations, (str, Annotation))):
            annotations = [annotations]

        if (not isinstance(annotations, Iterable)):
            raise PymzmValueIsNotExpression(arg_name, annotations)

        normalized = []
        for annotation in annotations:
            if (isinstance(annotation, Annotation)):
                normalized.append(str(annotation))
            elif (isinstance(annotation, str) and annotation.strip()):
                normalized.append(annotation.strip())
            else:
                raise PymzmValueIsNotExpression(arg_name, annotation)
        return normalized

    @staticmethod
    def _scalar_to_mz(value):
        if (isinstance(value, bool)):
            return "true" if value else "false"
        return str(value)

    @staticmethod
    def _normalize_let_declarations(declarations, arg_name: str="declarations"):
        if (isinstance(declarations, str)):
            declarations = [declarations]

        if (not isinstance(declarations, Iterable)):
            raise PymzmValueIsNotExpression(arg_name, declarations)

        normalized = []
        for declaration in declarations:
            if (not isinstance(declaration, str) or not declaration.strip()):
                raise PymzmValueIsNotExpression(arg_name, declaration)
            normalized.append(declaration.strip().rstrip(";"))

        if (not len(normalized)):
            raise PymzmNoValues(arg_name)
        return normalized

    def annotate(self, *annotations):
        normalized = Expression._normalize_annotations(annotations, "annotations")
        if (not len(normalized)):
            raise PymzmNoValues("annotations")

        expression_text = f"{self}"
        for annotation in normalized:
            expression_text += f" :: {annotation}"

        if (isinstance(self, ExpressionBool)):
            return ExpressionBool(expression_text)
        return Expression(expression_text)

    @staticmethod
    def let(declarations, in_expr):
        declarations = Expression._normalize_let_declarations(declarations, "declarations")

        if (not isinstance(in_expr, (Expression, bool, int, float))):
            raise PymzmValueIsNotExpression("in_expr", in_expr)

        body = str(in_expr) if isinstance(in_expr, Expression) else Expression._scalar_to_mz(in_expr)
        let_text = f"let {{ {' '.join(f'{d};' for d in declarations)} }} in ({body})"

        if (isinstance(in_expr, (ExpressionBool, bool))):
            return ExpressionBool(let_text)
        return Expression(let_text)

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
        return Expression.conditional([(condition, expr1)], expr2)

    @staticmethod
    def conditional(branches, else_expr):
        if (not isinstance(branches, Iterable)):
            raise PymzmValueIsNotExpression("branches", branches)

        branches = list(branches)
        if (not len(branches)):
            raise PymzmNoValues("branches")

        parts = []
        for i, branch in enumerate(branches):
            if (not isinstance(branch, (tuple, list)) or len(branch) != 2):
                raise PymzmValueIsNotExpression("branches", branch)

            condition, expr = branch
            if (not isinstance(condition, (ExpressionBool, bool))):
                raise PymzmValueIsNotCondition(f"condition_{i}", condition)
            if (not isinstance(expr, (Expression, int, float, bool))):
                raise PymzmValueIsNotExpression(f"expr_{i}", expr)

            condition_mz = "true" if condition is True else "false" if condition is False else str(condition)
            expr_mz = "true" if expr is True else "false" if expr is False else str(expr)

            if (i == 0):
                parts.append(f"if {condition_mz} then {expr_mz}")
            else:
                parts.append(f"elseif {condition_mz} then {expr_mz}")

        if (not isinstance(else_expr, (Expression, int, float, bool))):
            raise PymzmValueIsNotExpression("else_expr", else_expr)

        else_mz = "true" if else_expr is True else "false" if else_expr is False else str(else_expr)
        parts.append(f"else {else_mz} endif")
        conditional_text = " ".join(parts)

        has_bool_body = isinstance(else_expr, (ExpressionBool, bool)) and all(
            isinstance(expr, (ExpressionBool, bool))
            for _, expr in branches
        )

        if (has_bool_body):
            return ExpressionBool(f"({conditional_text})")
        return Expression(f"({conditional_text})")

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
    def _generator_clause_to_mz(generator, arg_name: str="generators") -> str:
        if (not isinstance(generator, (tuple, list)) or len(generator) not in (2, 3)):
            raise PymzmValueIsNotExpression(arg_name, generator)

        var_name = generator[0]
        domain = generator[1]
        predicate = generator[2] if (len(generator) == 3) else None

        if (not isinstance(var_name, str) or not var_name.strip()):
            raise PymzmValueIsNotExpression("var_name", var_name)

        domain_mz = Expression._domain_to_mz(domain)
        clause = f"{var_name} in {domain_mz}"
        if (predicate is not None):
            predicate_mz = Expression._predicate_to_mz(var_name, predicate)
            clause += f" where {predicate_mz}"

        return clause

    @staticmethod
    def _comprehension_expr_to_mz(expr, generator_var_names):
        if (isinstance(expr, Callable)):
            vars_expr = [Expression(name) for name in generator_var_names]
            if (len(vars_expr) == 1):
                expr = expr(vars_expr[0])
            else:
                expr = expr(*vars_expr)

        if (isinstance(expr, bool)):
            return "true" if expr else "false"

        if (isinstance(expr, (Expression, int, float))):
            return str(expr)

        raise PymzmValueIsNotExpression("expr", expr)

    @staticmethod
    def _quantifier_predicate_to_mz(predicate, generator_var_names):
        if (isinstance(predicate, Callable)):
            vars_expr = [Expression(name) for name in generator_var_names]
            if (len(vars_expr) == 1):
                predicate = predicate(vars_expr[0])
            else:
                predicate = predicate(*vars_expr)

        if (isinstance(predicate, bool)):
            return "true" if predicate else "false"
        if (isinstance(predicate, ExpressionBool)):
            return str(predicate)

        raise PymzmValueIsNotCondition("predicate", predicate)

    @staticmethod
    def _normalize_generators(generators, arg_name: str="generators"):
        if (not isinstance(generators, Iterable) or isinstance(generators, (str, bytes))):
            raise PymzmValueIsNotExpression(arg_name, generators)

        generators = list(generators)
        if (not len(generators)):
            raise PymzmNoValues(arg_name)

        return generators

    @staticmethod
    def array_comprehension(expr, generators):
        generators = Expression._normalize_generators(generators, "generators")

        clauses = [Expression._generator_clause_to_mz(g) for g in generators]
        expr_mz = Expression._comprehension_expr_to_mz(expr, [g[0] for g in generators])
        return Expression(f"[{expr_mz} | {', '.join(clauses)}]")

    @staticmethod
    def set_comprehension(expr, generators):
        generators = Expression._normalize_generators(generators, "generators")

        clauses = [Expression._generator_clause_to_mz(g) for g in generators]
        expr_mz = Expression._comprehension_expr_to_mz(expr, [g[0] for g in generators])
        return Expression(f"{{{expr_mz} | {', '.join(clauses)}}}")

    @staticmethod
    def predicate(name: str, *args) -> "ExpressionBool":
        if (not isinstance(name, str) or not name.strip()):
            raise PymzmValueIsNotExpression("name", name)
        return ExpressionBool._func(name.strip(), list(args))

    @staticmethod
    def function(name: str, *args, returns_bool: bool=False):
        if (not isinstance(name, str) or not name.strip()):
            raise PymzmValueIsNotExpression("name", name)
        if (returns_bool):
            return ExpressionBool._func(name.strip(), list(args))
        return Expression._func(name.strip(), list(args))

    @staticmethod
    def forall(var_name: str, domain, predicate: "ExpressionBool") -> "ExpressionBool":
        return Expression.forall_over([(var_name, domain)], predicate)

    @staticmethod
    def exists(var_name: str, domain, predicate: "ExpressionBool") -> "ExpressionBool":
        return Expression.exists_over([(var_name, domain)], predicate)

    @staticmethod
    def forall_over(generators, predicate: "ExpressionBool") -> "ExpressionBool":
        generators = Expression._normalize_generators(generators, "generators")
        clauses = [Expression._generator_clause_to_mz(g) for g in generators]
        predicate_mz = Expression._quantifier_predicate_to_mz(predicate, [g[0] for g in generators])
        return ExpressionBool(f"forall ({', '.join(clauses)}) ({predicate_mz})")

    @staticmethod
    def exists_over(generators, predicate: "ExpressionBool") -> "ExpressionBool":
        generators = Expression._normalize_generators(generators, "generators")
        clauses = [Expression._generator_clause_to_mz(g) for g in generators]
        predicate_mz = Expression._quantifier_predicate_to_mz(predicate, [g[0] for g in generators])
        return ExpressionBool(f"exists ({', '.join(clauses)}) ({predicate_mz})")

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
        out = ", ".join(str(a) for a in exprs2)
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

    def __getitem__(self, index):
        def _idx_to_mz(idx):
            if (isinstance(idx, int)):
                return str(idx + 1)
            if (isinstance(idx, Expression)):
                return f"{idx} + 1"
            raise PymzmValueIsNotExpression("index", idx)

        if (isinstance(index, (tuple, list))):
            if (not len(index)):
                raise PymzmNoValues("index")
            idx_mz = ", ".join(_idx_to_mz(idx) for idx in index)
        else:
            idx_mz = _idx_to_mz(index)

        return Expression(f"{self}[{idx_mz}]")

    def in_(self, container) -> "ExpressionBool":
        rhs = Expression._set_operand_to_mz(container, "container")
        return ExpressionBool(f"({self} in {rhs})")

    def not_in(self, container) -> "ExpressionBool":
        rhs = Expression._set_operand_to_mz(container, "container")
        return ExpressionBool(f"({self} not in {rhs})")

    def subset_of(self, other) -> "ExpressionBool":
        rhs = Expression._set_operand_to_mz(other, "other")
        return ExpressionBool(f"({self} subset {rhs})")

    def superset_of(self, other) -> "ExpressionBool":
        rhs = Expression._set_operand_to_mz(other, "other")
        return ExpressionBool(f"({self} superset {rhs})")

    def union(self, other) -> "Expression":
        rhs = Expression._set_operand_to_mz(other, "other")
        return Expression(f"({self} union {rhs})")

    def intersection(self, other) -> "Expression":
        rhs = Expression._set_operand_to_mz(other, "other")
        return Expression(f"({self} intersect {rhs})")

    def set_diff(self, other) -> "Expression":
        rhs = Expression._set_operand_to_mz(other, "other")
        return Expression(f"({self} diff {rhs})")

    def symdiff(self, other) -> "Expression":
        rhs = Expression._set_operand_to_mz(other, "other")
        return Expression(f"(({self} diff {rhs}) union ({rhs} diff {self}))")
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


class Annotation:
    def __init__(self, name: str, *args):
        if (not isinstance(name, str) or not name.strip()):
            raise PymzmValueIsNotExpression("name", name)
        self.name = name.strip()
        self.args = list(args)

    def __str__(self):
        if (not len(self.args)):
            return self.name
        return f"{self.name}({', '.join(self._format_arg(arg) for arg in self.args)})"

    @classmethod
    def _format_arg(cls, arg):
        if (isinstance(arg, Annotation)):
            return str(arg)
        if (isinstance(arg, Expression)):
            return str(arg)
        if (arg is None):
            return "<>"
        if (isinstance(arg, bool)):
            return "true" if arg else "false"
        if (isinstance(arg, (list, tuple))):
            return "[" + ", ".join(cls._format_arg(a) for a in arg) + "]"
        if (isinstance(arg, set)):
            return "{" + ", ".join(sorted(cls._format_arg(a) for a in arg)) + "}"
        return str(arg)