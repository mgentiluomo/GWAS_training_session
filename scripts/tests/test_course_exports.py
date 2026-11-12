"""Check that generated text exports remain faithful to the tested notebooks."""
import importlib.util
import json
from pathlib import Path
import shlex
import re
import unittest
import tempfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("course_exports", ROOT / "scripts" / "course_exports.py")
exports = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exports)


class CourseExportsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = exports.export_steps()

    def test_complete_main_path(self):
        self.assertEqual(len(self.records), 60)
        self.assertEqual([sum(r["module"] == i for r in self.records) for i in range(8)], [8, 7, 8, 8, 6, 7, 8, 8])
        self.assertEqual(self.records[0]["id"], "0.1")
        self.assertEqual(self.records[-1]["id"], "7.8")

    def test_mathematical_text_has_no_lossy_question_mark_substitutions(self):
        for path in exports.notebook_paths():
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(re.search(r"\w\?\w|\?\?|\?log10|10\^\(\?", text), path.name)
            self.assertNotIn("\ufffd", text)

    def test_committed_json_matches_canonical_sources(self):
        paths = list((ROOT / "site_content" / "steps").glob("*.json"))
        self.assertEqual(len(paths), 60)
        for record in self.records:
            with self.subTest(step=record["id"]):
                saved = json.loads((ROOT / "site_content" / "steps" / (record["anchor"] + ".json")).read_text(encoding="utf-8"))
                self.assertEqual(saved, record)

    def test_every_command_option_has_an_explanation(self):
        for record in self.records:
            flags = {token for command in record["plink"]["commands"] for token in shlex.split(command) if token.startswith("--")}
            self.assertEqual(flags, {option["name"] for option in record["plink"]["options"]})
            self.assertTrue(all(option["explanation_markdown"] for option in record["plink"]["options"]))

    def test_option_explanations_are_clauses_and_references_are_local(self):
        text = "`--geno 0.02` filters sites; `--mind 0.02` filters samples. R plots counts."
        self.assertEqual(exports.flag_explanation("--geno", text), "`--geno 0.02` filters sites")
        self.assertEqual(exports.flag_explanation("--mind", text), "`--mind 0.02` filters samples.")
        self.assertIsNone(exports.flag_explanation("--out", "`--out` has the meanings given at 3.1."))
        by_id = {r["id"]: r for r in self.records}
        references = []
        for record in self.records:
            for option in record["plink"]["options"]:
                if "explained_at" in option:
                    origin = by_id[option["explained_at"]]
                    self.assertEqual(origin["module"], record["module"])
                    self.assertLess(origin["step"], record["step"])
                    self.assertEqual(exports.flag_explanation(option["name"], origin["blocks"]["command"]),
                                     option["explanation_markdown"])
                    references.append(option)
        self.assertTrue(references)

    def test_interactive_counts_are_aggregate_only(self):
        record = next(r for r in self.records if r["id"] == "3.2")
        data = record["interactive_data"]
        self.assertEqual(set(data), {"kind", "source_state", "sample_count", "comparison",
                                     "call_rate_definition", "source_report_sha256", "rows"})
        self.assertEqual(data["source_state"], "3.1")
        self.assertEqual(data["sample_count"], 2013)
        self.assertEqual(data["comparison"], "strictly_below")
        self.assertEqual([r["threshold_percent"] for r in data["rows"]], [x / 2 for x in range(180, 200)])
        counts = [r["samples_below"] for r in data["rows"]]
        self.assertEqual(counts, sorted(counts))
        self.assertEqual(counts[16], 42)
        self.assertTrue(all(set(row) == {"threshold_percent", "samples_below"} for row in data["rows"]))
        self.assertNotIn("interactive_data:", record["blocks"]["expected_result"])
        self.assertEqual([r["id"] for r in self.records if "interactive_data" in r], ["3.2"])

    def test_call_rate_counts_use_strict_integer_boundaries(self):
        spec = importlib.util.spec_from_file_location("aggregate_counts", ROOT / "scripts/author/export_call_rate_counts.py")
        author = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(author)
        with tempfile.TemporaryDirectory() as folder:
            report = Path(folder) / "test.smiss"
            report.write_text("IID\tMISSING_CT\tOBS_CT\n" +
                              "".join(f"private{i}\t3\t100\n" for i in range(42)) +
                              "boundary\t2\t100\n" + "complete\t0\t100\n" * 1970)
            data = author.aggregate(report)
            self.assertEqual(data["rows"][14]["samples_below"], 0)  # exactly 97% passes
            self.assertEqual(data["rows"][16]["samples_below"], 42)  # exactly 98% passes
            self.assertEqual(data["rows"][17]["samples_below"], 43)
            self.assertNotIn("private", json.dumps(data))

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
            self.assertNotIn("Gemini prompt:", record["blocks"]["files_created"])

    def test_combined_script_matches_chunks_and_omits_interactive_downloads(self):
        script = exports.main_script()
        self.assertEqual((ROOT / "scripts" / "run_main_path.R").read_text(encoding="utf-8"), script)
        self.assertNotIn("download_course_data(", script)
        self.assertIn("# Chunk: s7-8", script)
        self.assertIn("# Chunk: s0-7_preflight", script)


if __name__ == "__main__":
    unittest.main()
