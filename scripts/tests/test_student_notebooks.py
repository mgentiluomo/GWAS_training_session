"""Check student delivery, option coverage and the tracked notebook freshness."""
import copy
import json
import shutil
import subprocess
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import course_exports as exports
import student_notebooks as students


class StudentNotebookTests(unittest.TestCase):
    def test_logistic_model_modifier_order(self):
        self.assertEqual(exports.plink_option_order(
            "bin/plink2 --glm sex hide-covar firth-fallback cols=+a1freq --out scan"),
            [("--glm", ["sex", "hide-covar", "firth-fallback", "cols"]), ("--out", [])])
        self.assertEqual(exports.plink_option_order("bin/plink2 --glm firth sex hide-covar"),
                         [("--glm", ["firth", "sex", "hide-covar"])])
        self.assertEqual(exports.plink_option_order("bin/plink2 --glm no-firth"),
                         [("--glm", ["no-firth"])])

    def test_reference_projection_modifier_order(self):
        self.assertEqual(exports.plink_option_order(
            "bin/plink2 --pca 10 allele-wts --score weights 2 5 header-read "
            "no-mean-imputation variance-standardize --score-col-nums 6-15"), [
                ("--pca", ["allele-wts"]),
                ("--score", ["header-read", "no-mean-imputation", "variance-standardize"]),
                ("--score-col-nums", []),
            ])

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

    def test_conditional_liftover_option_is_required_in_r_order(self):
        record = next(r for r in exports.export_steps() if r["id"] == "2.6")
        groups = copy.deepcopy(record["student_plink_options"])
        exports.step_metadata({"student_plink_options": groups}, copy.deepcopy(record))
        for alteration in ("omit", "reorder", "duplicate", "invent"):
            changed = copy.deepcopy(groups)
            options = changed[0]["options"]
            index = next(i for i, option in enumerate(options) if option["name"] == "--flip")
            if alteration == "omit":
                options.pop(index)
            elif alteration == "reorder":
                options[index], options[index + 1] = options[index + 1], options[index]
            elif alteration == "duplicate":
                options.insert(index, copy.deepcopy(options[index]))
            else:
                options[index]["name"] = "--invented"
            with self.subTest(alteration=alteration), self.assertRaisesRegex(ValueError, "Incomplete"):
                exports.step_metadata({"student_plink_options": changed}, copy.deepcopy(record))
        # An unconditional or unconsumed flag must not relax terminal coverage.
        for replacement in ('unused <- c(args, "--flip"', 'args <- c(args, "--flip"'):
            changed_record = copy.deepcopy(record)
            changed_record["r_commands"][0]["code"] = changed_record["r_commands"][0]["code"].replace(
                'if (length(reverse)) args <- c(args, "--flip"', replacement)
            with self.subTest(replacement=replacement), self.assertRaisesRegex(ValueError, "Incomplete"):
                exports.step_metadata({"student_plink_options": groups}, changed_record)

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
            with patch.object(students, "export_modules", return_value=exports.export_modules()), patch.object(
                    students, "build_models", return_value=students.build_models()):
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
        for step in ("3.1", "3.3", "3.4", "3.7", "4.4", "4.5"):
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
        for step in ("3.4", "3.7", "4.4", "4.5"):
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

    def test_module_three_bytes_match_tracked_head(self):
        previous = subprocess.run(["git", "show", "HEAD:notebooks/module_03_sample_quality_control.Rmd"],
                                  cwd=ROOT, check=True, capture_output=True).stdout
        self.assertEqual(students.module_three()[1].encode("utf-8"), previous)
        before = (ROOT / "notebooks/module_03_sample_quality_control.Rmd").read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            target = destination / "module_03_sample_quality_control.Rmd"
            target.write_bytes(before)
            students.export_notebooks(destination)
            self.assertEqual(target.read_bytes(), before)

    def test_new_kinds_in_temporary_lesson_copies(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "lessons", root / "lessons")
            path = next((root / "lessons").glob("module_01_*.Rmd"))
            original = path.read_text(encoding="utf-8")
            heading = next(m for m in exports.STEP.finditer(original) if m.group(2) == "8")
            # The lesson now carries its own metadata for this step. Remove it from the copy.
            following = next(m.start() for m in exports.HEADING.finditer(original) if m.start() > heading.end())
            section = exports.STEP_META.sub("", original[heading.end():following])
            original = original[:heading.end()] + section + original[following:]
            heading = next(m for m in exports.STEP.finditer(original) if m.group(2) == "8")
            for kind in ("reading", "outside_r"):
                metadata = {"student_summary": "Read the explanation.", "student_kind": kind}
                if kind == "outside_r":
                    metadata["student_action"] = "Download the file. Open it in RStudio."
                text = original[:heading.end()] + '\n<!-- step_meta: ' + json.dumps(metadata) + ' -->\n' + original[heading.end():]
                path.write_text(text, encoding="utf-8")
                record = next(r for r in exports.export_steps(root) if r["id"] == "1.8")
                self.assertEqual(record["student_kind"], kind)
                self.assertEqual(record["r_commands"], [])
                record.pop("student_kind")
                with self.assertRaises(ValueError):
                    exports.step_metadata({"student_summary": "Read it."}, record)
            self.assertIn(3, [model["module"] for model in students.build_models(root)])

    def test_kind_validation(self):
        record = {"id": "0.1", "r_commands": [], "plink": {"commands": [], "options": []}}
        for metadata in (
                {"student_kind": "outside_r"}, {"student_kind": "unknown"},
                {"student_kind": "reading", "student_action": "Click it."},
                {"student_kind": "reading", "student_plink_options": []},
                {"student_kind": "reading", "student_summary": "Two\nparagraphs"},
                {"student_kind": "outside_r", "student_action": "\u2014"}):
            with self.subTest(metadata=metadata), self.assertRaises(ValueError):
                exports.step_metadata(metadata, copy.deepcopy(record))
        record["r_commands"] = [{"code": "x <- 1", "label": "s0-1"}]
        with self.assertRaises(ValueError):
            exports.step_metadata({"student_kind": "reading"}, record)

    def fake_models(self):
        models = []
        for number in range(8):
            models.append({"module": number, "title": f"Topic {number}",
                           "source": f"lessons/module_0{number}_topic.Rmd", "source_sha256": "hash",
                           "prerequisites": {"checkpoint": None, "restart_step": None, "files": []},
                           "setup_code": 'source("R/guided.R")\ncfg <- guided_init()' if number else "",
                           "steps": [{"id": f"{number}.1", "title": "Read", "anchor": f"step-{number}-1",
                                      "summary": "Read the idea.", "kind": "reading", "action": None,
                                      "chunks": [], "option_groups": [], "terminal_commands": [], "expected_result": ""}]})
        models[0]["steps"][0].update(kind="outside_r", action="Install R.")
        return models

    def test_complete_notebook_and_format_registry(self):
        models = self.fake_models()
        outputs = students.notebook_outputs(models)
        self.assertEqual(len(outputs), 9)
        complete = outputs["gwas_course_complete.Rmd"]
        self.assertEqual(complete.count('title: "GWAS course: modules 0 to 7"'), 1)
        self.assertEqual(complete.count("---\n"), 2)
        self.assertEqual(complete.count("Open `GWAS_course.Rproj`"), 1)
        self.assertEqual(complete.count("cfg <- guided_init()"), 1)
        self.assertLess(complete.index("# Module 0:"), complete.index("# Module 1:"))
        for number in range(8):
            self.assertIn(f"# Module {number}: Topic {number}", complete)
            self.assertIn(f"module{number}_check", complete)
            self.assertIn(f"module-{number}/step-{number}-1", complete)
        self.assertNotIn('source("R/guided.R")', complete.split("# Module 1:")[0])
        self.assertIn('setwd("..")', complete)
        self.assertIn("What you do: Install R.", complete)
        self.assertIn("This step is reading only. There is no code to run.", complete)
        self.assertNotIn("### Expected result", complete)
        self.assertNotIn("### What each option does", complete)
        self.assertNotIn("### PLINK terminal equivalent", complete)
        self.assertNotIn("gwas_course_complete.Rmd", students.notebook_outputs(models[:4]))
        with patch.dict(students.RENDERERS, {"test": lambda models, complete=False: "rendered"}):
            self.assertEqual(set(students.notebook_outputs(models[:2], "test").values()), {"rendered"})

    def test_models_enable_arbitrary_subsets_and_keep_literal_chunks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "lessons").mkdir()
            modules, records = [], []
            for number in range(8):
                source = f"lessons/module_0{number}_test.Rmd"
                literal = f'```{{r s{number}-1, eval=FALSE}}\nx <- {number}\n```'
                (root / source).write_text(literal + '\n', encoding="utf-8")
                modules.append({"module": number, "source": source, "title": f"Test {number}",
                                "source_sha256": "hash"})
                if number:
                    modules[-1]["prerequisites"] = {"checkpoint": None, "restart_step": None,
                                                   "files": [{"base": "data", "path": "input.tsv"}]}
                records.append({"id": f"{number}.1", "module": number, "title": "Test", "anchor": f"step-{number}-1",
                                "student_summary": "Run the code.", "student_plink_options": [],
                                "student_expected_result": "A value.", "setup_code": "",
                                "r_commands": [{"label": f"s{number}-1", "code": f"x <- {number}"}],
                                "plink": {"commands": [], "options": []}})
            with patch.object(students, "export_modules", return_value=modules), patch.object(
                    students, "export_steps", return_value=records):
                models = students.build_models(root)
                self.assertEqual([m["module"] for m in models], list(range(8)))
                for number, model in enumerate(models):
                    self.assertEqual(model["steps"][0]["chunks"],
                                     [(root / model["source"]).read_text(encoding="utf-8").rstrip()])
                self.assertEqual(len(students.notebook_outputs(models)), 9)
                for number in (0, 2, 4, 5, 7):
                    records[number].pop("student_summary")
                models = students.build_models(root)
                self.assertEqual([m["module"] for m in models], [1, 3, 6])
                self.assertEqual(len(students.notebook_outputs(models)), 3)
                table = students.module_check_table(root, models)
                for number in range(8):
                    self.assertEqual(f'`{number}` = list(' in table, number in (1, 3, 6))
                records.append({**records[1], "id": "1.2"})
                records[-1].pop("student_summary")
                self.assertEqual([m["module"] for m in students.build_models(root)], [3, 6])
                modules[6].pop("prerequisites")
                with self.assertRaisesRegex(ValueError, "module_meta prerequisites"):
                    students.build_models(root)

    def test_multiple_file_freshness_is_read_only(self):
        models = self.fake_models()
        with tempfile.TemporaryDirectory() as directory, patch.object(students, "build_models", return_value=models):
            root = Path(directory)
            (root / "R").mkdir()
            guided = root / "R/guided.R"
            guided.write_text("# BEGIN GENERATED MODULE INPUTS\n# END GENERATED MODULE INPUTS\n", encoding="utf-8")
            destination = root / "notebooks"
            students.export_notebooks(destination, root=root)
            students.export_notebooks(destination, check=True, root=root)
            self.assertEqual(len(list(destination.glob("*.Rmd"))), 9)
            (destination / "module_01_topic.Rmd").unlink()
            (destination / "module_02_topic.Rmd").write_text("stale", encoding="utf-8")
            (destination / "module_04_old.Rmd").write_text("old", encoding="utf-8")
            before = {p.name: p.read_bytes() for p in destination.iterdir()}
            with self.assertRaises(SystemExit) as error:
                students.export_notebooks(destination, check=True, root=root)
            for name in ("module_01_topic.Rmd", "module_02_topic.Rmd", "module_04_old.Rmd"):
                self.assertIn(name, str(error.exception))
            self.assertEqual(before, {p.name: p.read_bytes() for p in destination.iterdir()})
            with patch.object(students, "build_models", return_value=models[:2]):
                with self.assertRaises(ValueError):
                    students.export_notebooks(destination, check=True, root=root)
                students.export_notebooks(destination, root=root)
                with self.assertRaises(SystemExit):
                    students.export_notebooks(destination, check=True, root=root)

    def test_data_only_prerequisites(self):
        spec = {"checkpoint": None, "restart_step": None, "files": [{"base": "data", "path": "input.tsv"}]}
        self.assertEqual(exports.module_prerequisites({"prerequisites": spec}), spec)
        for change in ({"restart_step": "1.1"}, {"files": [{"base": "output", "path": "state.pgen"}]}):
            with self.assertRaises(ValueError):
                exports.module_prerequisites({"prerequisites": {**spec, **change}})


