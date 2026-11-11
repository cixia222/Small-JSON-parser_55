import pytest

from mjson.cli import main


def test_cli_parse(tmp_path, capsys):
    f = tmp_path / "d.json"
    f.write_text('{"a": 1}', encoding="utf-8")
    assert main(["parse", str(f)]) == 0
    assert "{'a': 1}" in capsys.readouterr().out


def test_cli_validate_ok(tmp_path, capsys):
    f = tmp_path / "ok.json"
    f.write_text("[1,2,3]", encoding="utf-8")
    assert main(["validate", str(f)]) == 0
    assert "合法" in capsys.readouterr().out


def test_cli_validate_bad(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text("{bad}", encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        main(["validate", str(f)])
    assert e.value.code == 1


def test_cli_format(tmp_path, capsys):
    f = tmp_path / "f.json"
    f.write_text('{"a":1}', encoding="utf-8")
    assert main(["format", str(f)]) == 0
    assert '{\n  "a": 1\n}' in capsys.readouterr().out
