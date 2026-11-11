"""命令行入口。

用法示例::

    mjson parse data.json              # 解析并打印 Python 结构
    mjson parse data.json --trace      # 打印词法 + 语法分析全过程
    mjson validate data.json           # 只检查合法性
    mjson format data.json             # 格式化（美化）输出
    mjson format data.json --indent 4
"""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .errors import MjsonError
from .parser import loads
from .serializer import dumps


def _read_source(path: str) -> str:
    """从文件读取文本；路径为 '-' 时从标准输入读取。"""
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _load_or_die(text: str, trace: bool = False):
    """解析失败时打印人类可读错误并以非零状态码退出。"""
    try:
        return loads(text, trace=trace)
    except MjsonError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


def cmd_parse(args) -> int:
    text = _read_source(args.file)
    obj = _load_or_die(text, trace=args.trace)
    if not args.trace:
        print(obj)
    return 0


def cmd_validate(args) -> int:
    text = _read_source(args.file)
    _load_or_die(text)
    print("✓ JSON 合法")
    return 0


def cmd_format(args) -> int:
    text = _read_source(args.file)
    obj = _load_or_die(text)
    print(dumps(obj, indent=args.indent))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="mjson",
        description="一个为了让人读懂而写的 JSON 解析器（零依赖）",
    )
    parser.add_argument("--version", action="version", version=f"mjson {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_parse = sub.add_parser("parse", help="解析 JSON 并打印 Python 结构")
    p_parse.add_argument("file", help="JSON 文件路径；'-' 表示从标准输入读取")
    p_parse.add_argument("--trace", action="store_true", help="打印词法与语法分析全过程")
    p_parse.set_defaults(func=cmd_parse)

    p_validate = sub.add_parser("validate", help="检查 JSON 是否合法")
    p_validate.add_argument("file", help="JSON 文件路径；'-' 表示从标准输入读取")
    p_validate.set_defaults(func=cmd_validate)

    p_format = sub.add_parser("format", help="格式化 JSON 输出")
    p_format.add_argument("file", help="JSON 文件路径；'-' 表示从标准输入读取")
    p_format.add_argument("--indent", type=int, default=2, help="缩进空格数（默认 2）")
    p_format.set_defaults(func=cmd_format)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
