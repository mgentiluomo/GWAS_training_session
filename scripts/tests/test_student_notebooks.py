"""Check student delivery, option coverage and the tracked notebook freshness."""
import copy
import shutil
import subprocess
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import course_exports as exports
import student_notebooks as students


class StudentNotebookTests(unittest.TestCase):
    def test_tracked_pilot_is_current(self):
        students.export_notebooks(ROOT / "notebooks", check=True)

    def test_missing_or_changed_notebook_fails_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            with self.assertRaises(SystemExit):
                students.export_notebooks(folder, check=True)
            self.assertEqual(list(folder.iterdir()), [])
            students.export_notebooks(folder)
            path = folder / "module_03_sample_quality_control.Rmd"
            path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
            students.export_notebooks(folder, check=True)
            path.write_bytes(path.read_bytes() + b"Outdated copy\n")
            before = path.read_bytes()
            with self.assertRaises(SystemExit):
                students.export_notebooks(folder, check=True)
            self.assertEqual(path.read_bytes(), before)

    def test_each_step_preserves_its_literal_r_fence(self):
        _, notebook = students.module_three()
        source = (ROOT / "lessons/module_03_sample_quality_control.Rmd").read_text(encoding="utf-8")
        for chunk in exports.CHUNK.finditer(source):
            if chunk.group(1).startswith("s3-"):
                self.assertIn(chunk.group().rstrip(), notebook)
        labels = [chunk.group(1) for chunk in exports.CHUNK.finditer(notebook)]
        self.assertEqual(len(labels), len(set(labels)))
        self.assertEqual(len(re.findall(r"^## Step 3\.\d+ · ", notebook, re.M)), 8)

    def test_option_tables_are_complete_and_self_contained(self):
        _, notebook = students.module_three()
        for record in exports.export_steps():
            if record["module"] != 3:
                continue
            section = notebook.split(f'## Step {record["id"]} · ', 1)[1].split("\n## Step ", 1)[0]
            table = section.split("### What each option does", 1)[1].split("### Expected result", 1)[0]
            resource_line = ("Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) "
                             "and `--memory 2048` (PLINK uses at most about 2 GB of memory).")
            self.assertEqual(table.count(resource_line), int(bool(record["plink"]["commands"])))
            self.assertNotIn('| `--threads` |', table)
            self.assertNotIn('| `--memory` |', table)
            for group in record["student_plink_options"]:
                for option in group["options"]:
                    self.assertIn(f'`{option["name"]}`', table)
                    self.assertNotRegex(option["explanation"], r"earlier|given at|same as")
                    for modifier in option.get("modifiers", []):
                        self.assertIn(f'&nbsp;&nbsp;&rarr; `{modifier["name"]}`', table)
            if len(record["plink"]["commands"]) > 1:
                for index in range(1, len(record["plink"]["commands"]) + 1):
                    self.assertIn(f"**Command {index}:", table)
            else:
                self.assertNotIn("**Command 1:", table)
            self.assertNotIn("Validation:", section)
        self.assertIn("No PLINK equivalent", notebook)
        self.assertNotIn("\u2014", notebook)
        self.assertNotIn("interactive_data", notebook)

    def test_parser_rejects_an_omitted_option(self):
        record = next(r for r in exports.export_steps() if r["id"] == "3.3")
        metadata = {"student_plink_options": copy.deepcopy(record["student_plink_options"])}
        metadata["student_plink_options"][-1]["options"] = [
            o for o in metadata["student_plink_options"][-1]["options"] if o["name"] != "--remove"]
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            exports.step_metadata(metadata, copy.deepcopy(record))

    def test_parser_requires_exact_resource_values_in_every_command(self):
        record = next(r for r in exports.export_steps() if r["id"] == "3.3")
        metadata = {"student_plink_options": record["student_plink_options"]}
        for index in range(len(record["plink"]["commands"])):
            for flag, value, other in (("--threads", "2", "4"), ("--memory", "2048", "4096")):
                for replacement in ("", f"{flag} {other}", f"{flag} {value} {flag} {value}"):
                    with self.subTest(command=index, flag=flag, replacement=replacement):
                        changed = copy.deepcopy(record)
                        changed["plink"]["commands"][index] = changed["plink"]["commands"][index].replace(
                            f"{flag} {value}", replacement)
                        with self.assertRaisesRegex(ValueError, "PLINK command"):
                            exports.step_metadata(metadata, changed)
                        from unittest.mock import patch
                        records = [changed if r["id"] == record["id"] else r for r in exports.export_steps()]
                        with patch.object(students, "export_steps", return_value=records):
                            with self.assertRaisesRegex(ValueError, "PLINK command"):
                                students.module_three()

    def test_bookkeeping_comment_once_per_contiguous_block(self):
        source = (ROOT / "lessons/module_03_sample_quality_control.Rmd").read_text(encoding="utf-8")
        comment = "# Course bookkeeping: records the counts for the next step. Do not change."
        for chunk in exports.CHUNK.finditer(source):
            lines = chunk.group(3).splitlines()
            previous_bookkeeping = False
            for index, line in enumerate(lines):
                if line == comment:
                    self.assertFalse(previous_bookkeeping)
                    continue
                bookkeeping = line.startswith(("ops <- guided_replay_lists(", "guided_register("))
                if bookkeeping and not previous_bookkeeping:
                    self.assertEqual(lines[index - 1], comment)
                previous_bookkeeping = bookkeeping

    def test_first_chunk_delegates_to_the_module_check(self):
        _, notebook = students.module_three()
        chunks = list(exports.CHUNK.finditer(notebook))
        self.assertEqual(chunks[0].group(1), "module3_check")
        self.assertEqual(chunks[0].group(3).strip().splitlines(), [
            'if (!file.exists("config.R") && file.exists("../config.R")) setwd("..")',
            'source("R/guided.R"); guided_check_module(3)'])
        self.assertIn("cfg <- guided_init()", chunks[1].group(3))

    def test_module_check_table_matches_lesson_metadata(self):
        students.sync_module_check(ROOT, check=True)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "R").mkdir()
            source = (ROOT / "R/guided.R").read_text(encoding="utf-8")
            (root / "R/guided.R").write_text(source.replace("s2-8_state.pgen", "wrong.pgen"), encoding="utf-8")
            from unittest.mock import patch
            with patch.object(students, "export_modules", return_value=exports.export_modules()):
                with self.assertRaisesRegex(ValueError, "module_meta disagree"):
                    students.sync_module_check(root, check=True)

    def test_command_chunks_only_add_comments_compared_with_head(self):
        if shutil.which("git") is None:
            self.skipTest("Git is unavailable; cannot compare Module 3 command chunks with HEAD.")
        previous = subprocess.run(
            ["git", "show", "HEAD:lessons/module_03_sample_quality_control.Rmd"],
            cwd=ROOT, check=True, capture_output=True).stdout.decode("utf-8")
        current = (ROOT / "lessons/module_03_sample_quality_control.Rmd").read_text(encoding="utf-8")
        def command_chunks(text):
            result = {}
            for step in exports.STEP.finditer(text):
                following = exports.HEADING.search(text, step.end())
                body = text[step.end():following.start() if following else len(text)]
                for chunk in exports.CHUNK.finditer(exports.split_blocks(body)["command"]):
                    result[chunk.group(1)] = "\n".join(
                        line for line in chunk.group(3).splitlines() if not line.lstrip().startswith("#"))
            return result
        self.assertEqual(command_chunks(previous), command_chunks(current))

    def test_parser_rejects_wrong_order_and_misplaced_modifiers(self):
        for step in ("3.1", "3.3", "3.4", "3.7"):
            record = next(r for r in exports.export_steps() if r["id"] == step)
            groups = copy.deepcopy(record["student_plink_options"])
            groups[0]["options"][0:2] = reversed(groups[0]["options"][0:2])
            with self.assertRaisesRegex(ValueError, "ordered"):
                exports.step_metadata({"student_plink_options": groups}, copy.deepcopy(record))
            groups = copy.deepcopy(record["student_plink_options"])
            for group in groups:
                for option in group["options"]:
                    if option.get("modifiers"):
                        modifier = option["modifiers"].pop()
                        group["options"].append(modifier)
                        with self.assertRaisesRegex(ValueError, "modifiers"):
                            exports.step_metadata({"student_plink_options": groups}, copy.deepcopy(record))
                        break

    def test_parser_rejects_missing_bare_modifiers(self):
        for step in ("3.4", "3.7"):
            record = next(r for r in exports.export_steps() if r["id"] == step)
            groups = copy.deepcopy(record["student_plink_options"])
            for group in groups:
                for option in group["options"]:
                    option.pop("modifiers", None)
            with self.assertRaisesRegex(ValueError, "modifiers"):
                exports.step_metadata({"student_plink_options": groups}, copy.deepcopy(record))

    def test_verification_note_is_separate_without_changing_site_text(self):
        for record in exports.export_steps():
            if record["module"] != 3:
                continue
            self.assertEqual(record["blocks"]["expected_result"].replace(record["verification_notes"][0], "").strip(),
                             record["student_expected_result"])
            self.assertNotIn("Validation:", record["student_expected_result"])
            self.assertIn("passed on Windows", record["verification_notes"][0])

    def test_module_input_paths_cannot_escape(self):
        metadata = {"prerequisites": {"checkpoint": "2.8", "restart_step": "3.1",
                                     "files": [{"base": "output", "path": "../elsewhere"}]}}
        with self.assertRaises(ValueError):
            exports.module_prerequisites(metadata)


if __name__ == "__main__":
    unittest.main()
