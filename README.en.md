# markdown-github-normalizer

[中文](README.md) | **English**

*Translation by GPT-5.6 Sol.*

Have you ever written a document locally in Typora, pushed it, and then found the formula formatting turned into a mess because of **spaces and line breaks**?

Have you ever had GPT submit files automatically, only for formulas to become a mess because it **overuses LaTeX parenthesis/bracket syntax**?

This repository's **GitHub Action** is here to **stop Markdown from becoming unrecognizable on GitHub**!

## See It in Action

If you just want to see how it handles these problems, you do not need to experiment on your own repository first. Clone this repository and run the following command from the repository root:

```bash
python -m src.mdgithub_normalizer.cli demo/input.en.md --mode copy --repo-root .
```

It will generate `demo/input.en-github.md` locally. Just compare the two files.

`demo/input.en.md` contains examples of every problem this repository currently targets, so it gives a very direct reference for the effect~

## Usage

Run this in the Git repository where you want to enable it. Python is recommended:

```bash
python -c "from urllib.request import urlopen; exec(urlopen('https://raw.githubusercontent.com/leo-grayrat/markdown-github-normalizer/main/install.py').read().decode())"
```

After installation, commit and push as usual. Markdown updates will be processed automatically.

Alternative installation methods:

```powershell
irm https://raw.githubusercontent.com/leo-grayrat/markdown-github-normalizer/main/install.ps1 | iex
```

```bash
curl -fsSL https://raw.githubusercontent.com/leo-grayrat/markdown-github-normalizer/main/install.sh | bash
```

## Processing Modes

- **copy**: Keep the original file and generate `filename-github.md`. Suitable for documents written in Typora when you still want to keep the original draft.
- **replace**: Modify the original file directly. Suitable for README files, repository documentation, and Markdown generated directly by GPT / Codex.

The default is `copy`.

You can temporarily specify the mode for a particular commit:

```text
docs: update roadmap [md:copy]
docs: add explanation [md:replace]
```

For long-term rules, create `.markdown-github-normalizer.toml` in the target repository:

```toml
default_mode = "copy"

[[rules]]
pattern = "README.md"
mode = "replace"

[[rules]]
pattern = "docs/generated/*.md"
mode = "replace"
```

## Currently Handled

- Convert `\[ ... \]` and `$$ ... $$` display math into fenced `math` blocks;
- Convert ordinary `$...$` and `\( ... \)` inline math into GitHub protected inline math;
- Fix formula compatibility problems we have actually encountered: `\cross`, `\_{...}`, `\operatorname{...}`, `\,`, and `\;`;
- Add necessary boundary spaces when inline math or bold text is stuck directly to surrounding prose, and fix clear bold-spacing problems such as `**123 **`;
- Turn single line breaks in Typora prose into paragraph-separating blank lines.

## Prompt for LLMs

If you want GPT, Codex, or another model to use this project when modifying Markdown, you can add the following text to a system prompt, `AGENTS.md`, or another long-term agent configuration:

```text
This repository uses markdown-github-normalizer to handle Markdown compatibility issues on GitHub. When modifying Markdown, write normally and let the workflow process it after the commit.
If the original file should be replaced directly, add [md:replace] to the commit message; if the original should be preserved and a GitHub version generated, add [md:copy].
```

## Why This Project Exists

I usually write Markdown in Typora, and I also often let GPT or Codex generate or modify Markdown directly.

When writing in Typora's rich-text interface, we are not constantly staring at the Markdown source. For example, if a paragraph is missing one blank line after it, it may not look obviously wrong in Typora (and I even used this deliberately before to create tighter line spacing); after pushing to GitHub, two paragraphs that were meant to be separate may instead get joined together:

```markdown
First paragraph Second paragraph
```

Formulas have similar problems. GPT often likes to write formulas like this:

```markdown
\[
E = mc^2
\]

\(x+y\)
```

But GitHub Markdown does not use `\[ ... \]` for display math or parentheses/brackets for inline math; it only recognizes (single/double) dollar signs.

GPT also often generates:

```markdown
D\_{m\times n}
```

