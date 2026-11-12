"""Check student-facing text rules: dashes, UK spelling, module frame, glossary links.

Run from the project root: python -B scripts/check_text.py
Exit status 1 when a hard rule fails. Long sentences are reported as warnings only.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
FENCE = re.compile(r"^```.*?^```\s*$", re.M | re.S)
INLINE = re.compile(r"`[^`\n]*`")
COMMENT = re.compile(r"<!--.*?-->", re.S)
EM_DASH = "—"
# American spellings that must not appear in prose (option names live in code and are skipped).
US = re.compile(
    r"\b(analy[sz]e[sd]?|analyzing|normali[sz]e[sd]?|summari[sz]e[sd]?|organi[sz]e[sd]?|"
    r"recogni[sz]e[sd]?|minimi[sz]e[sd]?|maximi[sz]e[sd]?|randomi[sz]ation|randomi[sz]e[sd]?|"
    r"standardi[sz]e[sd]?|visuali[sz]e[sd]?|colou?rs?|behaviou?rs?|center(?:ed|s)?|"
    r"favou?rite|licen[cs]e)\b", re.I)
US_BAD = {"analyze", "analyzed", "analyzes", "analyzing", "normalize", "normalized", "normalizes",
          "summarize", "summarized", "summarizes", "organize", "organized", "recognize", "recognized",
          "minimize", "minimized", "maximize", "maximized", "randomization", "randomize", "randomized",
          "standardize", "standardized", "visualize", "visualized", "color", "colors", "behavior",
          "behaviors", "center", "centered", "centers", "favorite"}
GLOSSARY_LINK = re.compile(r"glossary\.md#([a-z0-9-]+)")
GLOSSARY_ANCHOR = re.compile(r"\{#([a-z0-9-]+)\}")


def prose(text: str) -> str:
    text = COMMENT.sub("", text)
    text = FENCE.sub("", text)
    return INLINE.sub("", text)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    files = sorted((ROOT / "lessons").glob("module_0[0-7]_*.Rmd")) + [ROOT / "README.md"] + \
        sorted((ROOT / "docs").glob("*.md"))
    glossary = (ROOT / "docs" / "glossary.md").read_text(encoding="utf-8")
    anchors = set(GLOSSARY_ANCHOR.findall(glossary))
    for path in files:
        raw = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        if EM_DASH in raw:
            errors.append(f"{rel}: contains an em dash")
        text = prose(raw)
        for match in US.finditer(text):
            if match.group(1).lower() in US_BAD:
                errors.append(f"{rel}: US spelling '{match.group(1)}'")
        for anchor in GLOSSARY_LINK.findall(raw):
            if anchor not in anchors:
                errors.append(f"{rel}: glossary link #{anchor} has no entry")
        if path.name.startswith("module_"):
            n = int(path.name.split("_")[1])
            first_step = re.search(rf"^## {n}\.1 ", raw, re.M)
            overview = re.search(rf"^## Module {n} at a glance \{{#module-{n}-overview\}}\s*$", raw, re.M)
            recap = re.search(rf"^## Module {n} recap \{{#module-{n}-recap\}}\s*$", raw, re.M)
            last_step = list(re.finditer(rf"^## {n}\.\d+ ", raw, re.M))
            if not overview or not first_step or overview.start() > first_step.start():
                errors.append(f"{rel}: missing 'Module {n} at a glance' section before step {n}.1")
            else:
                section = raw[overview.end():first_step.start()]
                for label in ("What you will do", "What you will learn", "How long it takes"):
                    if label not in section:
                        errors.append(f"{rel}: overview lacks '{label}'")
            if not recap or not last_step or recap.start() < last_step[-1].start():
                errors.append(f"{rel}: missing 'Module {n} recap' section after the last step")
            elif len(re.findall(r"^- ", raw[recap.end():], re.M)) < 3:
                errors.append(f"{rel}: recap needs at least three bullet points")
        for number, line in enumerate(text.splitlines(), 1):
            if line.lstrip().startswith(("|", "<", "#")):
                continue
            for sentence in re.split(r"(?<=[.!?])\s+", line):
                if len(sentence.split()) > 35:
                    warnings.append(f"{rel}: long sentence ({len(sentence.split())} words): {sentence[:70]}...")
    for w in warnings[:40]:
        print("warning:", w)
    if len(warnings) > 40:
        print(f"warning: {len(warnings) - 40} more long sentences not shown")
    for e in errors:
        print("error:", e)
    print(f"{len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
