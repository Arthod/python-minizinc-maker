
from .expression import *
    
def variableIterable2Str(variables) -> str:
    return str([v.name if isinstance(v, Expression) else v for v in variables]).replace("'", "")

def array_py2mz(arr, shape):
    assert len(shape) <= 2

    return str(arr).replace("], [", "|").replace("[[", "[|").replace("]]", "|]")