import tempfile
import unittest
from pathlib import Path

from mdgithub_normalizer.cli import process_file


class CliTests(unittest.TestCase):
    def test_copy_mode_preserves_source_and_writes_normalized_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "notes.md"
            source.write_text("第一行\n第二行\n", encoding="utf-8")

            result = process_file(source, explicit_mode="copy", repo_root=root)

            self.assertEqual(source.read_text(encoding="utf-8"), "第一行\n第二行\n")
            generated = root / "notes-github.md"
            self.assertEqual(generated.read_text(encoding="utf-8"), "第一行\n\n第二行\n")
            self.assertEqual(result.output_path, generated)
            self.assertTrue(result.changed)

    def test_replace_mode_uses_unified_normalization(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "analysis.md"
            source.write_text(
                "第一行\n第二行\n\\[\n\\operatorname{vec}(D\\_{m}) \\cross x\n\\]\n",
                encoding="utf-8",
            )

            result = process_file(source, explicit_mode="replace", repo_root=root)

            self.assertEqual(
                source.read_text(encoding="utf-8"),
                "第一行\n\n第二行\n\n```math\n\\mathrm{vec}(D_{m}) \\times x\n```\n",
            )
            self.assertEqual(result.output_path, source)
            self.assertTrue(result.changed)

    def test_generated_file_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "notes-github.md"
            source.write_text("a\nb\n", encoding="utf-8")
            result = process_file(source, repo_root=root)
            self.assertTrue(result.skipped)
            self.assertFalse(result.changed)


if __name__ == "__main__":
    unittest.main()
