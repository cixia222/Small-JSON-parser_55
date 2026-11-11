import pytest

from mjson import loads
from mjson.errors import MjsonError


@pytest.mark.parametrize(
    "text, keyword",
    [
        ("", "输入为空"),
        ("{", "输入结尾"),
        ("[1,]", "值"),
        ('{"a" 1}', "':'"),
        ('{"a": 1', "输入结尾"),
        ("tru", "非法字符"),
        ("0123", "前导零"),
        ('"abc', "未闭合"),
        ("[1 2]", "','"),
        ('{"a": 1 "b": 2}', "','"),
    ],
)
def test_invalid_json_raises(text, keyword):
    with pytest.raises(MjsonError) as e:
        loads(text)
    assert keyword in e.value.message


def test_error_reports_line_and_column():
    with pytest.raises(MjsonError) as e:
        loads('{\n  "a": 1,\n  "b": 2,\n  bad\n}')
    assert e.value.line == 4
    assert e.value.column == 3


def test_error_caret_context():
    try:
        loads('{\n  "a": 1,\n  "b": oops\n}')
    except MjsonError as e:
        msg = str(e)
        assert "^" in msg
        assert "oops" in msg
