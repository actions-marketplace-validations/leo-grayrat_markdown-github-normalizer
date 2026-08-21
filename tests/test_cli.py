import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from mdgithub_normalizer.cli import process_file


ROOT = Path(__file__).resolve().parents[1]


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
            self.assertTrue(result.output_path.samefile(generated))
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
            self.assertTrue(result.output_path.samefile(source))
            self.assertTrue(result.changed)

    def test_module_invocation_writes_copy_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "demo.md"
            source.write_text("第一行\n第二行\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "src.mdgithub_normalizer.cli",
                    str(source),
                    "--mode",
                    "copy",
                    "--repo-root",
                    str(root),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            generated = root / "demo-github.md"
            self.assertEqual(generated.read_text(encoding="utf-8"), "第一行\n\n第二行\n")
            self.assertIn("write:", result.stdout)

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
