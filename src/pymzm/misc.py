
from .expression import *
from .data_encoder import encode_scalar, encode_set, encode_array
    
def variableIterable2Str(variables) -> str:
    return str([v.name if isinstance(v, Expression) else v for v in variables]).replace("'", "")

def scalar_py2mz(value):
    return encode_scalar(value)


def set_py2mz(values) -> str:
    return encode_set(values)


def array_py2mz(arr, shape, scalar_formatter=scalar_py2mz):
    return encode_array(arr, shape=shape, scalar_formatter=scalar_formatter)