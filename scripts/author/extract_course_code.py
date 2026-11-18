"""Write every R snippet of the course pages and notebooks to one folder, one file per snippet.

Used by the function coverage check (check_function_coverage.R and its test). Read only: nothing is run.

    python scripts/author/extract_course_code.py OUT_FOLDER --steps site_content/steps --notebooks notebooks
    python scripts/author/extract_course_code.py OUT_FOLDER --git-repo C:/WEB_site/sito --git-ref main

A file is named STEP__SOURCE__LABEL.R. STEP is the step id (for example 7-6) or the notebook name. The R checker
reads the files of one step together, so a function that a step defines for itself is not reported.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

FENCE = re.compile(r"^```\{r([^\n}]*)\}\n(.*?)^```\s*$", re.M | re.S)
PLAIN_FENCE = re.compile(r"^```r\n(.*?)^```\s*$", re.M | re.S)


def snippets_of_markdown(text: str):
    """Yield (label, code) for the R fences of a markdown text."""
    for index, m in enumerate(FENCE.finditer(text)):
        label = (m.group(1).strip().split(",")[0].strip() or f"chunk{index}")
        yield re.sub(r"[^A-Za-z0-9_.-]", "_", label), m.group(2)
    for index, m in enumerate(PLAIN_FENCE.finditer(text)):
        yield f"plain{index}", m.group(1)


def snippets_of_step(record: dict):
    step = record["id"].replace(".", "-")
    if record.get("setup_code"):
        yield step, "setup", record["setup_code"]
    for command in record.get("r_commands") or []:
        yield step, "cmd_" + re.sub(r"[^A-Za-z0-9_.-]", "_", command["label"]), command["code"]
    for block_name, block in (record.get("blocks") or {}).items():
        for label, code in snippets_of_markdown(block):
            yield step, f"{block_name}_{label}", code


def snippets_of_notebook(name: str, text: str):
    for label, code in snippets_of_markdown(text):
        m = re.match(r"s(\d)-(\d)", label)
        step = f"{m.group(1)}-{m.group(2)}" if m else name
        yield step, "nb_" + label, code


def git_show(repo: str, ref: str, path: str) -> str:
    return subprocess.run(["git", "-C", repo, "show", f"{ref}:{path}"], check=True, capture_output=True).stdout.decode("utf-8")


def git_files(repo: str, ref: str, folder: str, suffix: str) -> list[str]:
    out = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "--name-only", ref, folder], check=True, capture_output=True).stdout.decode("utf-8")
    return [line for line in out.splitlines() if line.endswith(suffix)]


def write(out: Path, step: str, source: str, label: str, code: str, seen: dict) -> None:
    name = f"{step}__{source}__{label}.R"
    seen[name] = seen.get(name, 0) + 1
    if seen[name] > 1:
        name = f"{step}__{source}__{label}_{seen[name]}.R"
    (out / name).write_text(code.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("out", type=Path)
    parser.add_argument("--steps", type=Path, help="Folder of step JSON files (site_content/steps).")
    parser.add_argument("--notebooks", type=Path, help="Folder of .qmd notebooks.")
    parser.add_argument("--git-repo", help="Read the site files of a git repository instead of folders (no checkout).")
    parser.add_argument("--git-ref", default="main")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    seen: dict = {}
    count = 0
    if args.git_repo:
        for path in git_files(args.git_repo, args.git_ref, "src/content/gwas/steps", ".json"):
            for step, label, code in snippets_of_step(json.loads(git_show(args.git_repo, args.git_ref, path))):
                write(args.out, step, "site", label, code, seen); count += 1
        for path in git_files(args.git_repo, args.git_ref, "public/gwas/notebooks", ".qmd"):
            for step, label, code in snippets_of_notebook(Path(path).stem, git_show(args.git_repo, args.git_ref, path)):
                write(args.out, step, "notebook", label, code, seen); count += 1
    else:
        if args.steps:
            for path in sorted(args.steps.glob("step-*.json")):
                for step, label, code in snippets_of_step(json.loads(path.read_text(encoding="utf-8"))):
                    write(args.out, step, "site", label, code, seen); count += 1
        if args.notebooks:
            for path in sorted(args.notebooks.glob("*.qmd")):
                for step, label, code in snippets_of_notebook(path.stem, path.read_text(encoding="utf-8")):
                    write(args.out, step, "notebook", label, code, seen); count += 1
    print(f"{count} R snippets written to {args.out}")


if __name__ == "__main__":
    main()
