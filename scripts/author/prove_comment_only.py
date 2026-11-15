"""Prove that executable course code differs from a Git revision only by comments.

Run from any directory: python -B scripts/author/prove_comment_only.py --base REV
No Git or working-tree mutations are performed.
"""
from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
R_CHUNK = re.compile(r"^```\{r([^}]*)\}[^\S\r\n]*\r?\n(.*?)^```[^\S\r\n]*$", re.M | re.S)
HASH_LINE = re.compile(r"^\s*#\s*(?:.*source.*hash|.*sha[- ]?\d+|.*source.*checksum)\s*:", re.I)


def code_difference(before: str, after: str) -> str | None:
    """Permit added comment-only lines and changed source-hash comments only."""
    old = before.splitlines()
    new = after.splitlines()
    executable = lambda lines: [line for line in lines if not line.lstrip().startswith("#")]
    if executable(old) != executable(new):
        return "\n".join(list(difflib.unified_diff(executable(old), executable(new),
                                                 fromfile="base", tofile="working", lineterm=""))[:12])
    old = [line for line in old if not HASH_LINE.match(line)]
    new = [line for line in new if not HASH_LINE.match(line)]
    # Existing comments must remain, in order. Only inserted comments are allowed.
    index = 0
    for line in new:
        if index < len(old) and line == old[index]:
            index += 1
        elif not line.lstrip().startswith("#"):
            return "Existing lines were removed or reordered."
    if index != len(old):
        return "An existing line or comment was removed or changed."
    return None


def compare_content(path: str, before: str, after: str) -> list[str]:
    if path.endswith(".Rmd"):
        def chunks(text):
            return [(m.group(1).strip() or "<unnamed>", m.group(1), m.group(2)) for m in R_CHUNK.finditer(text)]
        old, new = chunks(before), chunks(after)
        if [(x[0], x[1]) for x in old] != [(x[0], x[1]) for x in new]:
            return ["R chunks or chunk options changed."]
        pairs = [(label, code, new[i][2]) for i, (label, _, code) in enumerate(old)]
    elif path.endswith(".json"):
        old, new = json.loads(before)["r_commands"], json.loads(after)["r_commands"]
        if [{k: v for k, v in c.items() if k != "code"} for c in old] != [
                {k: v for k, v in c.items() if k != "code"} for c in new]:
            return ["r_commands structure or metadata changed."]
        pairs = [(c["label"], c["code"], new[i]["code"]) for i, c in enumerate(old)]
    else:
        pairs = [(path, before, after)]
    differences = []
    for label, old_code, new_code in pairs:
        difference = code_difference(old_code, new_code)
        if difference:
            differences.append(f"{label}: {difference}")
    return differences


def prove(base: str, root: Path = ROOT) -> list[str]:
    def git(*args):
        return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True).stdout.decode("utf-8")
    paths = {p.relative_to(root).as_posix() for pattern in ("lessons/*.Rmd", "site_content/steps/*.json")
             for p in root.glob(pattern)}
    paths.update(line for line in git("ls-tree", "-r", "--name-only", base, "--", "lessons", "site_content/steps").splitlines()
                 if re.fullmatch(r"lessons/[^/]+\.Rmd|site_content/steps/[^/]+\.json", line))
    paths.add("scripts/run_main_path.R")
    differences = []
    for path in sorted(paths):
        try:
            old = git("show", f"{base}:{path}")
            new = (root / path).read_text(encoding="utf-8")
            differences.extend(f"{path}: {message}" for message in compare_content(path, old, new))
        except (subprocess.CalledProcessError, OSError, ValueError, KeyError) as error:
            differences.append(f"{path}: cannot compare ({type(error).__name__}).")
    return differences


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    args = parser.parse_args()
    try:
        differences = prove(args.base)
    except subprocess.CalledProcessError:
        parser.exit(1, "Cannot read the base revision.\n")
    if differences:
        parser.exit(1, "\n".join(differences[:20]) + "\n")
    print("Comment-only proof passed for lesson R chunks, main-path script and exported R commands.")


if __name__ == "__main__":
    main()
