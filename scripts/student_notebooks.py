"""Build student notebook models and render enabled main-path modules.

Generate: python -B scripts/build_tutorial.py --export-notebooks notebooks
Check: python -B scripts/build_tutorial.py --export-notebooks notebooks --check-notebooks
"""
from __future__ import annotations

import json
from pathlib import Path
import re

from course_exports import CHUNK, ROOT, export_modules, export_steps, student_plink_resources


def notebook_links(text: str) -> str:
    """The export uses root-relative repository paths; notebooks/ needs ../."""
    return re.sub(r"(\]\()((?:docs|examples|lessons)/[^)\s]+)(\))", r"\1../\2\3", text)


def build_models(root: Path = ROOT) -> list[dict]:
    """Return plain structured models, independent of the output format.

    Incomplete modules stay disabled while authors add fields step by step.
    Module 0 has no inputs beyond the project root.
    """
    records = export_steps(root)
    models = []
    for module in sorted(export_modules(root), key=lambda m: m["module"]):
        steps = [r for r in records if r["module"] == module["module"]]
        def ready(record):
            kind = record.get("student_kind", "code" if record["r_commands"] else None)
            return ("student_summary" in record and kind in {"code", "reading", "outside_r"}
                    and (kind != "code" or all(k in record for k in ("student_plink_options", "student_expected_result")))
                    and (kind != "outside_r" or "student_action" in record))
        if not steps or not all(ready(r) for r in steps):
            continue
        number = module["module"]
        spec = module.get("prerequisites")
        if number == 0:
            spec = spec or {"checkpoint": None, "restart_step": None, "files": []}
            if spec != {"checkpoint": None, "restart_step": None, "files": []}:
                raise ValueError("Module 0 needs only the project root.")
        elif spec is None:
            raise ValueError(f"Enabled module {number} needs module_meta prerequisites.")
        chunks = {m.group(1): m.group().rstrip() for m in CHUNK.finditer(
            (root / module["source"]).read_text(encoding="utf-8"))}
        model_steps = []
        for record in steps:
            # Validate even when callers supply exported fixtures directly.
            from course_exports import step_metadata
            step_metadata({k: v for k, v in record.items() if k in {
                "student_summary", "student_kind", "student_action", "student_plink_options"}}, record)
            model_steps.append({
                "id": record["id"], "title": record["title"], "anchor": record["anchor"],
                "summary": record["student_summary"], "kind": record.get("student_kind", "code"),
                "action": record.get("student_action"),
                "chunks": [chunks[c["label"]] for c in record["r_commands"]],
                "option_groups": record.get("student_plink_options", []),
                "expected_result": record.get("student_expected_result", ""),
                "terminal_commands": record["plink"]["commands"],
            })
        models.append({"module": number, "title": module["title"], "prerequisites": spec,
                       "source": module["source"], "source_sha256": module["source_sha256"],
                       "setup_code": next((r["setup_code"] for r in steps if r["setup_code"]), ""),
                       "steps": model_steps})
    return models


ROOT_CHECK = [
    'if (!file.exists("config.R") || !file.exists("R/guided.R")) {',
    '  stop("Open GWAS_course.Rproj and run this notebook from the project root.", call. = FALSE)',
    '}',
    'if (requireNamespace("knitr", quietly = TRUE)) knitr::opts_knit$set(root.dir = normalizePath("."))',
]


def check_chunk(model: dict) -> list[str]:
    number = model["module"]
    return [f"```{{r module{number}_check}}",
            'if (!file.exists("config.R") && file.exists("../config.R")) setwd("..")',
            *(ROOT_CHECK if number == 0 else [f'source("R/guided.R"); guided_check_module({number})']),
            "```", ""]


