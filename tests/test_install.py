import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL_PY = ROOT / "install.py"
INSTALL_SH = ROOT / "install.sh"
BASH_AVAILABLE = os.name != "nt" and shutil.which("bash") is not None
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

    def test_install_py_handles_non_utf8_stdout_with_bilingual_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "cp1252"

            result = subprocess.run(
                [sys.executable, str(INSTALL_PY)], cwd=repo, capture_output=True, env=env
            )

            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
            stdout = result.stdout.decode("utf-8")
            self.assertIn("已安装", stdout)
            self.assertIn("Installed", stdout)

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
                [sys.executable, str(INSTALL_PY)],
                cwd=tmp,
                text=True,
                encoding="utf-8",
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("请在 Git 仓库中运行此命令。", result.stderr)
            self.assertIn("Run this command inside a Git repository.", result.stderr)

    @unittest.skipUnless(BASH_AVAILABLE, "Bash installer is tested only on Unix-like runners")
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

    @unittest.skipUnless(BASH_AVAILABLE, "Bash installer is tested only on Unix-like runners")
    def test_install_sh_replaces_existing_installer_workflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            workflow = repo / ".github" / "workflows" / "normalize-markdown.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text("old\n", encoding="utf-8")

            subprocess.run(["bash", str(INSTALL_SH)], cwd=repo, check=True)

            self.assertEqual(workflow.read_text(encoding="utf-8"), EXPECTED)

    @unittest.skipUnless(BASH_AVAILABLE, "Bash installer is tested only on Unix-like runners")
    def test_install_sh_rejects_non_git_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["bash", str(INSTALL_SH)], cwd=tmp, text=True, capture_output=True
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Git", result.stderr)


if __name__ == "__main__":
    unittest.main()
