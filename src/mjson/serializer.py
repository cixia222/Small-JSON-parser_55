"""序列化（dumps）：把 Python 对象转换成 JSON 文本。

这是解析（loads）的逆过程。本模块同样手写实现，不依赖标准库 json。

支持的类型::

    dict        -> 对象 {}
    list/tuple  -> 数组 []
    str         -> 字符串 ""
    int/float   -> 数字
    bool        -> true / false
    None        -> null
"""

from __future__ import annotations


def dumps(obj, *, indent=None, ensure_ascii: bool = True) -> str:
    """把 Python 对象序列化为 JSON 字符串。

    参数:
        obj: 要序列化的对象。
        indent: None 表示紧凑输出；传 int 表示缩进空格数；传 str 表示缩进字符串。
        ensure_ascii: True 时把非 ASCII 字符转义成 \\uXXXX（与标准库一致）。
    """
    if indent is not None and not isinstance(indent, (int, str)):
        raise TypeError("indent 必须是 int、str 或 None")
    if isinstance(indent, int):
        indent = " " * indent
    return _encode(obj, indent, 0, ensure_ascii)


def dump(obj, fp, *, indent=None, ensure_ascii: bool = True) -> None:
    """把对象序列化并写入文件对象。"""
    fp.write(dumps(obj, indent=indent, ensure_ascii=ensure_ascii))


def _encode(value, indent, level, ensure_ascii):
    # 注意：bool 是 int 的子类，必须先判断 bool
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return _encode_string(value, ensure_ascii)
    if isinstance(value, (int, float)):
        return _encode_number(value)
    if isinstance(value, (list, tuple)):
        return _encode_array(value, indent, level, ensure_ascii)
    if isinstance(value, dict):
        return _encode_object(value, indent, level, ensure_ascii)
    raise TypeError(f"不支持的类型: {type(value).__name__}")


def _encode_number(value):
    if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
        raise ValueError("JSON 不支持 NaN 和 Infinity")
    if isinstance(value, float):
        return repr(value)
    return str(value)


def _encode_string(value: str, ensure_ascii: bool) -> str:
    out = ['"']
    for ch in value:
        cp = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif ch == "\b":
            out.append("\\b")
        elif ch == "\f":
            out.append("\\f")
        elif cp < 0x20:
            out.append(f"\\u{cp:04x}")
        elif ensure_ascii and cp > 0x7F:
            if cp > 0xFFFF:
                out.append("\\u" + _surrogate_pair(ch))
            else:
                out.append(f"\\u{cp:04x}")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def _surrogate_pair(ch: str) -> str:
    """把码点 > 0xFFFF 的字符转成两个 UTF-16 代理对。"""
    cp = ord(ch) - 0x10000
    high = 0xD800 + (cp >> 10)
    low = 0xDC00 + (cp & 0x3FF)
    return f"{high:04x}{low:04x}"


def _encode_array(items, indent, level, ensure_ascii):
    if not items:
        return "[]"
    if indent is None:
        body = ",".join(_encode(v, None, 0, ensure_ascii) for v in items)
        return f"[{body}]"
    pad = indent * level
    inner = indent * (level + 1)
    lines = [inner + _encode(v, indent, level + 1, ensure_ascii) for v in items]
    body = ",\n".join(lines)
    return f"[\n{body}\n{pad}]"


def _encode_object(mapping, indent, level, ensure_ascii):
    if not mapping:
        return "{}"
    keys = list(mapping.keys())
    if indent is None:
        parts = []
        for k in keys:
            _check_key(k)
            parts.append(f"{_encode_string(k, ensure_ascii)}:{_encode(mapping[k], None, 0, ensure_ascii)}")
        return "{" + ",".join(parts) + "}"
    pad = indent * level
    inner = indent * (level + 1)
    parts = []
    for k in keys:
        _check_key(k)
        parts.append(
            inner + f"{_encode_string(k, ensure_ascii)}: {_encode(mapping[k], indent, level + 1, ensure_ascii)}"
        )
    body = ",\n".join(parts)
    return f"{{\n{body}\n{pad}}}"


def _check_key(key):
    if not isinstance(key, str):
        raise TypeError(f"JSON 对象的键必须是字符串，但得到了 {type(key).__name__}")
