import pytest

from mjson import dumps, loads


def test_roundtrip():
    obj = {"name": "张三", "age": 20, "tags": ["a", "b"], "ok": True, "nil": None, "pi": 3.14}
    assert loads(dumps(obj)) == obj


def test_dumps_scalars():
    assert dumps(None) == "null"
    assert dumps(True) == "true"
    assert dumps(False) == "false"
    assert dumps(42) == "42"
    assert dumps(-3.5) == "-3.5"
    assert dumps("hi") == '"hi"'


def test_dumps_compact():
    assert dumps({"a": 1, "b": [1, 2]}) == '{"a":1,"b":[1,2]}'


def test_dumps_indent():
    assert dumps({"a": 1}, indent=2) == '{\n  "a": 1\n}'


def test_dumps_string_escape():
    assert dumps('a"b\\c\n') == '"a\\"b\\\\c\\n"'


def test_dumps_non_ascii():
    assert dumps("中文") == '"\\u4e2d\\u6587"'
    assert dumps("中文", ensure_ascii=False) == '"中文"'


def test_dumps_rejects_bad_types():
    with pytest.raises(TypeError):
        dumps({"a": object()})
    with pytest.raises(TypeError):
        dumps({1: "a"})
    with pytest.raises(ValueError):
        dumps(float("nan"))
