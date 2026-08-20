import unittest

from mdgithub_normalizer.normalize import normalize_markdown


class NormalizeMarkdownTests(unittest.TestCase):
    def test_converts_bracket_display_math_and_adds_blank_lines(self):
        source = "前文\n\\[\nx_i = 1\n\\]\n后文\n"
        expected = "前文\n\n$$\nx_i = 1\n$$\n\n后文\n"
        self.assertEqual(normalize_markdown(source), expected)

    def test_converts_inline_parenthesis_math_but_not_inline_code(self):
        source = "这里有 \\(x_i+1\\) ，但 `\\(literal\\)` 不应变化。\n"
        expected = "这里有 $x_i+1$ ，但 `\\(literal\\)` 不应变化。\n"
        self.assertEqual(normalize_markdown(source), expected)

    def test_typora_single_newline_between_plain_lines_becomes_paragraph_break(self):
        source = "第一句话\n第二句话\n\n第三句话\n"
        expected = "第一句话\n\n第二句话\n\n第三句话\n"
        self.assertEqual(normalize_markdown(source), expected)

    def test_does_not_split_structured_markdown(self):
        source = (
            "- 第一项\n"
            "- 第二项\n\n"
            "| A | B |\n"
            "| - | - |\n"
            "| 1 | 2 |\n\n"
            "> 引用第一行\n"
            "> 引用第二行\n\n"
            "```text\n"
            "line one\n"
            "line two\n"
            "```\n"
        )
        self.assertEqual(normalize_markdown(source), source)

    def test_does_not_restructure_indented_math_inside_list(self):
        source = "1. 条目\n   $$\n   x=1\n   $$\n   继续说明\n"
        self.assertEqual(normalize_markdown(source), source)

    def test_preserves_multiline_math_content(self):
        source = "$$\n\\begin{aligned}\na &= b \\\\\nc &= d\n\\end{aligned}\n$$\n"
        self.assertEqual(normalize_markdown(source), source)

    def test_is_idempotent(self):
        source = "前文\n\\[\na=b\n\\]\n后文\n"
        once = normalize_markdown(source)
        self.assertEqual(normalize_markdown(once), once)


if __name__ == "__main__":
    unittest.main()
