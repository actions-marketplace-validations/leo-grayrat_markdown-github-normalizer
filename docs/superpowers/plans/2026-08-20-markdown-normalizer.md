# Markdown GitHub Normalizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a dependency-free Python Markdown normalizer with copy/replace policy and a reusable GitHub composite Action.

**Architecture:** A small Python package owns transformation and policy resolution. A CLI exposes it to local use and to a composite GitHub Action. The Action discovers changed Markdown, invokes the CLI, and commits only resulting changes.

**Tech Stack:** Python 3.11+ standard library, `unittest`, GitHub composite Actions, TOML via `tomllib`.

**Spec:** `docs/superpowers/specs/2026-08-20-markdown-normalizer-design.md`

## Global Constraints

- No Pages, Releases, or Packages in v1.
- Default write mode is `copy`.
- `*-github.md` is never normalized again.
- Explicit mode > commit marker > per-file rule > repository default.
- Normalization is idempotent.
- No third-party Python dependencies.

---

### Task 1: Normalization engine

**Files:**
- Create: `src/mdgithub_normalizer/normalize.py`
- Test: `tests/test_normalize.py`

**Interfaces:**
- Produces: `normalize_markdown(text: str) -> str`

- [ ] Write tests for math delimiter conversion, display-block spacing, Typora prose newlines, protected Markdown structures, inline-code preservation, and idempotence.
- [ ] Run `python -m unittest tests.test_normalize -v` and confirm failures because the module is absent.
- [ ] Implement the minimal line-state normalizer.
- [ ] Re-run the tests until green.

### Task 2: Policy and file output

**Files:**
- Create: `src/mdgithub_normalizer/policy.py`
- Create: `src/mdgithub_normalizer/cli.py`
- Create: `src/mdgithub_normalizer/__init__.py`
- Create: `src/mdgithub_normalizer/__main__.py`
- Test: `tests/test_policy.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Produces: `load_config(path)`, `resolve_mode(...)`, `output_path_for_copy(path)`, CLI `python -m mdgithub_normalizer`.

- [ ] Write failing tests for precedence, glob rules, generated-file exclusion, copy naming, and replace/copy writes.
- [ ] Run the policy/CLI tests and confirm failures.
- [ ] Implement policy and CLI minimally.
- [ ] Run the full test suite until green.

### Task 3: Reusable GitHub Action and documentation

**Files:**
- Create: `action.yml`
- Create: `scripts/action.py`
- Create: `examples/normalize-markdown.yml`
- Modify: `README.md`

**Interfaces:**
- Consumes: CLI from Task 2.
- Produces: Action inputs `mode`, `files`, `config` and automatic bot commit behavior.

- [ ] Add an action-runtime test fixture for changed-file discovery and bot-loop exclusion where practical.
- [ ] Add the composite Action and example caller workflow.
- [ ] Document copy/replace/auto behavior and installation in concise Chinese.
- [ ] Run all Python tests and shell syntax checks.
