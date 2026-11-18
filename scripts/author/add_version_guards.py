"""Put the version guard at the top of every R chunk of the lessons that calls a function that older projects lack.

Author tool. Run from the project root; it is safe to run again (a chunk that has the guard is not changed):

    python scripts/author/add_version_guards.py --since C:/path/to/unzipped/GWAS_course-2026.3.3 [--check]

--since is an unzipped older release. A function counts as new when R/ of this project defines it and R/ of the older
release does not. The guard works in an old project too, because it uses only base R before it calls the function.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERSION = re.search(r'course_project_version <- "([^"]+)"', (ROOT / "R" / "course.R").read_text(encoding="utf-8")).group(1)
DEFINITION = re.compile(r"^([A-Za-z_.][A-Za-z0-9_.]*)\s*<-\s*function", re.M)
CALL = re.compile(r"(?<![A-Za-z0-9_.$@:])([A-Za-z_.][A-Za-z0-9_.]*)\s*\(")
CHUNK = re.compile(r"^```\{r ([^\n}]*)\}\n(.*?)^```\s*$", re.M | re.S)
GUARD_MARK = "# Course check."


def defined_in(folder: Path) -> set[str]:
    names: set[str] = set()
    for path in sorted((folder / "R").glob("*.R")):
        names |= set(DEFINITION.findall(path.read_text(encoding="utf-8")))
    return names


def guard_lines(version: str) -> str:
    return (f"{GUARD_MARK} This step needs project version {version} or later.\n"
            f'if (!exists("requires_course_version")) stop("This step needs project version {version} or later. '
            f'Your project is older. Download the new version at step 0.3.", call. = FALSE)\n'
            f'requires_course_version("{version}")\n')


def calls_of(code: str) -> set[str]:
    lines = [line for line in code.splitlines() if not line.lstrip().startswith("#")]
    return set(CALL.findall("\n".join(lines)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--since", type=Path, required=True)
    parser.add_argument("--check", action="store_true", help="Only report the chunks that need the guard.")
    args = parser.parse_args()
    new_functions = defined_in(ROOT) - defined_in(args.since)
    new_functions -= {"requires_course_version"}
    changed = 0
    for lesson in sorted((ROOT / "lessons").glob("module_0[3-7]_*.Rmd")):
        text = open(lesson, encoding="utf-8", newline="").read()
        assert "\r\n" not in text, lesson.name

        def add(match: re.Match) -> str:
            nonlocal changed
            code = match.group(2)
            if GUARD_MARK in code or not (calls_of(code) & new_functions):
                return match.group(0)
            changed += 1
            print(f"{lesson.name}: chunk {match.group(1).split(',')[0]} calls {sorted(calls_of(code) & new_functions)[:3]}")
            return f"```{{r {match.group(1)}}}\n{guard_lines(VERSION)}{code}```"

        new_text = CHUNK.sub(add, text)
        if new_text != text and not args.check:
            open(lesson, "w", encoding="utf-8", newline="").write(new_text)
    print(f"{changed} chunk(s) {'need' if args.check else 'got'} the guard for version {VERSION}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