adding an unnecessary extra escape to `_` inside LaTeX formulas.

There are also tiny problems such as one missing blank line or space between prose and a formula:

```markdown
Therefore we get$\implies$
$$
x = y + 1
$$
```

This can make the rendered result completely fall apart…

These problems are often only one space, one line break, or one formula delimiter away from being correct. Fixing any one of them is easy, but repeatedly checking and repairing them is annoying.

`markdown-github-normalizer` exists to automatically handle these small differences between Typora, AI-generated Markdown, and GitHub Markdown\~

---

## But Then We Found More and More Problems

However, things turned out to be more complicated than we expected…

| Problem actually encountered | Cause / example |
| --- | --- |
| A standalone `=` line inside `$$ ... $$` gets parsed by Markdown as a heading structure | `=` is treated as setext heading syntax and turns into an H1 |
| After a blank line inside `$$ ... $$`, a line starting with `+` can be parsed as a Markdown list | `+` gets treated as ordinary Markdown syntax |
| A blank line by itself inside `$$ ... $$` may also make the whole formula fail to render | Same underlying problem: the content is not being isolated as one formula block, so ordinary Markdown parsing interferes; blank lines strike again |
| Valid LaTeX spacing commands such as `\;` and `\,` render merely as escaped `;` and `,` characters | ? (a classic GitHub moment; I do not know why this has to be forbidden) |
| GitHub blocks some LaTeX macros often written by AI, such as `\operatorname{vec}` | GitHub does not allow users to “freely extend macros” because macros can involve injection and similar risks, even though this is just a syntax-extension macro |
| Some symbols simply do not render (especially ones improvised by hand) | For example, using `\cross` for multiplication does not work; it has to be `\times` |
| AI unnecessarily escapes LaTeX subscripts | For example, `D\_{m\times n}` |
| A space mixed inside the closing bold delimiter can break bold formatting | `**123 **`: the bold delimiter has to bind toward adjacent valid characters; otherwise who knows whether it should match forward or backward? |
| Bold text ending in punctuation and immediately followed by prose may fail to close properly | `**Conclusion:**text` — and yes, special characters can cause trouble too; AI can easily produce this kind of thing |
| A normal single newline in Typora prose gets merged into the same paragraph on GitHub | It is treated like a continuation; rich-text Typora obviously has no need for that source-code wrapping behavior |
| Prose stuck directly to an inline-math `$` delimiter may stop the formula from rendering | Similar to the bold problem |
| A `$$` block formula without blank-line separation from surrounding prose may fail to render | Same idea |

### Follow-up Strategy

We can now confirm that GitHub's `$$ ... $$` does not reliably isolate its contents from Markdown block parsing, while ` ```math ... ``` ` is a real fenced formula **block**. We have actually tested the same formula containing blank lines: it failed with `$$`, but rendered correctly after switching to ` ```math `. Therefore, display math is normalized to the latter whenever possible.

Other formatting problems are also handled with deliberately simple rules:

- **Separate inline structures with spaces.** For example, when inline math or bold text is directly attached to surrounding prose, add spaces at the structure boundaries.
- **Separate block structures with blank lines.** For example, ensure blank lines between prose and display math.
- For clear internal-spacing errors such as `**123 **`, move the space outside the bold range.
- For punctuation cases such as `**Conclusion:**text`, add a space after the closing `**`.
- For problems such as `\operatorname`, `\cross`, and `\_{...}`, only handle formula forms that we have actually encountered and can rewrite unambiguously.

> We originally wanted to keep the script from becoming too miscellaneous, and:
>
> - AI tends to make one set of mistakes (parentheses and `\\[`, macros, excessive escaping)
> - humans tend to make another set of mistakes (missing spaces, missing line breaks, improvised symbols)
>
> These do not overlap much,
>
> ~~so the implementation would distinguish Markdown written manually in Typora from Markdown generated directly by AI.~~
>
> ~~Manual writing would be the default, while AI commits would be specially marked to trigger the AI case.~~
>
> re: After actually implementing it, we found that these specific rules are simple enough to handle in the script. Running them together does not make the tool bloated, so the source distinction was removed.
