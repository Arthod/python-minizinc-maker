
from .expression import *
    
def variableIterable2Str(variables) -> str:
    return str([v.name if isinstance(v, Expression) else v for v in variables]).replace("'", "")