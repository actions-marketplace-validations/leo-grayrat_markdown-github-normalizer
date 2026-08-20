import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL_PY = ROOT / "install.py"
INSTALL_SH = ROOT / "install.sh"
EXPECTED = """name: Normalize Markdown

on:
  push:
    paths: ['**/*.md', '**/*.markdown']

permissions:
  contents: write

jobs:
  normalize:
    uses: leo-grayrat/markdown-github-normalizer/.github/workflows/normalize.yml@main
"""


class InstallScriptTests(unittest.TestCase):
    def test_install_py_writes_caller_workflow_at_repo_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            nested = repo / "docs" / "notes"
            nested.mkdir(parents=True)

            result = subprocess.run(
                [sys.executable, str(INSTALL_PY)], cwd=nested, text=True, capture_output=True
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            workflow = repo / ".github" / "workflows" / "normalize-markdown.yml"
            self.assertEqual(workflow.read_text(encoding="utf-8"), EXPECTED)
            self.assertFalse((nested / ".github").exists())

    def test_install_py_replaces_existing_installer_workflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            workflow = repo / ".github" / "workflows" / "normalize-markdown.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text("old\n", encoding="utf-8")

            subprocess.run([sys.executable, str(INSTALL_PY)], cwd=repo, check=True)

            self.assertEqual(workflow.read_text(encoding="utf-8"), EXPECTED)

    def test_install_py_rejects_non_git_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(INSTALL_PY)], cwd=tmp, text=True, capture_output=True
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Git", result.stderr)

    @unittest.skipUnless(shutil.which("bash"), "bash is not available")
    def test_install_sh_writes_caller_workflow_in_current_git_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)

            result = subprocess.run(
                ["bash", str(INSTALL_SH)], cwd=repo, text=True, capture_output=True
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            workflow = repo / ".github" / "workflows" / "normalize-markdown.yml"
            self.assertEqual(workflow.read_text(encoding="utf-8"), EXPECTED)

    @unittest.skipUnless(shutil.which("bash"), "bash is not available")
    def test_install_sh_replaces_existing_installer_workflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            workflow = repo / ".github" / "workflows" / "normalize-markdown.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text("old\n", encoding="utf-8")

            subprocess.run(["bash", str(INSTALL_SH)], cwd=repo, check=True)

            self.assertEqual(workflow.read_text(encoding="utf-8"), EXPECTED)

    @unittest.skipUnless(shutil.which("bash"), "bash is not available")
    def test_install_sh_rejects_non_git_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["bash", str(INSTALL_SH)], cwd=tmp, text=True, capture_output=True
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Git", result.stderr)


if __name__ == "__main__":
    unittest.main()
