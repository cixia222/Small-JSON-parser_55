# 贡献指南（CONTRIBUTING.md）

感谢你对 Small-JSON-parser 的兴趣！欢迎 **star**、**watch**、提 **issue** 或提交 **PR**。

## 提 issue

提交 issue 前，请先搜索是否已有类似问题。报告 bug 时请尽量包含：

- 运行环境（Python 版本、操作系统）
- 复现步骤与输入
- 期望行为与实际行为

## 提交 PR 的流程

1. **Fork** 本仓库
2. 克隆到本地，安装开发依赖：`pip install -e ".[dev]"`
3. 创建功能分支：`git checkout -b feature/你的功能`
4. 编写代码并补充测试，运行 `pytest` 确保全部通过
5. 提交并推送：`git push origin feature/你的功能`
6. 发起 Pull Request，描述改动内容

## 分支命名规范

| 前缀 | 用途 | 示例 |
|---|---|---|
| `feature/` | 新功能 | `feature/cli` |
| `fix/` | 修复 bug | `fix/number-leading-zero` |
| `docs/` | 文档 | `docs/readme` |

## 提交信息规范

采用[约定式提交](https://www.conventionalcommits.org/zh-hans/)：

```
feat: 添加 dumps 序列化
fix: 修复数字前导零报错
docs: 补充 README 使用示例
test: 增加非法 JSON 测试用例
```

## 代码风格

- 遵循 [PEP 8](https://peps.python.org/pep-0008/)
- 注释使用中文，方便初学者阅读（这是本项目"可读性优先"的定位）
- 新增功能尽量配合同名测试文件
