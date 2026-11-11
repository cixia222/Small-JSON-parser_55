# 分支管理工作流（GIT_WORKFLOW.md）

本文档记录本项目的 Git 分支策略与完整操作流程，用于规范协作并满足"创建分支、合并分支、解决冲突"的实践要求。

## 1. 分支策略

采用轻量化 Git Flow：以 `main` 为稳定分支，每个功能在独立的 `feature/` 分支开发，完成后合并回 `main`。

```
main            ──●────────●────────●──→  稳定分支
                   \      /        /
feature/tokenizer ──●────          /       功能分支（合并后删除）
feature/parser       ────●────────/
```

## 2. 分支命名规范

| 前缀 | 用途 | 示例 |
|---|---|---|
| `feature/` | 新功能 | `feature/cli` |
| `fix/` | 修复 bug | `fix/number-leading-zero` |
| `docs/` | 文档 | `docs/readme` |

## 3. 完整操作流程

### 3.1 初始化与首次提交

```bash
git init
git add .
git commit -m "feat: 完成 Small-JSON-parser 首版（解析/dumps/CLI/报错定位/trace）"
git branch -M main
git remote add origin https://github.com/cixia222/Small-JSON-parser_55.git
git push -u origin main
```

### 3.2 创建分支并合并

```bash
git checkout -b feature/readme-a        # 创建分支
# ……修改代码……                        # 在分支上开发
git commit -am "docs: 修改 README 标题(A)"
git checkout main                       # 切回主分支
git merge feature/readme-a              # 合并分支
```

### 3.3 制造并解决冲突

```bash
git checkout -b feature/readme-b        # 第二个分支，改同一处
# ……把 README 标题改成不同内容……
git commit -am "docs: 修改 README 标题(B)"

git checkout main
git merge feature/readme-b              # 冲突发生！
# 打开冲突文件，会看到 <<<<<<< / ======= / >>>>>>> 标记，
# 手动保留正确内容后：
git add README.md
git commit -m "merge: 解决 README 标题冲突"
```

### 3.4 查看分支历史

```bash
git log --graph --oneline --all   # 命令行分支图
git branch -a                     # 查看所有分支
```

## 4. 常用命令速查

| 命令 | 作用 |
|---|---|
| `git checkout -b 分支名` | 创建并切换到新分支 |
| `git branch -d 分支名` | 删除已合并的分支 |
| `git merge 分支名` | 把分支合并到当前分支 |
| `git status` | 查看冲突与未提交状态 |
| `git log --graph --oneline --all` | 查看分支拓扑图 |
