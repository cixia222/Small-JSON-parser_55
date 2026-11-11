"""词法分析（Tokenizer）：把一段 JSON 文本切成一个个 token。

词法分析是编译的第一步。它不关心 JSON 的整体结构，
只负责把连续的字符流切成有意义的"小片段"（token），
例如 ``{``、``"name"``、``:``、``123``、``true`` 等。

每个 token 都带着它出现在原文中的行、列，供后面报错使用。
"""

from __future__ import annotations

from .errors import MjsonError

# token 类型常量
LBRACE = "LBRACE"      # {
RBRACE = "RBRACE"      # }
LBRACKET = "LBRACKET"  # [
RBRACKET = "RBRACKET"  # ]
COMMA = "COMMA"        # ,
COLON = "COLON"        # :
STRING = "STRING"      # "abc"
NUMBER = "NUMBER"      # 123 / -3.14 / 1e10
TRUE = "TRUE"          # true
FALSE = "FALSE"        # false
NULL = "NULL"          # null
EOF = "EOF"            # 输入结束标记


class Token:
    """一个 token：类型 + 值 + 位置。"""

    __slots__ = ("type", "value", "line", "column")

    def __init__(self, type_: str, value, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self) -> str:
        return f"Token({self.type}, {self.value!r}, {self.line}:{self.column})"


class Tokenizer:
    """把 JSON 文本切成 token 的迭代器。"""

    # 转义字符映射表（JSON 规范里允许的转义）
    _ESCAPES = {
        '"': '"',
        "\\": "\\",
        "/": "/",
        "b": "\b",
        "f": "\f",
        "n": "\n",
        "r": "\r",
        "t": "\t",
    }

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1

    # ---------- 底层辅助 ----------

    def _peek(self, offset: int = 0) -> str:
        """看当前位置（或往后 offset 位）的字符，不越过末尾。"""
        idx = self.pos + offset
        return self.text[idx] if idx < len(self.text) else ""

    def _advance(self) -> str:
        """前进一个字符，并维护行、列号。"""
        ch = self.text[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _eof(self) -> bool:
        return self.pos >= len(self.text)

    def _make(self, type_: str, value, line: int, column: int) -> Token:
        return Token(type_, value, line, column)

    # ---------- 各类 token 的读取 ----------

    def _read_single(self, type_: str) -> Token:
        """读取一个单字符 token（{ } [ ] , :）。"""
        line, column = self.line, self.column
        self._advance()
        return self._make(type_, None, line, column)

    def _read_keyword(self, type_: str, word: str) -> Token:
        """读取 true/false/null 这类固定关键字。"""
        line, column = self.line, self.column
        for _ in word:
            self._advance()
        return self._make(type_, word, line, column)

    def _read_string(self) -> Token:
        """读取一个字符串 token（含转义处理）。"""
        line, column = self.line, self.column
        self._advance()  # 跳过开头的引号 "
        result = []
        while True:
            if self._eof():
                raise MjsonError("字符串未闭合（缺少结尾引号）", line, column, self.text)
            ch = self._advance()
            if ch == '"':
                break
            if ch == "\\":
                result.append(self._read_escape(line, column))
            elif ord(ch) < 0x20:
                # JSON 不允许字符串里出现未转义的控制字符
                raise MjsonError("字符串中包含未转义的控制字符", self.line, self.column, self.text)
            else:
                result.append(ch)
        return self._make(STRING, "".join(result), line, column)

    def _read_escape(self, str_line: int, str_column: int) -> str:
        """读取一个转义序列（跟在反斜杠后面的内容）。"""
        if self._eof():
            raise MjsonError("转义序列不完整", str_line, str_column, self.text)
        ch = self._advance()
        if ch in self._ESCAPES:
            return self._ESCAPES[ch]
        if ch == "u":
            return self._read_unicode_escape(str_line, str_column)
        raise MjsonError(f"非法的转义字符 \\{ch}", self.line, self.column, self.text)

    def _read_unicode_escape(self, line: int, column: int) -> str:
        """读取 \\uXXXX 形式的 Unicode 转义。"""
        hex_digits = ""
        for _ in range(4):
            if self._eof():
                raise MjsonError("\\u 转义不完整（需要 4 位十六进制）", line, column, self.text)
            ch = self._advance()
            if ch not in "0123456789abcdefABCDEF":
                raise MjsonError(
                    f"\\u 后面不是合法的十六进制字符 {ch!r}", self.line, self.column, self.text
                )
            hex_digits += ch
        return chr(int(hex_digits, 16))

    def _read_number(self) -> Token:
        """按 JSON 规范读取一个数字（支持负数、小数、科学计数法）。"""
        line, column = self.line, self.column
        start = self.pos

        if self._peek() == "-":
            self._advance()

        # 整数部分
        if self._peek() == "0":
            self._advance()
            # JSON 不允许 "0123" 这种前导零
            if self._peek().isdigit():
                raise MjsonError("数字不能有前导零（如 0123）", self.line, self.column, self.text)
        elif self._peek().isdigit():
            while self._peek().isdigit():
                self._advance()
        else:
            raise MjsonError("减号后面必须跟数字", self.line, self.column, self.text)

        # 小数部分
        if self._peek() == ".":
            self._advance()
            if not self._peek().isdigit():
                raise MjsonError("小数点后面必须跟数字", self.line, self.column, self.text)
            while self._peek().isdigit():
                self._advance()

        # 指数部分
        if self._peek() in ("e", "E"):
            self._advance()
            if self._peek() in ("+", "-"):
                self._advance()
            if not self._peek().isdigit():
                raise MjsonError("指数部分必须跟数字", self.line, self.column, self.text)
            while self._peek().isdigit():
                self._advance()

        raw = self.text[start:self.pos]
        return self._make(NUMBER, raw, line, column)

    # ---------- 主入口 ----------

    def tokenize(self):
        """生成全部 token，直到输入结束。"""
        while not self._eof():
            ch = self._peek()

            if ch in " \t\r\n":
                self._advance()  # 跳过空白
                continue

            if ch == "{":
                yield self._read_single(LBRACE)
            elif ch == "}":
                yield self._read_single(RBRACE)
            elif ch == "[":
                yield self._read_single(LBRACKET)
            elif ch == "]":
                yield self._read_single(RBRACKET)
            elif ch == ",":
                yield self._read_single(COMMA)
            elif ch == ":":
                yield self._read_single(COLON)
            elif ch == '"':
                yield self._read_string()
            elif ch == "-" or ch.isdigit():
                yield self._read_number()
            elif self.text.startswith("true", self.pos):
                yield self._read_keyword(TRUE, "true")
            elif self.text.startswith("false", self.pos):
                yield self._read_keyword(FALSE, "false")
            elif self.text.startswith("null", self.pos):
                yield self._read_keyword(NULL, "null")
            else:
                raise MjsonError(f"非法字符 {ch!r}", self.line, self.column, self.text)

        yield self._make(EOF, None, self.line, self.column)
