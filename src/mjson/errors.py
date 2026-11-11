"""错误类型与报错上下文定位。

这个模块定义了解析过程中抛出的异常。和其它 JSON 库最大的不同在于：
报错时会精确定位到出错的行、列，并打印出出错那一行，用 ``^`` 标出具体位置。

示例::

    >>> from mjson import loads
    >>> try:
    ...     loads('{\\n  "a": 1,\\n  "b": oops\\n}')
    ... except Exception as e:
    ...     print(e)
    解析错误: 第 3 行 第 8 列: 非法字符 'o'
      3 |   "b": oops
        |        ^
"""

from __future__ import annotations


class MjsonError(Exception):
    """JSON 解析过程中抛出的错误基类。

    属性:
        message: 错误描述文字。
        line: 出错位置所在行（从 1 开始）。
        column: 出错位置所在列（从 1 开始）。
        source: 原始输入文本，用于打印上下文。
    """

    def __init__(self, message: str, line: int, column: int, source: str | None = None):
        self.message = message
        self.line = line
        self.column = column
        self.source = source
        super().__init__(self.format())

    def format(self) -> str:
        """把错误格式化成一串带上下文的人类可读信息。"""
        head = f"解析错误: 第 {self.line} 行 第 {self.column} 列: {self.message}"
        if self.source is None:
            return head

        lines = self.source.splitlines()
        if not (1 <= self.line <= len(lines)):
            return head

        bad_line = lines[self.line - 1]
        prefix = f"{self.line:>3} | "
        caret = " " * (len(prefix) + self.column - 1) + "^"
        return f"{head}\n{prefix}{bad_line}\n{caret}"
