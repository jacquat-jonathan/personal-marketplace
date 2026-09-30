import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("section.py")

HTML = """<!doctype html><html><head><style>p { color: red; }</style></head><body><main>
<section id="goal"><h2>Goal</h2><p>Ship <strong>it</strong>.</p></section>
<section id="acceptance-criteria"><h2>Acceptance criteria</h2><ol><li id="ac-1">Button shows</li><li id="ac-2">Error<br>message</li></ol></section>
<section id="plan"><h2>Plan</h2><div id="plan-ios"><h3>iOS</h3><div><p>inner</p></div><img src="x.png"><p>after nested</p></div></section>
<section id="scope"><h2>Scope</h2><table><tr><th>In</th><th>Out</th></tr><tr><td>A</td><td>B</td></tr></table></section>
</main></body></html>"""


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


class SectionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.file = Path(self.tmp.name, "spec.html")
        self.file.write_text(HTML, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_prints_only_requested_section(self):
        result = run(str(self.file), "goal")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "## goal\nGoal\nShip it.")

    def test_list_items_are_bulleted_and_br_breaks_lines(self):
        out = run(str(self.file), "acceptance-criteria").stdout
        self.assertIn("- Button shows", out)
        self.assertIn("- Error\nmessage", out)

    def test_nested_same_tag_and_void_elements_do_not_end_section_early(self):
        out = run(str(self.file), "plan-ios").stdout
        self.assertIn("inner", out)
        self.assertIn("after nested", out)
        self.assertNotIn("Scope", out)

    def test_nested_requested_ids_are_both_returned(self):
        result = run(str(self.file), "plan", "plan-ios")
        self.assertEqual(result.returncode, 0)
        self.assertIn("## plan\n", result.stdout)
        self.assertIn("## plan-ios\n", result.stdout)

    def test_table_rows_are_pipe_separated(self):
        out = run(str(self.file), "scope").stdout
        self.assertIn("| In | Out", out)
        self.assertIn("| A | B", out)

    def test_sections_print_in_request_order(self):
        out = run(str(self.file), "scope", "goal").stdout
        self.assertLess(out.index("## scope"), out.index("## goal"))

    def test_svg_is_summarised_not_dumped(self):
        html = '<section id="flows"><h2>Flows</h2><svg viewBox="0 0 10 10"><title>Call flow</title><text x="1">checkout</text><rect/></svg><p>after</p></section>'
        self.file.write_text(html, encoding="utf-8")
        out = run(str(self.file), "flows").stdout
        self.assertIn("[diagram: Call flow]", out)
        self.assertNotIn("checkout", out)
        self.assertIn("after", out)

    def test_missing_id_exits_3_and_still_prints_found(self):
        result = run(str(self.file), "goal", "nope")
        self.assertEqual(result.returncode, 3)
        self.assertIn("## goal", result.stdout)
        self.assertIn("MISSING: nope", result.stderr)

    def test_missing_file_exits_2(self):
        result = run(str(Path(self.tmp.name, "absent.html")), "goal")
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot read", result.stderr)

    def test_no_ids_is_usage_error(self):
        self.assertEqual(run(str(self.file)).returncode, 1)


if __name__ == "__main__":
    unittest.main()