def render_rmd(models: list[dict], complete: bool = False) -> str:
    module = models[0]
    number = module["module"]
    title = "GWAS course: modules 0 to 7" if complete else f'Module {number}: {module["title"]}'
    lines = [
        "---", f'title: {json.dumps(title, ensure_ascii=False)}', "output: html_notebook",
        *([] if complete else [f'course_source_sha256: "{module["source_sha256"]}"']), "---", "",
        "Open `GWAS_course.Rproj` and work from the project root. Run the chunks in order in a fresh R session.",
        "All data are simulated. Read each summary, run its chunk and compare your result with the expected result.",
        "The linked step pages explain the ideas and provide troubleshooting.", "",
    ]
    setup_written = False
    for model in models:
        number = model["module"]
        if complete:
            lines.extend([f'# Module {number}: {model["title"]}', ""])
        elif model["prerequisites"]["checkpoint"] is not None:
            checkpoint = model["prerequisites"]["checkpoint"]
            previous = checkpoint.split(".")[0]
            anchor = checkpoint.replace(".", "-")
            lines.extend([f"You need the full [checkpoint at step {checkpoint}](https://www.manuelgentiluomo.it/teaching/gwas/module-{previous}/step-{anchor}) before you start.", ""])
        lines.extend(check_chunk(model))
        if model["setup_code"] and not setup_written:
            lines.extend([f"```{{r module{number}_setup}}", model["setup_code"], "```", ""])
            setup_written = True
        lines.extend(render_steps_rmd(model))
    return "\n".join(lines).rstrip() + "\n"


def option_table_lines(record: dict) -> list[str]:
    """The "What each option does" section, shared by every output format."""
    lines = []
    lines.extend(["### What each option does", ""])
    if record["option_groups"]:
        for index, group in enumerate(record["option_groups"], 1):
            if len(record["option_groups"]) > 1:
                lines.extend([f'**Command {index}: {group["label"]}**', ""])
            lines.extend(["| Option or modifier | What it does |", "| --- | --- |"])
            for option in group["options"]:
                explanation = option["explanation"].replace("|", "\\|")
                lines.append(f'| `{option["name"]}` | {explanation} |')
                for modifier in option.get("modifiers", []):
                    explanation = modifier["explanation"].replace("|", "\\|")
                    lines.append(f'| &nbsp;&nbsp;&rarr; `{modifier["name"]}` | {explanation} |')
            lines.append("")
        resources = [student_plink_resources(command) for command in record["terminal_commands"]]
        threads = resources[0]["--threads"]
        memory = resources[0]["--memory"]
        threads_word = {2: "two"}[threads]
        lines.extend([
            f"Every command also uses `--threads {threads}` (PLINK runs at most {threads_word} tasks at the same time) "
            f"and `--memory {memory}` (PLINK uses at most about {memory // 1024} GB of memory).", ""])
    else:
        lines.extend(["No PLINK options are used in this step.", ""])
    return lines


def render_steps_rmd(model: dict) -> list[str]:
    lines = []
    records = model["steps"]
    for record in records:
        lines.extend([
            f'## Step {record["id"]} · {record["title"]}', "", record["summary"], "",
            f'[Read step {record["id"]} on the course website](https://www.manuelgentiluomo.it/teaching/gwas/module-{model["module"]}/{record["anchor"]}).', "",
        ])
        if record["kind"] != "code":
            if record["kind"] == "reading":
                lines.extend(["This step is reading only. There is no code to run.", ""])
            else:
                lines.extend(["No code to run in this step.", "", f'What you do: {record["action"]}', ""])
            continue
        for chunk in record["chunks"]:
            lines.extend([chunk, ""])
        lines.extend(option_table_lines(record))
        lines.extend(["### Expected result", "", notebook_links(record["expected_result"]), "",
                      "### PLINK terminal equivalent", ""])
        if record["terminal_commands"]:
            lines.extend(["These commands are shown for reference. Run the R chunk above to follow the course.",
                          "R creates any lists needed between PLINK commands. On Windows, use `bin\\plink2.exe`.",
                          "", "```sh", *record["terminal_commands"], "```", ""])
        else:
            lines.extend(["No PLINK equivalent", ""])
    return lines


CHUNK_HEADER = re.compile(r"^```\{r ([^,}\s]+)(?:,\s*([^}]*))?\}$")
NUMBERED_COMMENT = re.compile(r"^(\s*)# (\d+)\. (.*)$")


