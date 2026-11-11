# Small-JSON-parser —— 手写解析器


一个**为了让人读懂而写的 JSON 解析器**。

不调用 Python 标准库的 `json` 模块，纯手写词法分析（Tokenizer）与递归下降语法分析（Parser），零运行时依赖。它不追求最快，追求的是**最清晰**：每一行代码都带注释，报错能精确定位到行列并画出 `^`，还提供 `--trace` 教学模式把解析过程一步步打印出来。

> 🔗 仓库地址：https://github.com/cixia222/Small-JSON-parser_55

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

## ✨ 特性

- **零依赖**：不 import `json`，完全手写解析核心
- **完整往返**：`loads`（文本 → 对象）+ `dumps`（对象 → 文本）双向支持
- **精准报错**：非法 JSON 报出**行号、列号**，并用 `^` 标出出错字符
- **trace 教学模式**：一键打印 token 流与递归下降全过程，适合学习编译原理
- **命令行工具**：`parse` / `validate` / `format` 三个子命令，开箱即用
- **测试齐全**：覆盖合法 / 非法 / 边界用例，接 GitHub Actions 自动测试

## 🤔 为什么做这个

Python 自带 `json` 模块，又稳又快——所以这个项目的**目的不是替代它**，而是**展示"把文本变成结构化数据"这件编译器核心工作的原理**。做过它之后，你就能上手写"解析自定义配置格式""迷你脚本语言""公式计算器"这类东西。这是一个"造轮子以理解轮子"的教学项目。

## 📦 安装

```bash
# 开发模式安装（推荐，方便本地改代码立即生效）
git clone https://github.com/cixia222/Small-JSON-parser_55.git
cd Small-JSON-parser_55
pip install -e ".[dev]"
```

## 🚀 快速开始

### Python API

```python
from mjson import loads, dumps

# 解析：JSON 文本 -> Python 对象
obj = loads('{"name": "张三", "age": 20, "tags": ["json", "parser"]}')
print(obj)  # {'name': '张三', 'age': 20, 'tags': ['json', 'parser']}

# 序列化：Python 对象 -> JSON 文本
print(dumps(obj, indent=2))
# {
#   "name": "\u5f20\u4e09",
#   "age": 20,
#   "tags": ["json", "parser"]
# }
```

### 命令行

```bash
mjson parse examples/demo.json       # 解析并打印 Python 结构
mjson validate examples/demo.json    # 检查是否合法
mjson format examples/demo.json      # 格式化输出
mjson format examples/demo.json --indent 4
```

## 🎯 报错定位

普通解析器报错只说"哪里错了"，mjson 会**画出来**：

```bash
$ mjson validate bad.json
解析错误: 第 3 行 第 8 列: 非法字符 'o'
  3 |   "b": oops
        |        ^
```

## 🧭 trace 教学模式

加 `--trace`（或 API 里 `trace=True`），即可看到解析的**每一步**：

```bash
$ mjson parse data.json --trace
== 词法分析结果（token 流）==
  Token(LBRACE, None, 1:1)
  Token(STRING, 'a', 1:2)
  Token(COLON, None, 1:5)
  ...

→ parse_object  (第 1 行, 遇到 LBRACE)
  → parse_array  (第 1 行, 遇到 LBRACKET)
    · 数字 1
    · 数字 2
  ← parse_array -> [1, 2]
← parse_object -> {'a': [1, 2]}
```

## 📁 项目结构

```
Small-JSON-parser_55/
├── src/mjson/            # 源码
│   ├── __init__.py       # 对外 API
│   ├── tokenizer.py      # 词法分析
│   ├── parser.py         # 语法分析（递归下降）
│   ├── serializer.py     # 序列化（dumps）
│   ├── errors.py         # 错误类型 + 报错定位
│   └── cli.py            # 命令行入口
├── tests/                # pytest 测试
├── benchmark/            # 性能对比脚本
├── examples/             # 示例数据
├── DESIGN.md             # 设计文档
├── CONTRIBUTING.md       # 贡献指南
├── CHANGELOG.md          # 更新日志
├── GIT_WORKFLOW.md       # 分支管理工作流
├── ANALYSIS.md           # 五看三定战略分析
└── .github/workflows/    # CI 自动测试
```

## 🧪 测试

```bash
pytest
```

测试覆盖：各类 token、合法/非法 JSON、字符串转义、数字边界、错误行列号与 `^` 定位、序列化 round-trip、CLI 行为。

## ⚡ 性能对比

运行 `python benchmark/bench.py` 会对比标准库 `json`。诚实地说，mjson 更慢——因为它的定位是**可读性**而非速度：

```
标准库 json.loads : 0.1234 秒
mjson.loads        : 0.4567 秒
mjson 慢约        : 3.7 倍
```

## 📄 许可证

[MIT](./LICENSE)

## 🤝 贡献

欢迎提 issue、star、watch！详见 [CONTRIBUTING.md](./CONTRIBUTING.md)。
