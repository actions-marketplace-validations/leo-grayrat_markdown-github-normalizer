# markdown-github-normalizer

你是否苦恼在本地 Typora 写了文档推送之后，会发现被空格和换行搞得公式格式一坨？你是否发现 GPT 自动提交文件后，因为滥用 LaTeX 括号语法而让公式也变成一坨？这个仓库的 GitHub Action 就来解决这个痛点。

它不要求你为了 GitHub 改变 Typora 写作习惯。Markdown 推送后，由 Action 自动整理为 GitHub 更稳定的写法。

## 两种处理方式

- **copy**：保留原文件，例如 `roadmap.md`，生成 `roadmap-github.md`。适合 Typora 长文、论文笔记等仍想保留原稿的内容。
- **replace**：直接清理原文件。适合 README、面向 GitHub 的说明文档，以及 GPT / Codex 直接生成的 Markdown。
- **auto**：按下面的优先级自动决定：本次明确参数 → commit message → 文件规则 → 仓库默认值。

默认模式是 `copy`。生成的 `*-github.md` 不会再次被处理。

## 第一版会修什么

目前只处理已经实际遇到、规则比较明确的问题：

- `\[ ... \]` 块公式改为 GitHub 可识别的 `$$ ... $$`；
- `\( ... \)` 行内公式改为 `$...$`，不会动行内代码；
- 给顶层 `$$` 公式块补齐必要空行；
- Typora 普通正文中只有一次换行时，补成段落空行；
- 不在代码块、公式块、列表、表格、引用等结构内部乱插空行。

## 在其他仓库启用

把 [`examples/normalize-markdown.yml`](examples/normalize-markdown.yml) 复制到目标仓库的：

```text
.github/workflows/normalize-markdown.yml
```

它会在 Markdown push 后自动运行，并把转换结果以 `github-actions[bot]` 的新 commit 写回仓库。

目标仓库需要允许 workflow 写入内容；示例 workflow 已声明：

```yaml
permissions:
  contents: write
```

## 配置 copy / replace

目标仓库可选创建 `.markdown-github-normalizer.toml`：

```toml
default_mode = "copy"

[[rules]]
pattern = "README.md"
mode = "replace"

[[rules]]
pattern = "docs/generated/*.md"
mode = "replace"
```

不创建配置文件时，默认全部 `copy`。

## 单次临时指定

commit message 可以覆盖配置：

```text
docs: update roadmap [md:copy]
```

或：

```text
docs: add generated explanation [md:replace]
```

也可以进入 GitHub 的 **Actions → Normalize Markdown → Run workflow**，手动选择 `auto / copy / replace`，并填写需要处理的文件。

## 本地运行

无需第三方 Python 依赖：

```bash
PYTHONPATH=src python -m mdgithub_normalizer --mode copy roadmap.md
```

或：

```bash
PYTHONPATH=src python -m mdgithub_normalizer --mode replace README.md
```

## 测试

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```
