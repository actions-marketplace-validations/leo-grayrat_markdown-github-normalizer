import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("action_runtime", ROOT / "scripts" / "action.py")
action_runtime = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(action_runtime)


class ActionRuntimeTests(unittest.TestCase):
    def test_discovers_markdown_changed_since_before_and_ignores_generated(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
            (repo / "notes.md").write_text("a\n", encoding="utf-8")
            subprocess.run(["git", "add", "notes.md"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", "first"], cwd=repo, check=True, capture_output=True)
            before = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=repo, text=True, capture_output=True, check=True
            ).stdout.strip()

            (repo / "notes.md").write_text("a\nb\n", encoding="utf-8")
            (repo / "notes-github.md").write_text("generated\n", encoding="utf-8")
            (repo / "data.txt").write_text("x\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", "second"], cwd=repo, check=True, capture_output=True)

            paths = action_runtime.discover_changed_paths(repo, before)
            markdown = action_runtime.markdown_paths(repo, paths)
            self.assertEqual(markdown, [Path("notes.md")])


if __name__ == "__main__":
    unittest.main()
