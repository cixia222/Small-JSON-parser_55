from mjson import tokenizer as tk


def test_token_types():
    tokens = list(tk.Tokenizer('{"a": 1}').tokenize())
    assert [t.type for t in tokens] == [
        tk.LBRACE, tk.STRING, tk.COLON, tk.NUMBER, tk.RBRACE, tk.EOF
    ]


def test_token_values():
    tokens = list(tk.Tokenizer('{"a": 1}').tokenize())
    assert tokens[1].value == "a"
    assert tokens[3].value == "1"


def test_token_positions():
    tokens = list(tk.Tokenizer('{\n  "a"\n}').tokenize())
    s = tokens[1]
    assert s.type == tk.STRING
    assert s.value == "a"
    assert s.line == 2
    assert s.column == 3


def test_keywords():
    tokens = list(tk.Tokenizer("true false null").tokenize())
    assert [t.type for t in tokens] == [tk.TRUE, tk.FALSE, tk.NULL, tk.EOF]
