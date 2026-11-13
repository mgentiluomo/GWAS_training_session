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
            text = (ROOT / record["source"]).read_text(encoding="utf-8")
            heading = next(m for m in exports.STEP.finditer(text)
                           if f"{m.group(1)}.{m.group(2)}" == record["id"])
            end = next(m.start() for m in exports.HEADING.finditer(text) if m.start() > heading.start())
            body = text[heading.end():end]
            opening = body.strip().splitlines()[0]
            note = exports.READING_NOTE.fullmatch(opening)
            self.assertIsNotNone(note)
            self.assertEqual(int(note.group(1)), (exports.reading_word_count(body) + 199) // 200)
            self.assertTrue(record["blocks"]["what_we_do"].startswith(opening))
        journey = next(r for r in readings if r["id"] == "1.9")
        self.assertEqual(len(journey["figures"]), 1)
        self.assertIn("Three data journeys", journey["figures"][0]["alt_text"])
        self.assertNotIn("samtools view", exports.main_script())
        self.assertNotIn("--bgen", exports.main_script())

    def test_reading_count_ignores_urls_code_and_hidden_metadata(self):
        text = ("Reading, about 1 minutes. You can come back to it later.\n\n"
                "[Two words](https://example.invalid/a?b=c)\n"
                "| Field | Meaning |\n| --- | --- |\n| GT | Called genotype |\n"
                "<!-- Hidden words -->\n```sh\nnot part of prose\n```\n")
        self.assertEqual(exports.reading_word_count(text), 7)

    def test_format_syntax_is_explicitly_read_only_and_tables_are_scannable(self):
        record = next(r for r in self.records if r["id"] == "1.10")
        text = record["blocks"]["why"]
        sections = re.split(r"^#### ", text, flags=re.M)[1:]
        self.assertEqual(len(sections), 9)
        for section in sections:
            self.assertIn("| Field | Meaning |", section)
            self.assertIn("**Common mistakes**", section)
        examples = re.findall(r"<details><summary>Example syntax, do not run</summary>(.*?)</details>", text, re.S)
        self.assertEqual(len(examples), 4)
        self.assertEqual(sum(part.count("```sh") for part in examples), text.count("```sh"))
        for phrase in ("No vendor binary is fabricated", "not genuine imputation",
                       "The filenames here are explanatory names"):
            self.assertNotIn(phrase, text)

    def test_format_examples_links_and_exported_assets_resolve(self):
        from urllib.parse import unquote
        for record in self.records:
            for target in re.findall(r"\]\((examples/formats/[^)]+)\)", "\n".join(record["blocks"].values())):
                # Exported links are paths from the repository root.
                path = ROOT / unquote(target)
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

    def test_relative_links_are_exported_as_repository_paths(self):
        text = ("[a](../docs/glossary.md#r) [b](module_02_files_and_formats.Rmd#step-2-5) "
                "[c](../examples/formats/) [d](https://example.org/x) [e](#here) "
                '<a href="../docs/troubleshooting.md">t</a>\n```r\nx[1](../docs/not-a-link.md)\n```\n')
        out = exports.normalise_links(text)
        for expected in ("](docs/glossary.md#r)", "](lessons/module_02_files_and_formats.Rmd#step-2-5)",
                         "](examples/formats/)", "](https://example.org/x)", "](#here)",
                         'href="docs/troubleshooting.md"', "x[1](../docs/not-a-link.md)"):
            self.assertIn(expected, out)
        with self.assertRaises(ValueError):
            exports.normalise_links("[x](../../outside.md)")

    def test_every_exported_internal_link_resolves_from_the_repository_root(self):
        link = re.compile(r"(?<!!)\]\(([^)\s]+)\)|href=\"([^\"]+)\"")
        anchor = re.compile(r"\{#([A-Za-z0-9_-]+)\}")
        texts = [json.dumps(r["blocks"]) for r in self.records]
        texts += [m["overview_markdown"] + m["recap_markdown"] for m in exports.export_modules()]
        checked = 0
        for text in texts:
            text = text.replace("\\n", "\n").replace('\\"', '"')
            for match in link.finditer(text):
                target = match.group(1) or match.group(2)
                if re.match(r"[A-Za-z][A-Za-z0-9+.-]*:|#", target):
                    continue
                path, _, fragment = target.partition("#")
                resolved = ROOT / path
                self.assertTrue(resolved.exists(), target)
                if fragment and resolved.suffix in {".md", ".Rmd"}:
                    self.assertIn(fragment, anchor.findall(resolved.read_text(encoding="utf-8")), target)
                checked += 1
        self.assertGreater(checked, 300)

    def test_under_the_hood_block_is_optional_last_and_sourced(self):
        pilot = {"3.4", "3.5", "3.6", "5.4", "6.6"}
        for record in self.records:
            blocks = record["blocks"]
            if record["id"] not in pilot:
                self.assertNotIn("under_the_hood", blocks)
                continue
            self.assertEqual(list(blocks)[-1], "under_the_hood")
            text = blocks["under_the_hood"]
            words = len(re.findall(r"\b\w+(?:[.'/-]\w+)*\b", text))
            self.assertTrue(150 <= words <= 350, (record["id"], words))
            for heading in ("**What the tool computes.**", "**Why these values.**", "**Pitfalls.**", "**References**"):
                self.assertIn(heading, text)
            references = re.findall(r"^\d+\. .*$", text, re.M)
            self.assertTrue(2 <= len(references) <= 4, record["id"])
            for reference in references:
                self.assertRegex(reference, r"PMID \d+\.|doi:10\.\d+/\S+\.")
            self.assertNotIn("—", text)
        with self.assertRaises(ValueError):
            exports.split_blocks("### What we do\nx\n### Why\nx\n### You need\nx\n### Command\nx\n"
                                 "<details><summary>Show the expected result</summary>x</details>\n"
                                 "<details><summary>If something goes wrong</summary>x</details>\n"
                                 "<details><summary>Under the hood & literature</summary>x</details>\n"
                                 "### Quick check\nx\n### Files created\nx\n")

    def test_mathematical_text_has_no_lossy_question_mark_substitutions(self):
        for path in exports.notebook_paths():
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("\ufffd", text)
            # Query strings in legitimate source URLs are not mathematical corruption.
            visible = re.sub(r"https?://[^\s)]+", "", text)
            self.assertIsNone(re.search(r"\w\?\w|\?\?|\?log10|10\^\(\?", visible), path.name)

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
                              "boundary\t2\t100\n" + "complete\t0\t100\n" * 1970, encoding="utf-8")
            data = author.aggregate(report)
            self.assertEqual(data["rows"][14]["samples_below"], 0)  # exactly 97% passes
            self.assertEqual(data["rows"][16]["samples_below"], 42)  # exactly 98% passes
            self.assertEqual(data["rows"][17]["samples_below"], 43)
            self.assertNotIn("private", json.dumps(data))

    def test_required_blocks_and_figure_prompts(self):
        for record in self.records:
            if (record["module"] != 0 or record["step"] in {4, 5, 7, 8}) and not (record["module"] == 1 and record["step"] >= 8):
                self.assertTrue(record["r_commands"])
            self.assertTrue(record["setup_code"] or record["module"] == 0 or not record["r_commands"])
            for name, _ in exports.BLOCKS:
                if name not in exports.OPTIONAL_BLOCKS:
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
        expected = {"0.1": 2, "0.2": 2, "0.4": 2, "0.6": 2, "0.7": 4, "0.8": 2, "5.5": 2}
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
        for record in [r for r in self.records if r["id"] in {"0.1", "0.2", "0.3", "0.6"}]:
            with self.subTest(step=record["id"]):
                self.assertEqual(record["r_commands"], [])
                self.assertEqual(record["setup_code"], "")
                self.assertEqual(record["verification"], "manual_required")
                self.assertNotIn("```", record["blocks"]["command"])
                self.assertNotIn("Rscript", record["blocks"]["command"])
        system_step = self.records[0]
        self.assertIn("System type", system_step["blocks"]["what_we_do"])
        self.assertIn("Settings", system_step["blocks"]["what_we_do"])
        check = next(r for r in self.records if r["id"] == "0.4")
        code = "\n".join(c["code"] for c in check["r_commands"])
        self.assertIn("Sys.info()", code)
        self.assertIn("R.version.string", code)
        preflight = next(r for r in self.records if r["id"] == "0.8")
        self.assertIn('source("scripts/preflight.R")', preflight["r_commands"][0]["code"])
        installer = next(r for r in self.records if r["id"] == "0.2")
        download_url = "https://docs.posit.co/ide/user/download.html"
        self.assertIn(download_url, installer["blocks"]["what_we_do"])
        self.assertIn('Go to "RStudio Desktop"', installer["blocks"]["what_we_do"])
        old_url = "https://posit.co/download/" + "rstudio-desktop/"
        for source in ("lessons/module_00_preparation.Rmd", "docs/legacy_demo.md", "tutorial/index.html"):
            text = (ROOT / source).read_text(encoding="utf-8")
            self.assertNotIn(old_url, text)
            self.assertIn(download_url, text)

    def test_data_download_has_one_main_command_and_a_file_chooser_fallback(self):
        record = next(r for r in self.records if r["id"] == "0.7")
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
        self.assertIn("# Chunk: s0-8_preflight", script)
        self.assertNotIn("install_course_packages()", script)
        self.assertIn("# Chunk: course_progress", script)

    def test_ui_metadata_is_source_backed_and_optional(self):
        for record in self.records:
            self.assertEqual(record["schema_version"], "1.1")
            if record["module"] == 0:
                self.assertIn("actions", record)
                self.assertIn("success_line", record)
                self.assertTrue(all(c["where"] == "console" for c in record["r_commands"]))
            if "success_line" in record:
                self.assertIn(record["success_line"], record["blocks"]["expected_result"])
            self.assertNotIn("<!-- step_meta:", json.dumps(record["blocks"]))
        self.assertEqual([r["id"] for r in self.records if "success_line" not in r], ["1.8", "1.9", "1.10", "1.11"])
        record = {"id": "test", "blocks": {"expected_result": "A real result."},
                  "r_commands": [{"label": "example"}]}
        for bad in ({"success_line": "Invented output."}, {"where": {"missing": "console"}},
                    {"where": {"example": "unknown"}}, {"actions": [{"label": "bad", "url": "javascript:alert(1)", "kind": "page"}]}):
            with self.subTest(metadata=bad), self.assertRaises(ValueError):
                exports.step_metadata(bad, record)
        self.assertEqual(exports.step_metadata({}, record), {})
        self.assertNotIn("where", record["r_commands"][0])


if __name__ == "__main__":
    unittest.main()
