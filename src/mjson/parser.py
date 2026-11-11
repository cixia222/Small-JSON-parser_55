"""语法分析（Parser）：把 token 序列拼装成 Python 数据结构。

词法分析把文本切成 token，语法分析则按 JSON 的语法规则，
用"递归下降"的方式把这些 token 组合成嵌套的 dict / list / 标量。

递归下降的思想很直观：

* 每个语法结构对应一个函数（parse_object / parse_array / parse_value）；
* 函数之间互相调用，天然形成嵌套结构；
* 遇到不认识的 token，立刻抛出错，并带上精确的行列号。
"""

from __future__ import annotations

from . import tokenizer as tk
from .errors import MjsonError

# token 类型的可读名称，用于报错信息
_TOKEN_NAMES = {
    tk.LBRACE: "'{'",
    tk.RBRACE: "'}'",
    tk.LBRACKET: "'['",
    tk.RBRACKET: "']'",
    tk.COMMA: "','",
    tk.COLON: "':'",
    tk.STRING: "字符串",
    tk.NUMBER: "数字",
    tk.TRUE: "true",
    tk.FALSE: "false",
    tk.NULL: "null",
    tk.EOF: "输入结尾",
}


class Parser:
    """递归下降解析器。"""

    def __init__(self, tokens: list, source: str, trace: bool = False):
        self.tokens = tokens
        self.source = source
        self.trace = trace
        self.index = 0
        self._depth = 0

    # ---------- token 操作 ----------

    def _peek(self):
        return self.tokens[self.index]

    def _advance(self):
        tok = self.tokens[self.index]
        self.index += 1
        return tok

    def _expect(self, type_: str):
        """当前 token 必须是 type_ 类型，否则报错；成功则消费并返回它。"""
        tok = self._peek()
        if tok.type != type_:
            raise MjsonError(
                f"期望 {_describe_type(type_)}，却遇到了 {_describe_token(tok)}",
                tok.line, tok.column, self.source,
            )
        return self._advance()

    # ---------- trace 辅助 ----------

    def _trace_enter(self, name: str, tok):
        if not self.trace:
            return
        indent = "  " * self._depth
        print(f"{indent}→ {name}  (第 {tok.line} 行, 遇到 {tok.type})")
        self._depth += 1

    def _trace_leave(self, name: str, value):
        if not self.trace:
            return
        self._depth -= 1
        indent = "  " * self._depth
        print(f"{indent}← {name} -> {_repr_value(value)}")

    # ---------- 各语法结构 ----------

    def parse(self):
        """解析整个输入，返回对应的 Python 对象。"""
        first = self._peek()
        if first.type == tk.EOF:
            raise MjsonError("输入为空，期望一个 JSON 值", first.line, first.column, self.source)

        value = self._parse_value()

        # 解析完必须到达 EOF，否则说明后面有多余内容
        tail = self._peek()
        if tail.type != tk.EOF:
            raise MjsonError("值之后存在多余的内容", tail.line, tail.column, self.source)
        return value

    def _parse_value(self):
        tok = self._peek()
        if tok.type == tk.LBRACE:
            return self._parse_object()
        if tok.type == tk.LBRACKET:
            return self._parse_array()
        if tok.type == tk.STRING:
            if self.trace:
                print(f"{'  ' * self._depth}· 字符串 {tok.value!r}")
            self._advance()
            return tok.value
        if tok.type == tk.NUMBER:
            if self.trace:
                print(f"{'  ' * self._depth}· 数字 {tok.value}")
            self._advance()
            return _parse_number(tok.value)
        if tok.type == tk.TRUE:
            self._advance()
            return True
        if tok.type == tk.FALSE:
            self._advance()
            return False
        if tok.type == tk.NULL:
            self._advance()
            return None
        raise MjsonError(
            f"期望一个值，却遇到了 {_describe_token(tok)}", tok.line, tok.column, self.source
        )

    def _parse_object(self):
        self._trace_enter("parse_object", self._peek())
        self._expect(tk.LBRACE)
        obj = {}

        if self._peek().type == tk.RBRACE:
            self._advance()
            self._trace_leave("parse_object", obj)
            return obj

        while True:
            key_tok = self._expect(tk.STRING)
            self._expect(tk.COLON)
            value = self._parse_value()
            obj[key_tok.value] = value  # 同名键后者覆盖前者（与标准库一致）

            sep = self._peek()
            if sep.type == tk.COMMA:
                self._advance()
                continue
            if sep.type == tk.RBRACE:
                self._advance()
                break
            raise MjsonError(
                f"对象里期望 ',' 或 '}}'，却遇到了 {_describe_token(sep)}",
                sep.line, sep.column, self.source,
            )

        self._trace_leave("parse_object", obj)
        return obj

    def _parse_array(self):
        self._trace_enter("parse_array", self._peek())
        self._expect(tk.LBRACKET)
        arr = []

        if self._peek().type == tk.RBRACKET:
            self._advance()
            self._trace_leave("parse_array", arr)
            return arr

        while True:
            arr.append(self._parse_value())
            sep = self._peek()
            if sep.type == tk.COMMA:
                self._advance()
                continue
            if sep.type == tk.RBRACKET:
                self._advance()
                break
            raise MjsonError(
                f"数组里期望 ',' 或 ']'，却遇到了 {_describe_token(sep)}",
                sep.line, sep.column, self.source,
            )

        self._trace_leave("parse_array", arr)
        return arr


# ---------- 模块级辅助 ----------

def _parse_number(raw: str):
    """把数字字符串转成 int 或 float。整数优先用 int，含小数点/指数用 float。"""
    if any(c in raw for c in ".eE"):
        return float(raw)
    return int(raw)


def _describe_token(tok) -> str:
    if tok.type == tk.STRING:
        return f"字符串 {tok.value!r}"
    if tok.type == tk.NUMBER:
        return f"数字 {tok.value}"
    return _TOKEN_NAMES.get(tok.type, tok.type)


def _describe_type(type_: str) -> str:
    return _TOKEN_NAMES.get(type_, type_)


def _repr_value(value) -> str:
    """trace 时用于简短展示结果，避免打印超长对象。"""
    s = repr(value)
    return s if len(s) <= 60 else s[:57] + "..."


def loads(text: str, *, trace: bool = False):
    """把 JSON 文本解析为 Python 对象。

    参数:
        text: JSON 文本。
        trace: 为 True 时，打印词法分析与语法分析的每一步过程。
    """
    tokens = list(tk.Tokenizer(text).tokenize())

    if trace:
        print("== 词法分析结果（token 流）==")
        for t in tokens:
            print(f"  {t}")
        print()

    return Parser(tokens, text, trace=trace).parse()


def load(fp, *, trace: bool = False):
    """从文件对象读取 JSON 并解析。"""
    return loads(fp.read(), trace=trace)
