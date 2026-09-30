import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("frontmatter.py")

GOAL = """---
title: Order redesign
type: implement
status: idea
tier:
stacks: [ios, android]
---

# Goal

status: this line is body text, not frontmatter
"""


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


class FrontmatterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.file = Path(self.tmp.name, "goal.md")
        self.file.write_text(GOAL, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_get_value(self):
        result = run("get", str(self.file), "status")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "idea\n")

    def test_get_strips_inline_comment(self):
        self.file.write_text(GOAL.replace("status: idea", "status: approved   # set by /spec"), encoding="utf-8")
        self.assertEqual(run("get", str(self.file), "status").stdout, "approved\n")

    def test_get_empty_value(self):
        result = run("get", str(self.file), "tier")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "\n")

    def test_get_missing_key_exits_4(self):
        result = run("get", str(self.file), "jira")
        self.assertEqual(result.returncode, 4)
        self.assertIn("MISSING KEY: jira", result.stderr)

    def test_set_existing_key_changes_only_that_line(self):
        self.assertEqual(run("set", str(self.file), "status", "specified").returncode, 0)
        self.assertEqual(self.file.read_text(encoding="utf-8"), GOAL.replace("status: idea", "status: specified"))

    def test_set_new_key_goes_before_closing_marker(self):
        self.assertEqual(run("set", str(self.file), "complexity", "high").returncode, 0)
        text = self.file.read_text(encoding="utf-8")
        self.assertIn("stacks: [ios, android]\ncomplexity: high\n---\n", text)
        self.assertEqual(run("get", str(self.file), "complexity").stdout, "high\n")

    def test_set_list_value(self):
        run("set", str(self.file), "repos", "[checkout, website-js]")
        self.assertEqual(run("get", str(self.file), "repos").stdout, "[checkout, website-js]\n")

    def test_no_frontmatter_exits_5(self):
        self.file.write_text("# Just a note\n", encoding="utf-8")
        self.assertEqual(run("get", str(self.file), "status").returncode, 5)
        self.assertEqual(run("set", str(self.file), "status", "idea").returncode, 5)

    def test_missing_file_exits_2(self):
        self.assertEqual(run("get", str(Path(self.tmp.name, "absent.md")), "status").returncode, 2)

    def test_bad_usage_exits_1(self):
        self.assertEqual(run("get", str(self.file)).returncode, 1)
        self.assertEqual(run("set", str(self.file), "status").returncode, 1)
        self.assertEqual(run("delete", str(self.file), "status").returncode, 1)


if __name__ == "__main__":
    unittest.main()
