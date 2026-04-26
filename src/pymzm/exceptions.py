class PymzmException(Exception):
    """Base exception for all pymzm-specific failures."""


class PymzmValidationError(PymzmException):
    """Base class for invalid input or invalid model state errors."""


class PymzmArgumentError(PymzmValidationError):
    def __init__(self, argname, message):
        self.argname = argname
        self.message = message

    def __str__(self):
        return f"Invalid argument '{self.argname}': {self.message}"


class PymzmModelStateError(PymzmValidationError):
    pass


class PymzmConfigurationError(PymzmValidationError):
    pass


class PymzmInvalidConstraintType(PymzmArgumentError):
    def __init__(self, argname, value=None):
        self.value = value
        message = "expected one of Constraint.CTYPES"
        if value is not None:
            message += f", got {value!r}"
        super().__init__(argname, message)


class PymzmValueIsNotCondition(PymzmArgumentError):
    def __init__(self, argname, expr):
        self.expr = expr
        expr_type = type(expr).__name__
        super().__init__(
            argname,
            f"expected a boolean condition expression, got {expr!r} (type={expr_type})",
        )


class PymzmValueIsNotExpression(PymzmArgumentError):
    def __init__(self, argname, expr):
        self.expr = expr
        expr_type = type(expr).__name__
        super().__init__(
            argname,
            f"expected an expression-compatible value, got {expr!r} (type={expr_type})",
        )


class PymzmNoValues(PymzmArgumentError):
    def __init__(self, argname):
        super().__init__(argname, "expected a non-empty iterable")


class PymzmInvalidVarchoiceAnnotation(PymzmArgumentError):
    def __init__(self, argname, value=None):
        self.value = value
        message = "expected one of AnnotationVariableChoice.VARCHOICES"
        if value is not None:
            message += f", got {value!r}"
        super().__init__(argname, message)


class PymzmInvalidConstraintAnnotation(PymzmArgumentError):
    def __init__(self, argname, value=None):
        self.value = value
        message = "expected one of AnnotationConstraint.ANNOTATIONS"
        if value is not None:
            message += f", got {value!r}"
        super().__init__(argname, message)


class PymzmInvalidValchoiceAnnotation(PymzmArgumentError):
    def __init__(self, argname, value=None):
        self.value = value
        message = "expected one of AnnotationValueChoice.VALCHOICES"
        if value is not None:
            message += f", got {value!r}"
        super().__init__(argname, message)


class PymzmInvalidVariableError(PymzmArgumentError):
    def __init__(self, argname, msg):
        self.msg = msg
        super().__init__(argname, msg)


class PymzmInvalidSearchAnnotation(PymzmValidationError):
    def __str__(self):
        return "Invalid search annotation: expected SearchAnnotation instances in seq_search(...)"


class PymzmInvalidSolveCriteria(PymzmConfigurationError):
    def __init__(self, criteria):
        self.criteria = criteria

    def __str__(self):
        return (
            "Invalid solve criteria: "
            f"{self.criteria!r}. Expected one of 'satisfy', 'minimize', or 'maximize'."
        )


class PymzmUnsupportedVariableType(PymzmArgumentError):
    def __init__(self, vtype):
        self.vtype = vtype
        super().__init__(
            "vtype",
            f"unsupported variable type {vtype!r}; expected one of int, float, bool, string, set",
        )


class PymzmNonInitializedConstant(PymzmModelStateError):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Constant '{self.name}' is not initialized. Use add_parameter(..., value=None) for declaration-only data."


class PymzmInvalidScalarType(PymzmArgumentError):
    def __init__(self, kind, vtype):
        self.kind = kind
        self.vtype = vtype
        super().__init__(
            "vtype",
            f"invalid {kind} scalar type {vtype!r}; supported scalar types are int, bool, float, string, or enum type names",
        )


class PymzmIndexingScalarValue(PymzmModelStateError):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Value '{self.name}' is scalar and cannot be indexed."


class PymzmSolveNotConfigured(PymzmModelStateError):
    def __str__(self):
        return (
            "Solve criteria not configured. "
            "Call model.set_solve_criteria(...) before generating or solving."
        )


class PymzmVariableTypeError(PymzmArgumentError):
    def __init__(self, argname, expected_vtype, actual_vtype):
        self.expected_vtype = expected_vtype
        self.actual_vtype = actual_vtype
        super().__init__(
            argname,
            f"operation requires variable type {expected_vtype!r}, got {actual_vtype!r}",
        )
