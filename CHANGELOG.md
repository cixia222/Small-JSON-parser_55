# 更新日志（CHANGELOG.md）

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 与[语义化版本](https://semver.org/lang/zh-CN/)。

## [0.1.0] - 2026-10-29

### 新增

- 手写词法分析器（`tokenizer.py`）：支持全部 JSON token 类型与行列号追踪
- 递归下降语法分析器（`parser.py`）：支持对象 / 数组 / 标量解析
- 序列化器（`serializer.py`）：支持紧凑与缩进两种输出，正确处理转义
- 报错上下文定位（行号 + 列号 + `^` 标注）
- trace 教学模式（打印 token 流与递归下降全过程）
- 命令行工具（`parse` / `validate` / `format`）
- pytest 测试套件（合法 / 非法 / 边界用例）
- GitHub Actions 自动测试
