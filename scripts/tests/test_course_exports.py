"""Check that generated text exports remain faithful to the tested notebooks."""
import importlib.util
import json
from pathlib import Path
import shlex
import re
import unittest
from unittest.mock import patch
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
        self.assertEqual(len(self.records), 64)
        self.assertEqual([sum(r["module"] == i for r in self.records) for i in range(8)], [8, 11, 8, 8, 6, 7, 8, 8])
        self.assertEqual(self.records[0]["id"], "0.1")
        self.assertEqual(self.records[-1]["id"], "7.8")

    def test_new_format_readings_have_no_executable_commands_or_setup(self):
        readings = [r for r in self.records if r["module"] == 1 and r["step"] >= 8]
        self.assertEqual([r["id"] for r in readings], ["1.8", "1.9", "1.10", "1.11"])
        for record in readings:
            self.assertEqual(record["r_commands"], [])
            self.assertEqual(record["setup_code"], "")
            self.assertEqual(record["verification"], "manual_required")
            self.assertEqual(record["plink"]["commands"], [])
            self.assertIn("No code to run", record["blocks"]["command"])
            self.assertIn("pubmed.ncbi.nlm.nih.gov", record["blocks"]["why"])
        journey = next(r for r in readings if r["id"] == "1.9")
        self.assertEqual(len(journey["figures"]), 1)
        self.assertIn("Three data journeys", journey["figures"][0]["alt_text"])
        self.assertNotIn("samtools view", exports.main_script())
        self.assertNotIn("--bgen", exports.main_script())

    def test_format_examples_links_and_exported_assets_resolve(self):
        from urllib.parse import unquote
        for record in self.records:
            for target in re.findall(r"\]\((\.\./examples/formats/[^)]+)\)", "\n".join(record["blocks"].values())):
                path = ROOT / "lessons" / unquote(target)
                self.assertNotRegex(path.name, r"\s")
                self.assertTrue(path.exists(), target)
                if path.is_file():
                    copied = ROOT / "site_content/formats/examples" / path.name
                    self.assertEqual(copied.read_bytes(), path.read_bytes())
        reading = next(r for r in self.records if r["id"] == "1.10")
        for line in reading["blocks"]["why"].splitlines():
            if not line.startswith("plink2 "):
                continue
            tokens = shlex.split(line)
            for option in ("--vcf", "--update-sex", "--bgen", "--sample", "--bfile"):
                if option not in tokens:
                    continue
                name = tokens[tokens.index(option) + 1]
                suffixes = (".bed", ".bim", ".fam") if option == "--bfile" else ("",)
                for suffix in suffixes:
                    self.assertTrue((ROOT / "examples/formats" / (name + suffix)).is_file(), line)

    def test_mathematical_text_has_no_lossy_question_mark_substitutions(self):
        for path in exports.notebook_paths():
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(re.search(r"\w\?\w|\?\?|\?log10|10\^\(\?", text), path.name)
            self.assertNotIn("\ufffd", text)

    def test_committed_json_matches_canonical_sources(self):
        paths = list((ROOT / "site_content" / "steps").glob("*.json"))
        self.assertEqual(len(paths), 64)
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
            if (record["module"] != 0 or record["step"] >= 5) and not (record["module"] == 1 and record["step"] >= 8):
                self.assertTrue(record["r_commands"])
            self.assertTrue(record["setup_code"] or record["module"] == 0 or not record["r_commands"])
            for name, _ in exports.BLOCKS:
                if name != "what_this_check_can_reveal":
                    self.assertTrue(record["blocks"][name])
            for figure in record["figures"]:
                if figure["kind"] == "placeholder":
                    self.assertIsNone(figure["asset"])
                    self.assertTrue(figure["gemini_prompt"])
                else:
                    self.assertEqual(figure["kind"], "screenshot")
                    expected = figure["asset_path"] if (ROOT / figure["asset_path"]).is_file() else None
                    self.assertEqual(figure["asset"], expected)
                    self.assertNotIn("gemini_prompt", figure)
                self.assertFalse(figure["reviewed"])
            self.assertNotIn("Gemini prompt:", record["blocks"]["files_created"])

    def test_screenshot_capture_list_matches_notebook_declarations(self):
        screenshots = [(r, f) for r in self.records for f in r["figures"] if f["kind"] == "screenshot"]
        self.assertEqual(len(screenshots), 16)
        expected = {"0.2": 2, "0.3": 2, "0.4": 2, "0.5": 4, "0.6": 2, "0.7": 2, "5.5": 2}
        self.assertEqual({step: sum(r["id"] == step for r, _ in screenshots) for step in expected}, expected)
        self.assertEqual(len({f["asset_path"] for _, f in screenshots}), 16)
        checklist = (ROOT / "docs/screenshot_list.md").read_text(encoding="utf-8")
        for record, figure in screenshots:
            self.assertIn(Path(figure["asset_path"]).name, checklist)
            self.assertIn(figure["alt_text"], checklist)
            self.assertTrue(Path(figure["asset_path"]).name.startswith("s" + record["id"].replace(".", "-") + "_"))
            self.assertTrue(figure["asset_path"].endswith("_" + figure["platform"] + ".png"))
            self.assertIn(figure["placement"], record["blocks"])
            self.assertNotIn("<!-- screenshot:", json.dumps(record["blocks"]))
        self.assertEqual({r["id"] for r, _ in screenshots}, set(expected))

    def test_screenshot_assets_resolve_only_when_the_file_exists(self):
        spec = {"kind": "screenshot", "asset_path": "Figures/screenshots/s0-3_console_windows.png",
                "platform": "windows", "placement": "expected_result", "alt_text": "RStudio Console with an empty R prompt."}
        body = "<!-- screenshot: " + json.dumps(spec) + " -->"
        # Simulate the file's presence without creating an image.
        with patch.object(Path, "is_file", return_value=False):
            self.assertIsNone(exports.screenshot_figures(body)[0]["asset"])
        with patch.object(Path, "is_file", return_value=True):
            figure = exports.screenshot_figures(body)[0]
            self.assertEqual(figure["asset"], spec["asset_path"])
            self.assertEqual(figure["alt_text"], spec["alt_text"])
            self.assertFalse(figure["reviewed"])
        for changes in ({"asset_path": "../outside.png"}, {"asset_path": "/outside.png"},
                        {"asset_path": "https://example.invalid/a.png"}, {"alt_text": ""},
                        {"platform": "unknown"}, {"placement": "unknown"}, {"asset_path": "Figures/screenshots/a.svg"}):
            with self.subTest(changes=changes):
                bad = "<!-- screenshot: " + json.dumps({**spec, **changes}) + " -->"
                with self.assertRaises(ValueError):
                    exports.screenshot_figures(bad)
        with self.assertRaises(ValueError):
            exports.screenshot_figures(body + body)

    def test_installation_steps_need_no_r_commands_or_setup(self):
        for record in self.records[:4]:
            with self.subTest(step=record["id"]):
                self.assertEqual(record["r_commands"], [])
                self.assertEqual(record["setup_code"], "")
                self.assertEqual(record["verification"], "manual_required")
                self.assertNotIn("```", record["blocks"]["command"])
                self.assertNotIn("Rscript", record["blocks"]["command"])
        system_step = self.records[0]
        self.assertIn("System type", system_step["blocks"]["what_we_do"])
        self.assertIn("Settings", system_step["blocks"]["what_we_do"])
        check = next(r for r in self.records if r["id"] == "0.7")
        code = "\n".join(c["code"] for c in check["r_commands"])
        self.assertIn("Sys.info()", code)
        self.assertIn("R.version.string", code)
        self.assertIn('source("scripts/preflight.R")', code)

    def test_data_download_has_one_main_command_and_a_file_chooser_fallback(self):
        record = next(r for r in self.records if r["id"] == "0.5")
        self.assertEqual([c["code"] for c in record["r_commands"]], ["download_course_data()"])
        self.assertNotIn("zip_path", record["blocks"]["command"])
        self.assertNotIn("yourname", json.dumps(record))
        self.assertIn("download_course_data(zip_path = file.choose())", record["blocks"]["troubleshooting"])
        self.assertIn("download_course_data(overwrite = TRUE)", record["blocks"]["troubleshooting"])
        self.assertIn("108 files verified. Nothing to do.", record["blocks"]["expected_result"])

    def test_site_setup_keeps_helpers_and_excludes_notebook_rendering(self):
        for record in self.records:
            with self.subTest(step=record["id"]):
                setup = record["setup_code"]
                self.assertNotIn("setwd", setup)
                self.assertNotIn("knitr", setup)
                self.assertNotIn("start_dir", setup)
                if record["module"] == 0 or not record["r_commands"]:
                    self.assertEqual(setup, "")
                else:
                    self.assertIn('source("R/guided.R")', setup)
                    self.assertIn("cfg <- guided_init()", setup)
        script = exports.main_script()
        self.assertNotIn("knit_setup", script)
        self.assertNotIn("opts_knit", script)
        self.assertIn('source("R/guided.R")', script)

    def test_combined_script_matches_chunks_and_omits_interactive_downloads(self):
        script = exports.main_script()
        self.assertEqual((ROOT / "scripts" / "run_main_path.R").read_text(encoding="utf-8"), script)
        self.assertNotIn("download_course_data(", script)
        self.assertIn("# Chunk: s7-8", script)
        self.assertIn("# Chunk: s0-7_preflight", script)


if __name__ == "__main__":
    unittest.main()
