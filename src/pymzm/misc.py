
from .expression import *
    
def variableIterable2Str(variables) -> str:
    return str([v.name if isinstance(v, Expression) else v for v in variables]).replace("'", "")

def scalar_py2mz(value):
    if (isinstance(value, bool)):
        return "true" if value else "false"
    if (isinstance(value, str)):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return str(value)


def set_py2mz(values) -> str:
    values_list = list(values)
    values_list.sort(key=lambda v: (type(v).__name__, str(v)))
    return "{" + ", ".join(scalar_py2mz(v) if isinstance(v, str) else str(v) for v in values_list) + "}"


def array_py2mz(arr, shape, scalar_formatter=scalar_py2mz):
    arr_list = arr.tolist() if hasattr(arr, "tolist") else arr

    if (len(shape) == 1):
        return "[" + ", ".join(scalar_formatter(v) for v in arr_list) + "]"

    if (len(shape) == 2):
        rows = [
            ", ".join(scalar_formatter(v) for v in row)
            for row in arr_list
        ]
        return "[|" + "|".join(rows) + "|]"

    def _flatten(values):
        if (isinstance(values, (list, tuple))):
            out = []
            for value in values:
                out.extend(_flatten(value))
            return out
        return [values]

    flat = _flatten(arr_list)
    idx_sets = ", ".join(f"1..{d}" for d in shape)
    flat_values = ", ".join(scalar_formatter(v) for v in flat)
    return f"array{len(shape)}d({idx_sets}, [{flat_values}])"