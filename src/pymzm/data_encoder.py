def _sort_key(value):
    return (type(value).__name__, str(value))


def _tolist_if_available(value):
    if hasattr(value, "tolist"):
        return value.tolist()
    return value


def infer_shape(value):
    normalized = _tolist_if_available(value)

    def _shape_of(node):
        if isinstance(node, (list, tuple)):
            if len(node) == 0:
                return (0,)
            return (len(node), *_shape_of(node[0]))
        return ()

    shape = _shape_of(normalized)
    return shape if (len(shape) > 0) else None


def encode_scalar(value, vtype=None, is_enum_type=False):
    if value is None:
        return "<>"

    if hasattr(value, "_to_mz_token"):
        return value._to_mz_token()

    if is_enum_type:
        if isinstance(value, str):
            return value
        return str(value)

    if vtype == "bool" or isinstance(value, bool):
        return "true" if bool(value) else "false"

    if vtype == "string" or isinstance(value, str):
        escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    return str(value)


def encode_set(values, vtype=None, is_enum_type=False):
    sorted_values = sorted(list(values), key=_sort_key)
    return (
        "{"
        + ", ".join(
            encode_scalar(v, vtype=vtype, is_enum_type=is_enum_type)
            for v in sorted_values
        )
        + "}"
    )


def encode_array(
    values, shape=None, scalar_formatter=None, vtype=None, is_enum_type=False
):
    normalized = _tolist_if_available(values)
    if shape is None:
        shape = infer_shape(normalized)
    assert shape is not None

    if scalar_formatter is None:

        def scalar_formatter(value):
            return encode_scalar(value, vtype=vtype, is_enum_type=is_enum_type)

    if len(shape) == 1:
        return "[" + ", ".join(scalar_formatter(v) for v in normalized) + "]"

    if len(shape) == 2:
        rows = [", ".join(scalar_formatter(v) for v in row) for row in normalized]
        return "[|" + "|".join(rows) + "|]"

    def _flatten(node):
        if isinstance(node, (list, tuple)):
            out = []
            for child in node:
                out.extend(_flatten(child))
            return out
        return [node]

    flat = _flatten(normalized)
    idx_sets = ", ".join(f"1..{d}" for d in shape)
    flat_values = ", ".join(scalar_formatter(v) for v in flat)
    return f"array{len(shape)}d({idx_sets}, [{flat_values}])"


def encode_dict(values, vtype=None, is_enum_type=False):
    items = sorted(values.items(), key=lambda kv: _sort_key(kv[0]))
    rendered = ", ".join(
        f"{encode_scalar(k)}: {encode_value(v, vtype=vtype, is_enum_type=is_enum_type)}"
        for k, v in items
    )
    return f"[{rendered}]"


def encode_value(value, vtype=None, is_enum_type=False):
    if isinstance(value, dict):
        return encode_dict(value, vtype=vtype, is_enum_type=is_enum_type)

    if isinstance(value, (set, frozenset)):
        return encode_set(value, vtype=vtype, is_enum_type=is_enum_type)

    shape = infer_shape(value)
    if shape is not None:
        return encode_array(value, shape=shape, vtype=vtype, is_enum_type=is_enum_type)

    return encode_scalar(value, vtype=vtype, is_enum_type=is_enum_type)
