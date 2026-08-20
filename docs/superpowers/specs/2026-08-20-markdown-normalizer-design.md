# Markdown GitHub Normalizer Design

## Goal

Keep authoring comfortable in Typora/ChatGPT while automatically producing Markdown that GitHub renders reliably, without Pages, Releases, or Packages.

## Core model

The tool separates **normalization** from **write mode**:

- `copy`: keep `name.md`, write normalized `name-github.md` beside it.
- `replace`: normalize `name.md` in place.
- `auto`: resolve mode from the commit marker, then per-file config, then repository default.

Mode precedence:

1. Explicit Action/CLI mode (`copy` or `replace`).
2. Commit marker `[md:copy]` or `[md:replace]`.
3. First matching per-file rule in `.markdown-github-normalizer.toml`.
4. `default_mode`, which defaults to `copy`.

Generated `*-github.md` files are never treated as inputs.

## Normalization scope for v1

The first version targets concrete failures observed in Typora/GPT -> GitHub workflows:

- Convert standalone `\[ ... \]` display math to GitHub `$$ ... $$` blocks.
- Convert inline `\( ... \)` math to `$...$`, while leaving inline code untouched.
- Ensure top-level `$$` display blocks are separated from surrounding prose by blank lines.
- In ordinary prose, turn a single source newline between two plain text lines into a paragraph break. This reflects Typora rich-editor authoring: such a newline is treated as intended visual separation, not source-code line wrapping.
- Do not inject paragraph breaks inside fenced code, display math, lists, tables, blockquotes, headings, HTML-like blocks, or other obvious Markdown containers.

The normalizer must be idempotent: running it twice produces the same text.

## GitHub integration

A composite `action.yml` runs the bundled Python normalizer in the caller repository. With no explicit file list it processes Markdown changed by the triggering commit. It commits generated/normalized output using `github-actions[bot]` when there are changes.

Consumer workflows should skip runs triggered by `github-actions[bot]` to avoid normalization loops. Manual `workflow_dispatch` can pass `mode` and `files` explicitly.

## Configuration

Optional `.markdown-github-normalizer.toml`:

```toml
default_mode = "copy"

[[rules]]
pattern = "README.md"
mode = "replace"

[[rules]]
pattern = "docs/generated/*.md"
mode = "replace"
```

Patterns use shell-style glob matching.
