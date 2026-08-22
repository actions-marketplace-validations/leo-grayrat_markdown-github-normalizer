# markdown-github-normalizer

**中文** | [English](README.en.md)

**[在 GitHub Marketplace 上查看详情](https://github.com/marketplace/actions/markdown-github-normalizer)** 

你是否苦恼在本地 Typora 写了文档推送之后，会发现被**空格和换行**搞得公式格式一坨？

你是否发现 GPT 自动提交文件后，因为**滥用 LaTeX 括号语法**而让公式也变成一坨？

这个仓库的 **GitHub Action** 就来**解决 Markdown 在 GitHub 上面目全非**的痛点！

## 先看看效果

如果只是想看看它会怎么处理这些问题，不需要先拿自己的仓库做实验。clone 本仓库后，在仓库根目录运行：

```bash
python -m src.mdgithub_normalizer.cli demo/input.md --mode copy --repo-root .
```

它会在本地生成 `demo/input-github.md`。直接对比两个文件即可。

`demo/input.md` 中有我们这个仓库针对的所有问题的例子，可以作为非常直观的效果参考~

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

- `\[ ... \]` 和 `$$ ... $$` 块公式转换为 fenced `math`；
- 普通 `$...$` 和 `\( ... \)` 行内公式转换为 GitHub 的 protected inline math；
- 修正已经实际遇到的公式兼容问题：`\cross`、`\_{...}`、`\operatorname{...}`、`\,`、`\;`、`\makebox`；
- 行内公式、加粗与正文粘连时补必要的边界空格，并修正 `**123 **` 这类明确的加粗空格问题；
- 将 Typora 正文中的单换行补成段落空行；

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

---

## 但是我们后面还发现了越来越多的问题

然而，事情比我们想象的更复杂……

| 实际遇到的问题                                            | 原因/例子                                             |
| -------------------------------------------------- | ------------------------------------------------- |
| `$$ ... $$` 内出现单独一行的 `=` 时，被 Markdown 抢先解析成标题结构    | 因为 `=` 被当作 setext 标题语法解析了，变成一级标题了                 |
| `$$ ... $$` 内出现空行后再以 `+` 等符号开头时，被 Markdown 当成列表    | 因为 `+` 被当作普通语法解析了                                   |
| `$$ ... $$` 内单纯出现空行，也可能导致整个公式无法渲染                  | 和上面一样，都是因为没有被当作一个公式块去解析，而是撞到了普通的格式，都是空行惹的祸（恼      |
| `\;` `\,` 等本身合法的 LaTeX 间距命令渲染成单纯的转义字符 `;`  `,`     | ？（GitHub 魅力时刻，我不知道为什么要禁止这个）                       |
| GitHub 会禁止部分 AI 常写的 `\operatorname{vec}` 类 LaTeX 宏 | GitHub 不允许用户“随便扩展宏”，因为宏可能有注入等风险，虽然这只是个语法拓展宏       |
| 单纯就是不渲染一些（AI 喜欢乱用的）LaTeX 高级命令                     | `makebox` 被 AI 天天拿来右对齐（注意这个不是画框的）                    |
| 单纯就是不渲染一些（人乱凑的）符号                                  | 例如用 `\cross` 表示乘号不行，得改用 `\times`                  |
| AI 对 LaTeX 下标进行多余转义                                | 例如 `D\_{m\times n}`                               |
| 加粗结束符内部混入空格时会导致加粗失效                                | `**123 **` 加粗符号会向粘连有效字符一侧生效，否则谁知道你是向后匹配还是向前匹配？    |
| 加粗内容以标点结束、后面又立刻连接正文时，`**` 无法正常闭合                   | `**结论：**正文` （接上文）哦对了，特殊符号也不行，例如这里的标点， AI 很容易犯这种问题 |
| Typora 中正常的正文单换行，到了 GitHub 并成同一段                   | 被认定为续航符了，显然富文本自动换行的 typora 并没有这种需求                |
| 正文与行内公式 `$` 符号粘在一起时无法渲染出公式                         | 类似加粗问题                                            |
| 块公式 `$$` 和正文不间隔空行时无法渲染出公式                          | 同上                                                |

### 后续修改方略

目前已经可以确定，GitHub 的 `$$ ... $$` 并不能可靠地把内部内容完全隔离于 Markdown 的块级解析；而 ` ```math ... ``` ` 是真正的公式**块**。已经实际测试过，同一段包含空行的公式使用 `$$` 无法渲染，改成 ` ```math ` 后即可正常显示，因此块公式统一优先转换为后者。

其他格式问题也尽量统一而简单地处理：

- **行内结构用空格隔离。** 例如正文与行内公式、加粗结构直接相连时，在结构边界补空格。
- **块级结构用空行隔离。** 例如正文与块公式之间保证有空行。
- 对 `**123 **` 这种明确的内部空格错误，将空格移到加粗范围之外。
- 对 `**结论：**正文` 这种标点情况，在闭合的 `**` 后补空格。
- 对 `\operatorname`、`\cross`、`\_{...}` 等问题，只处理已经实际遇到、能够明确判断的公式写法。

> 为了不把脚本做的太杂，而且：
>
> - AI 犯的问题（喜欢括号和\\[，喜欢宏，喜欢转义） 
> - 人工犯的问题（缺空格，缺换行，乱凑符号）
>
> 不太重合，
> 
> ~~因此处理时会区分人工在 Typora 中编写和 AI 直接生成 Markdown 的情况。~~
>
> ~~默认按照人工编写处理，AI 提交时特别标注就可以触发 AI 情况。~~
>
> re：后来实际实现后发现这些特定规则在脚本里很简单就可以处理，统一执行也不会很臃肿，因此不再区分来源。

## 更新日志

- **2026-08-22**：新增 `\makebox` 兼容处理。GitHub 当前无法渲染 `\makebox`，因此将其降级为 `\mbox`，保留内部内容并移除宽度、对齐等参数；中英文 demo 同步加入示例。
