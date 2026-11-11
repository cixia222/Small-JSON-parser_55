"""mjson —— 一个为了让人读懂而写的 JSON 解析器。

对外 API 与标准库 json 对齐（loads / load / dumps / dump），
但内部是纯手写的词法分析 + 递归下降解析，零依赖。

示例::

    >>> from mjson import loads, dumps
    >>> obj = loads('{"name": "张三", "age": 20}')
    >>> obj
    {'name': '张三', 'age': 20}
    >>> dumps(obj, indent=2)
    '{\\n  "name": "\\u5f20\\u4e09",\\n  "age": 20\\n}'
"""

from .errors import MjsonError
from .parser import load, loads
from .serializer import dump, dumps

__version__ = "0.1.0"

__all__ = ["loads", "load", "dumps", "dump", "MjsonError", "__version__"]
