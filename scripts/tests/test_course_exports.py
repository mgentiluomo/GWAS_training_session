"""Check that generated text exports remain faithful to the tested notebooks."""
import importlib.util
import json
from pathlib import Path
import shlex
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("course_exports", ROOT / "scripts" / "course_exports.py")
exports = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exports)


class CourseExportsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = exports.export_steps()

    def test_complete_main_path(self):
        self.assertEqual(len(self.records), 59)
        self.assertEqual([sum(r["module"] == i for r in self.records) for i in range(8)], [8, 7, 8, 8, 6, 7, 7, 8])
        self.assertEqual(self.records[0]["id"], "0.1")
        self.assertEqual(self.records[-1]["id"], "7.8")

    def test_committed_json_matches_canonical_sources(self):
        paths = list((ROOT / "site_content" / "steps").glob("*.json"))
        self.assertEqual(len(paths), 59)
        for record in self.records:
            with self.subTest(step=record["id"]):
                saved = json.loads((ROOT / "site_content" / "steps" / (record["anchor"] + ".json")).read_text(encoding="utf-8"))
                self.assertEqual(saved, record)

    def test_every_command_option_has_an_explanation(self):
        for record in self.records:
            flags = {token for command in record["plink"]["commands"] for token in shlex.split(command) if token.startswith("--")}
            self.assertEqual(flags, {option["name"] for option in record["plink"]["options"]})
            self.assertTrue(all(option["explanation_markdown"] for option in record["plink"]["options"]))

    def test_required_blocks_and_figure_prompts(self):
        for record in self.records:
            self.assertTrue(record["r_commands"])
            self.assertTrue(record["setup_code"] or record["module"] == 0)
            for name, _ in exports.BLOCKS:
                if name != "what_this_check_can_reveal":
                    self.assertTrue(record["blocks"][name])
            for figure in record["figures"]:
                self.assertIsNone(figure["asset"])
                self.assertTrue(figure["gemini_prompt"])
                self.assertFalse(figure["reviewed"])

    def test_combined_script_matches_chunks_and_omits_interactive_downloads(self):
        script = exports.main_script()
        self.assertEqual((ROOT / "scripts" / "run_main_path.R").read_text(encoding="utf-8"), script)
        self.assertNotIn("download_course_data(", script)
        self.assertIn("# Chunk: s7-8", script)
        self.assertIn("# Chunk: s0-7_preflight", script)


if __name__ == "__main__":
    unittest.main()
