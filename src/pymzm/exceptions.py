

class PymzmException(Exception):
    pass

class PymzmInvalidConstraintType(PymzmException):
    def __init__(self, argname):
        self.argname = argname

    def __str__(self):
        return f"Argument \"{self.argname}\" is not a valid constraint type."

class PymzmValueIsNotCondition(PymzmException):
    def __init__(self, argname, expr):
        self.argname = argname
        self.expr = expr

    def __str__(self):
        return f"Argument \"{self.argname}\": {repr(self.expr)} (type={type(self.expr)}) is not valid as a condition."

class PymzmValueIsNotExpression(PymzmException):
    def __init__(self, argname, expr):
        self.argname = argname
        self.expr = expr

    def __str__(self):
        return f"Argument \"{self.argname}\": {repr(self.expr)} (type={type(self.expr)}) is not valid as a expression."

class PymzmNoValues(PymzmException):
    def __init__(self, argname):
        self.argname = argname

    def __str__(self):
        return f"Argument \"{self.argname}\", expected iterable but has no values."
    
class PymzmInvalidVarchoiceAnnotation(PymzmException):
    def __init__(self, argname):
        self.argname = argname

    def __str__(self):
        return f"Argument \"{self.argname}\" is not valid as a varchoice annotation."
    
class PymzmInvalidConstraintAnnotation(PymzmException):
    def __init__(self, argname):
        self.argname = argname

    def __str__(self):
        return f"Argument \"{self.argname}\" is not valid as a constraint annotation."
    
class PymzmInvalidValchoiceAnnotation(PymzmException):
    def __init__(self, argname):
        self.argname = argname

    def __str__(self):
        return f"Argument \"{self.argname}\" is not valid as a valchoice annotation."
    
class PymzmInvalidVariableError(PymzmException):
    def __init__(self, argname, msg):
        self.argname = argname
        self.msg = msg

    def __str__(self):
        return f"Argument \"{self.argname}\" error. {self.msg}."

class PymzmInvalidSearchAnnotation(PymzmException):
    def __init__(self):
        pass
    def __str__(self):
        return f"PymzmInvalidSearchAnnotation."