def qmd_chunk(chunk: str) -> list[str]:
    """Turn an R Markdown chunk into a Quarto chunk with code annotations.

    A numbered comment such as `# 1. Text` becomes a trailing `# <1>` on the next
    line of code, and the text moves to a numbered list under the chunk. Other
    comments, including the course bookkeeping comment, stay in the code.
    """
    lines = chunk.split("\n")
    header = CHUNK_HEADER.match(lines[0])
    if not header or lines[-1] != "```":
        raise ValueError(f"Unsupported chunk for Quarto output: {lines[0]!r}")
    options = [f"#| label: {header[1]}"]
    for option in filter(None, (o.strip() for o in (header[2] or "").split(","))):
        if option != "eval=FALSE":
            raise ValueError(f"Unsupported chunk option for Quarto output: {option!r}")
        options.append("#| eval: false")
    code, explanations, pending = [], [], None
    for line in lines[1:-1]:
        numbered = NUMBERED_COMMENT.match(line)
        if numbered:
            if pending is not None:
                raise ValueError("Two numbered comments without code between them.")
            pending = (numbered[2], numbered[3])
            continue
        if pending is not None and line.strip() and not line.lstrip().startswith("#"):
            if pending[0] != str(len(explanations) + 1):
                raise ValueError("Numbered comments must count 1, 2, 3 in order within a chunk.")
            code.append(f"{line}  # <{pending[0]}>")
            explanations.append(f"{pending[0]}. {pending[1]}")
            pending = None
        else:
            code.append(line)
    if pending is not None:
        raise ValueError("A numbered comment has no code after it.")
    out = ["```{r}", *options, *code, "```", ""]
    return out + (explanations + [""] if explanations else [])


def render_qmd(models: list[dict], complete: bool = False) -> str:
    module = models[0]
    title = "GWAS course: modules 0 to 7" if complete else f'Module {module["module"]}: {module["title"]}'
    lines = ["---", f"title: {json.dumps(title, ensure_ascii=False)}", "format:", "  html:", "    toc: true",
             "    embed-resources: true", "editor: visual",
             *([] if complete else [f'course_source_sha256: "{module["source_sha256"]}"']), "---", "",
             "Open `GWAS_course.Rproj` and work from the project root. Run the chunks in order in a fresh R session.",
             "All data are simulated. Read each summary, run its chunk and compare your result with the expected result.",
             "The linked step pages explain the ideas and provide troubleshooting.", ""]
    setup_written = False
    for model in models:
        number = model["module"]
        if complete:
            lines.extend([f'# Module {number}: {model["title"]}', ""])
        elif model["prerequisites"]["checkpoint"] is not None:
            checkpoint = model["prerequisites"]["checkpoint"]
            previous = checkpoint.split(".")[0]
            anchor = checkpoint.replace(".", "-")
            lines.extend([f"You need the full [checkpoint at step {checkpoint}](https://www.manuelgentiluomo.it/teaching/gwas/module-{previous}/step-{anchor}) before you start.", ""])
        lines.extend(qmd_chunk("\n".join(check_chunk(model)).rstrip("\n")))
        if model["setup_code"] and not setup_written:
            lines.extend(qmd_chunk("\n".join([f"```{{r module{number}_setup}}", model["setup_code"], "```"])))
            setup_written = True
        lines.extend(render_steps_qmd(model))
    return "\n".join(lines).rstrip() + "\n"


def render_steps_qmd(model: dict) -> list[str]:
    lines = []
    for record in model["steps"]:
        lines.extend([
            f'## Step {record["id"]} · {record["title"]}', "", record["summary"], "",
            f'[Read step {record["id"]} on the course website](https://www.manuelgentiluomo.it/teaching/gwas/module-{model["module"]}/{record["anchor"]}).', "",
        ])
        if record["kind"] != "code":
            if record["kind"] == "reading":
                lines.extend(["This step is reading only. There is no code to run.", ""])
            else:
                lines.extend(["No code to run in this step.", "", f'What you do: {record["action"]}', ""])
            continue
        for chunk in record["chunks"]:
            lines.extend(qmd_chunk(chunk))
        lines.extend(option_table_lines(record))
        lines.extend(['::: {.callout-tip title="Expected result" collapse="true"}', "",
                      notebook_links(record["expected_result"]), ":::", ""])
        if record["terminal_commands"]:
            lines.extend(['::: {.callout-note title="PLINK terminal equivalent"}', "",
                          "These commands are shown for reference. Run the R chunk above to follow the course.",
                          "R creates any lists needed between PLINK commands. On Windows, use `bin\\plink2.exe`.",
                          "", "```sh", *record["terminal_commands"], "```", ":::", ""])
        else:
            lines.extend(['::: {.callout-note title="PLINK terminal equivalent"}', "", "No PLINK equivalent", ":::", ""])
    return lines


# Quarto output is available with --notebook-format qmd. To make it the default, change DEFAULT_FORMAT.
RENDERERS = {"rmd": render_rmd, "qmd": render_qmd}
DEFAULT_FORMAT = "rmd"


