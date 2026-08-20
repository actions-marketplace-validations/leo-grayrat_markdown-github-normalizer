import tempfile
import unittest
from pathlib import Path

from mdgithub_normalizer.policy import (
    is_generated_path,
    load_config,
    output_path_for_copy,
    resolve_mode,
)


class PolicyTests(unittest.TestCase):
    def test_default_mode_is_copy_without_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = load_config(Path(tmp) / ".markdown-github-normalizer.toml")
            self.assertEqual(resolve_mode(Path("notes.md"), config=config), "copy")

    def test_precedence_explicit_then_commit_then_rule_then_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".markdown-github-normalizer.toml"
            path.write_text(
                'default_mode = "copy"\n\n[[rules]]\npattern = "README.md"\nmode = "replace"\n',
                encoding="utf-8",
            )
            config = load_config(path)
            self.assertEqual(resolve_mode(Path("README.md"), config=config), "replace")
            self.assertEqual(
                resolve_mode(Path("README.md"), config=config, commit_message="x [md:copy]"),
                "copy",
            )
            self.assertEqual(
                resolve_mode(
                    Path("README.md"),
                    config=config,
                    commit_message="x [md:copy]",
                    explicit_mode="replace",
                ),
                "replace",
            )

    def test_copy_output_uses_github_suffix_and_generated_files_are_ignored(self):
        self.assertEqual(output_path_for_copy(Path("docs/notes.md")), Path("docs/notes-github.md"))
        self.assertTrue(is_generated_path(Path("docs/notes-github.md")))
        self.assertFalse(is_generated_path(Path("docs/notes.md")))


if __name__ == "__main__":
    unittest.main()
