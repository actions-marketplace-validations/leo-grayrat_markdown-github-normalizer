# markdown-github-normalizer
你是否苦恼在本地 Typora 写了文档推送之后，会发现被空格和换行搞得公式格式一坨？你是否发现 GPT 自动提交文件后，因为滥用 LaTeX 括号语法而让公式也变成一坨？  这个仓库的 GitHub Action 就来解决这个痛点

## 使用

在目标仓库新建 `.github/workflows/normalize-markdown.yml`：

```yaml
name: Normalize Markdown

on:
  push:
    paths: ['**/*.md', '**/*.markdown']

permissions:
  contents: write

jobs:
  normalize:
    uses: leo-grayrat/markdown-github-normalizer/.github/workflows/normalize.yml@main
```

之后 Markdown 更新并 push 时会自动处理。

## 处理方式

- **copy**：保留原文件，生成 `文件名-github.md`。适合从 Typora 编写、还想保留原稿的文档。
- **replace**：直接修改原文件。适合 README、仓库说明，以及 GPT / Codex 直接生成的 Markdown。

默认使用 `copy`。

某次提交可以临时指定：

```text
docs: update roadmap [md:copy]
docs: add explanation [md:replace]
```

需要长期规则时，可在目标仓库创建 `.markdown-github-normalizer.toml`：

```toml
default_mode = "copy"

[[rules]]
pattern = "README.md"
mode = "replace"

[[rules]]
pattern = "docs/generated/*.md"
mode = "replace"
```

## 目前处理

- `\[ ... \]` 块公式转换为 GitHub 块公式；
- `\( ... \)` 行内公式转换为 GitHub 行内公式；
- 补齐 `$$` 公式块周围的空行；
- 将 Typora 正文中的单换行补成段落空行；
- 保持列表、表格、引用、代码块和公式内部结构。
