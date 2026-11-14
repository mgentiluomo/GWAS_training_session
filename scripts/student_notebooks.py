"""Generate the module 3 student notebook from the canonical lesson.

Generate: python -B scripts/build_tutorial.py --export-notebooks notebooks
Check: python -B scripts/build_tutorial.py --export-notebooks notebooks --check-notebooks
The pilot deliberately exports no other module or complete-course notebook.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

from course_exports import CHUNK, ROOT, export_modules, export_steps, student_plink_resources


def notebook_links(text: str) -> str:
    """The export uses root-relative repository paths; notebooks/ needs ../."""
    return re.sub(r"(\]\()((?:docs|examples|lessons)/[^)\s]+)(\))", r"\1../\2\3", text)


def module_three(root: Path = ROOT) -> tuple[str, str]:
    module = next(item for item in export_modules(root) if item["module"] == 3)
    records = [item for item in export_steps(root) if item["module"] == 3]
    source = root / module["source"]
    source_text = source.read_text(encoding="utf-8")
    lines = [
        "---", 'title: "Module 3: Sample quality control"', "output: html_notebook",
        f'course_source_sha256: "{module["source_sha256"]}"', "---", "",
        "Open `GWAS_course.Rproj` and work from the project root. Run the chunks in order in a fresh R session.",
        "All data are simulated. Read each summary, run its chunk and compare your result with the expected result.",
        "The linked step pages explain the ideas and provide troubleshooting.", "",
        "You need the full [checkpoint at step 2.8](https://www.manuelgentiluomo.it/teaching/gwas/module-2/step-2-8) before you start.", "",
        "```{r module3_check}",
        'if (!file.exists("config.R") && file.exists("../config.R")) setwd("..")',
        'source("R/guided.R"); guided_check_module(3)', "```", "",
        "```{r module3_setup}", records[0]["setup_code"], "```", "",
    ]
    chunks = {m.group(1): m for m in CHUNK.finditer(source_text)}
    for record in records:
        if "student_summary" not in record or "student_plink_options" not in record or "student_expected_result" not in record:
            raise ValueError(f"Missing student fields in step {record['id']}.")
        lines.extend([
            f'## Step {record["id"]} · {record["title"]}', "", record["student_summary"], "",
            f'[Read step {record["id"]} on the course website](https://www.manuelgentiluomo.it/teaching/gwas/module-3/{record["anchor"]}).', "",
        ])
        if record["r_commands"]:
            for command in record["r_commands"]:
                # Preserve the complete original fence, chunk options and literal code.
                lines.extend([chunks[command["label"]].group().rstrip(), ""])
        else:
            lines.extend(["No code to run in this step", ""])
        lines.extend(["### What each option does", ""])
        if record["student_plink_options"]:
            for index, group in enumerate(record["student_plink_options"], 1):
                if len(record["student_plink_options"]) > 1:
                    lines.extend([f'**Command {index}: {group["label"]}**', ""])
                lines.extend(["| Option or modifier | What it does |", "| --- | --- |"])
                for option in group["options"]:
                    explanation = option["explanation"].replace("|", "\\|")
                    lines.append(f'| `{option["name"]}` | {explanation} |')
                    for modifier in option.get("modifiers", []):
                        explanation = modifier["explanation"].replace("|", "\\|")
                        lines.append(f'| &nbsp;&nbsp;&rarr; `{modifier["name"]}` | {explanation} |')
                lines.append("")
            resources = [student_plink_resources(command) for command in record["plink"]["commands"]]
            threads = resources[0]["--threads"]
            memory = resources[0]["--memory"]
            threads_word = {2: "two"}[threads]
            lines.extend([
                f"Every command also uses `--threads {threads}` (PLINK runs at most {threads_word} tasks at the same time) "
                f"and `--memory {memory}` (PLINK uses at most about {memory // 1024} GB of memory).", ""])
        else:
            lines.extend(["No PLINK options are used in this step.", ""])
        lines.extend(["### Expected result", "", notebook_links(record["student_expected_result"]), "",
                      "### PLINK terminal equivalent", ""])
        if record["plink"]["commands"]:
            lines.extend(["These commands are shown for reference. Run the R chunk above to follow the course.",
                          "R creates any lists needed between PLINK commands. On Windows, use `bin\\plink2.exe`.",
                          "", "```sh", *record["plink"]["commands"], "```", ""])
        else:
            lines.extend(["No PLINK equivalent", ""])
    return source.name, "\n".join(lines).rstrip() + "\n"


def module_check_table(root: Path = ROOT) -> str:
    """Generate the small R prerequisite table from the lesson's module_meta."""
    module = next(item for item in export_modules(root) if item["module"] == 3)
    spec = module["prerequisites"]
    quote = lambda value: json.dumps(value, ensure_ascii=False)
    rows = ["# BEGIN GENERATED MODULE 3 INPUTS", "# Source: module_meta in lessons/module_03_sample_quality_control.Rmd.",
            "# Regenerate with --export-notebooks; do not edit this table.",
            "guided_module_inputs <- list(`3` = list(",
            f'  checkpoint = {quote(spec["checkpoint"])}, restart_step = {quote(spec["restart_step"])},']
    for base in ("data", "output"):
        values = ", ".join(quote(entry["path"]) for entry in spec["files"] if entry["base"] == base)
        rows.append(f'  {base} = c({values})' + ("," if base == "data" else "))"))
    return "\n".join(rows + ["# END GENERATED MODULE 3 INPUTS"])


def sync_module_check(root: Path, check: bool) -> None:
    path = root / "R/guided.R"
    text = path.read_text(encoding="utf-8")
    pattern = r"# BEGIN GENERATED MODULE 3 INPUTS.*?# END GENERATED MODULE 3 INPUTS"
    match = re.search(pattern, text, re.S)
    expected = module_check_table(root)
    if not match:
        raise ValueError("R/guided.R needs the generated module input table.")
    if check and match.group() != expected:
        raise ValueError("R/guided.R and module_meta disagree. Regenerate with --export-notebooks.")
    if not check and match.group() != expected:
        path.write_text(text[:match.start()] + expected + text[match.end():], encoding="utf-8", newline="\n")


def export_notebooks(destination: Path, check: bool = False, root: Path = ROOT) -> None:
    sync_module_check(root, check)
    name, content = module_three(root)
    path = destination / name
    expected = content.encode("utf-8")
    if check:
        # Git may check out CRLF on Windows. Only line endings may differ.
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            raise SystemExit(f"Student notebook is missing or out of date: {path}. Regenerate with --export-notebooks {destination}.")
        print(f"Student notebook is up to date: {path}")
        return
    destination.mkdir(parents=True, exist_ok=True)
    path.write_bytes(expected)
    print(f"Exported student pilot: {path}")