class QuartoRendererTests(unittest.TestCase):
    """The qmd renderer is optional output. It must not change the default or the Rmd files."""

    CHUNK = "\n".join([
        "```{r s9-9}",
        "# 1. Choose the input.",
        'input <- guided_path(cfg, "2.8")',
        "# 2. Remove poor samples.",
        "run_plink(cfg, c(",
        '  "--pfile", input))',
        "# Course bookkeeping: records the counts for the next step. Do not change.",
        'guided_register(cfg, "9.9", "2.8", 1, 2)',
        "```"])

    def test_command_titles_are_not_repeated(self):
        group = lambda label: {"label": label, "options": [{"name": "--glm", "explanation": "Fits a model."}]}
        record = {"option_groups": [group("Command 1: first job"), group("second job")], "terminal_commands": ["bin/plink2 --glm --threads 2 --memory 2048"]}
        text = chr(10).join(students.option_table_lines(record))
        self.assertIn("**Command 1: first job**", text)
        self.assertIn("**Command 2: second job**", text)
        self.assertNotIn("Command 1: Command", text)
        for path in (ROOT / "lessons").glob("module_0*.Rmd"):
            self.assertNotRegex(path.read_text(encoding="utf-8"), r'"label": "Command \d')

    def test_default_format_stays_rmd(self):
        self.assertEqual(students.DEFAULT_FORMAT, "rmd")
        self.assertEqual(set(students.RENDERERS), {"rmd", "qmd"})

    def test_numbered_comments_become_code_annotations(self):
        lines = students.qmd_chunk(self.CHUNK)
        self.assertEqual(lines[:3], ["```{r}", "#| label: s9-9", 'input <- guided_path(cfg, "2.8")  # <1>'])
        self.assertIn("run_plink(cfg, c(  # <2>", lines)
        self.assertIn("# Course bookkeeping: records the counts for the next step. Do not change.", lines)
        self.assertNotIn("# 1. Choose the input.", lines)
        self.assertEqual(lines[-3:], ["1. Choose the input.", "2. Remove poor samples.", ""])

    def test_chunk_without_numbered_comments_has_no_list(self):
        lines = students.qmd_chunk("```{r setup}\nx <- 1\n```")
        self.assertEqual(lines, ["```{r}", "#| label: setup", "x <- 1", "```", ""])

    def test_eval_false_option_is_kept_and_other_options_fail(self):
        lines = students.qmd_chunk("```{r a, eval=FALSE}\ninstall.packages('x')\n```")
        self.assertEqual(lines[:3], ["```{r}", "#| label: a", "#| eval: false"])
        with self.assertRaises(ValueError):
            students.qmd_chunk("```{r a, echo=FALSE}\nx\n```")

    def test_bad_numbering_fails(self):
        for body in ("# 2. Starts at two.\nx <- 1",
                     "# 1. First.\n# 2. Second without code.\nx <- 1",
                     "x <- 1\n# 1. Trailing comment without code."):
            with self.subTest(body=body), self.assertRaises(ValueError):
                students.qmd_chunk("```{r a}\n" + body + "\n```")

    def test_every_module_renders_with_callouts_and_no_rmd_front_matter(self):
        models = students.build_models()
        outputs = students.notebook_outputs(models, "qmd")
        rmd = students.notebook_outputs(models, "rmd")
        self.assertEqual({n.replace(".qmd", "") for n in outputs}, {n.replace(".Rmd", "") for n in rmd})
        for name, text in outputs.items():
            twin = rmd[name.replace(".qmd", ".Rmd")]
            with self.subTest(name=name):
                self.assertTrue(text.startswith("---\ntitle:"))
                self.assertIn("editor: visual", text)
                self.assertNotIn("html_notebook", text)
                self.assertNotIn("execute:", text)
                self.assertEqual(text.count("```{r}"), text.count("#| label:"))
                self.assertEqual(text.count("### What each option does"), twin.count("### What each option does"))
                self.assertEqual(text.count('{.callout-tip title="Expected result" collapse="true"}'),
                                 twin.count("### Expected result"))
                self.assertEqual(text.count('{.callout-note title="PLINK terminal equivalent"}'),
                                 twin.count("### PLINK terminal equivalent"))
                self.assertNotIn("—", text)

    def test_qmd_export_and_check_use_their_own_suffix(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            students.export_notebooks(destination, format="qmd")
            self.assertEqual(len(list(destination.glob("*.qmd"))), 9)
            self.assertEqual(list(destination.glob("*.Rmd")), [])
            students.export_notebooks(destination, check=True, format="qmd")
            (destination / "module_03_sample_quality_control.qmd").write_text("stale", encoding="utf-8")
            with self.assertRaises(SystemExit):
                students.export_notebooks(destination, check=True, format="qmd")


if __name__ == "__main__":
    unittest.main()