def notebook_outputs(models: list[dict], format: str = DEFAULT_FORMAT) -> dict[str, str]:
    renderer = RENDERERS[format]
    suffix = ".Rmd" if format == "rmd" else "." + format
    outputs = {Path(m["source"]).with_suffix(suffix).name: renderer([m]) for m in models}
    if {m["module"] for m in models} == set(range(8)):
        outputs["gwas_course_complete" + suffix] = renderer(sorted(models, key=lambda m: m["module"]), complete=True)
    return outputs


def module_three(root: Path = ROOT) -> tuple[str, str]:
    """Compatibility entry point for the original pilot checks."""
    model = next(m for m in build_models(root) if m["module"] == 3)
    return Path(model["source"]).name, render_rmd([model])


def module_check_table(root: Path = ROOT, models: list[dict] | None = None) -> str:
    """Generate the small R prerequisite table from the lesson's module_meta."""
    models = build_models(root) if models is None else models
    quote = lambda value: "NULL" if value is None else json.dumps(value, ensure_ascii=False)
    rows = ["# BEGIN GENERATED MODULE INPUTS", "# Sources: module_meta in enabled lessons (module 0 needs only the project root).",
            "# Regenerate with --export-notebooks; do not edit this table.",
            "guided_module_inputs <- list("]
    for index, module in enumerate(models):
        spec = module["prerequisites"]
        rows.extend([f'`{module["module"]}` = list(',
                     f'  checkpoint = {quote(spec["checkpoint"])}, restart_step = {quote(spec["restart_step"])},'])
        for base in ("data", "output"):
            values = ", ".join(quote(entry["path"]) for entry in spec["files"] if entry["base"] == base)
            vector = f"c({values})" if values else "character(0)"
            rows.append(f'  {base} = {vector}' + ("," if base == "data" else ")" + ("," if index < len(models) - 1 else "")))
    rows.append(")")
    # The inline module 0 check and guided_check_module share this generated definition.
    rows.extend(["guided_check_project_root <- function() {", *["  " + line for line in ROOT_CHECK],
                 "  invisible(TRUE)", "}"])
    return "\n".join(rows + ["# END GENERATED MODULE INPUTS"])


def sync_module_check(root: Path, check: bool, models: list[dict] | None = None) -> None:
    path = root / "R/guided.R"
    text = path.read_text(encoding="utf-8")
    pattern = r"# BEGIN GENERATED MODULE(?: 3)? INPUTS.*?# END GENERATED MODULE(?: 3)? INPUTS"
    match = re.search(pattern, text, re.S)
    expected = module_check_table(root, models)
    if not match:
        raise ValueError("R/guided.R needs the generated module input table.")
    if check and match.group() != expected:
        raise ValueError("R/guided.R and module_meta disagree. Regenerate with --export-notebooks.")
    if not check and match.group() != expected:
        path.write_text(text[:match.start()] + expected + text[match.end():], encoding="utf-8", newline="\n")


def export_notebooks(destination: Path, check: bool = False, root: Path = ROOT, format: str = DEFAULT_FORMAT) -> None:
    models = build_models(root)
    outputs = notebook_outputs(models, format)
    suffix = ".Rmd" if format == "rmd" else "." + format
    sync_module_check(root, check, models)
    generated_name = re.compile(r"(?:module_0[0-7]_.+|gwas_course_complete)" + re.escape(suffix) + "$")
    unexpected = sorted(p.name for p in destination.glob("*" + suffix)
                        if generated_name.fullmatch(p.name) and p.name not in outputs)
    if check:
        # Git may check out CRLF on Windows. Only line endings may differ.
        stale = [name for name, content in outputs.items() if not (destination / name).is_file()
                 or (destination / name).read_text(encoding="utf-8") != content]
        if stale or unexpected:
            raise SystemExit(f"Student notebooks missing or out of date: {stale}; unexpected: {unexpected}. Regenerate with --export-notebooks {destination}.")
        print(f"Student notebooks are up to date: {len(outputs)} files in {destination}")
        return
    destination.mkdir(parents=True, exist_ok=True)
    for name, content in outputs.items():
        path = destination / name
        # Avoid changing existing bytes solely because of Windows checkout newlines.
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            path.write_bytes(content.encode("utf-8"))
        print(f"Exported student notebook: {path}")
    if unexpected:
        print(f"Unexpected notebooks retained for author review: {unexpected}")
