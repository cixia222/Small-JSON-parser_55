from mjson import loads


def test_empty_object_and_array():
    assert loads("{}") == {}
    assert loads("[]") == []


def test_scalars():
    assert loads("null") is None
    assert loads("true") is True
    assert loads("false") is False
    assert loads("42") == 42
    assert loads("-17") == -17
    assert loads("3.14") == 3.14
    assert loads("1e3") == 1000.0
    assert loads("1E-2") == 0.01
    assert loads('"hello"') == "hello"


def test_nested():
    data = '{"a": [1, 2, {"b": null}], "c": true}'
    assert loads(data) == {"a": [1, 2, {"b": None}], "c": True}


def test_string_escapes():
    assert loads(r'"a\nb\tc\"d\\e"') == 'a\nb\tc"d\\e'
    assert loads(r'"\u4e2d\u6587"') == "中文"


def test_whitespace_and_newlines():
    data = '  {\n    "x" : 1 ,\n    "y" : [ true , false ]\n  }  '
    assert loads(data) == {"x": 1, "y": [True, False]}


def test_zero_edge():
    assert loads("0") == 0
    assert loads("-0") == 0
    assert loads("0.0") == 0.0


def test_duplicate_keys_last_wins():
    assert loads('{"a": 1, "a": 2}') == {"a": 2}
