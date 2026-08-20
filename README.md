# markdown-github-normalizer
你是否苦恼在本地 Typora 写了文档推送之后，会发现被空格和换行搞得公式格式一坨？你是否发现 GPT 自动提交文件后，因为滥用 LaTeX 括号语法而让公式也变成一坨？  这个仓库的 GitHub Action 就来解决这个痛点

## 使用

在需要启用的 Git 仓库中运行，推荐直接用 Python：

```bash
python -c "from urllib.request import urlopen; exec(urlopen('https://raw.githubusercontent.com/leo-grayrat/markdown-github-normalizer/main/install.py').read().decode())"
```

安装后正常提交、push 即可，Markdown 更新时会自动处理。

备用安装方式：

```powershell
irm https://raw.githubusercontent.com/leo-grayrat/markdown-github-normalizer/main/install.ps1 | iex
```

```bash
curl -fsSL https://raw.githubusercontent.com/leo-grayrat/markdown-github-normalizer/main/install.sh | bash
```

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

## 给大模型的提示词

如果希望 GPT、Codex 等在修改 Markdown 时使用本项目，可以把下面这段加入系统提示词、`AGENTS.md` 或其他长期 Agent 配置中：

```text
本仓库使用 markdown-github-normalizer 处理 Markdown 与 GitHub 的格式兼容问题。修改 Markdown 时正常编写即可；提交后交给该工作流处理。
需要直接覆盖原文件时，在 commit message 中加入 [md:replace]；需要保留原文件并生成 GitHub 版本时，加入 [md:copy]。
```

## 为什么会有这个项目

我平时主要用 Typora 写 Markdown，也经常让 GPT、Codex 直接生成或修改 Markdown。

在 Typora 的富文本界面里写东西时，我们不会一直盯着 Markdown 源码。例如一段话后面少打了一个空行，在 Typora 里看起来可能没有明显问题（甚至我之前有时专门用这种来创造短行间距）；推到 GitHub 后，原本想分开的两段却连在了一起：

```markdown
第一段 第二段
```

公式也有类似的问题。GPT 平常喜欢这样写公式：

```markdown
\[
E = mc^2
\]

\(x+y\)
```

但 GitHub 的 md 并不使用 `\[ ... \]` 行间公式 和 括号方括号行内公式，只认（双）美元符号。

GPT 还经常生成：

```markdown
D\_{m\times n}
```

把 LaTeX 公式里的 `_` 多转义了一层。

还有正文和公式之间少一个空行/空格这种很细小的问题：

```markdown
由此得到$\implies$
$$
x = y + 1
$$
```

这会导致渲染出来完全崩坏……

这些问题往往只差一个空格、一次换行，或者换一个公式分割符。这种工作单独修都不难，但反复检查和修改很麻烦。

`markdown-github-normalizer` 就是用来自动处理这些 Typora、AI 与 GitHub Markdown 之间的小差异的\~
