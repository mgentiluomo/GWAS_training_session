"""Export website step content and an executable script from canonical notebooks."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import posixpath
from pathlib import Path, PurePosixPath
import re
import shlex

ROOT = Path(__file__).resolve().parents[1]
STEP = re.compile(r"^## (\d+)\.(\d+) (.*?) \{#(step-\d+-\d+)\}\s*$", re.M)
HEADING = re.compile(r"^## .*$", re.M)
OVERVIEW = re.compile(r"^## Module (\d+) at a glance \{#module-\d+-overview\}\s*$", re.M)
RECAP = re.compile(r"^## Module (\d+) recap \{#module-\d+-recap\}\s*$", re.M)
CHUNK = re.compile(r"^```\{r\s+([^,}\s]+)([^}]*)\}\s*\n(.*?)^```\s*$", re.M | re.S)
SCREENSHOT = re.compile(r"<!-- screenshot:\s*(.*?)\s*-->", re.S)
STEP_META = re.compile(r"<!-- step_meta:\s*(.*?)\s*-->", re.S)
SCHEMA_VERSION = "1.1"
READING_NOTE = re.compile(r"^Reading, about (\d+) minutes\. You can come back to it later\.$", re.M)
BLOCKS = [
    ("what_we_do", "### What we do"), ("why", "### Why"),
    ("you_need", "### You need"), ("command", "### Command"),
    ("expected_result", "<details><summary>Show the expected result</summary>"),
    ("troubleshooting", "<details><summary>If something goes wrong</summary>"),
    ("what_this_check_can_reveal", "### What this check can reveal"),
    ("quick_check", "### Quick check"), ("files_created", "### Files created"),
    # Optional ninth block for readers who want the statistics and the literature behind a step.
    # It must come last, after "Files created", so the beginner path ends where it always did.
    ("under_the_hood", "<details><summary>Under the hood & literature</summary>"),
]
OPTIONAL_BLOCKS = {"what_this_check_can_reveal", "under_the_hood"}
COLLAPSED_BLOCKS = {"expected_result", "troubleshooting", "under_the_hood"}
FENCE = re.compile(r"^```.*?^```\s*$", re.M | re.S)
MD_LINK = re.compile(r"(\]\()([^)\s]+)((?:\s+\"[^\"]*\")?\))")
HTML_HREF = re.compile(r"(\bhref=\")([^\"]+)(\")")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def repo_relative(target: str, base: str = "lessons") -> str:
    """Rewrite a link written relative to the notebook folder as a path from the repository root.

    Absolute URLs, same-page anchors and root-absolute paths are returned unchanged.
    """
    if not target or SCHEME.match(target) or target.startswith(("#", "/", "?")):
        return target
    path, hash_mark, fragment = target.partition("#")
    resolved = posixpath.normpath(posixpath.join(base, path))
    if resolved == ".." or resolved.startswith("../") or resolved == ".":
        raise ValueError(f"A link leaves the repository: {target}")
    if path.endswith("/"):
        resolved += "/"
    return resolved + hash_mark + fragment


def normalise_links(text: str, base: str = "lessons") -> str:
    """Make every relative link in exported Markdown a path from the repository root.

    Notebooks sit in lessons/, so their links are written relative to that folder. Readers of the
    exported JSON resolve them from the repository root. Fenced code is never changed.
    """
    def fix(segment: str) -> str:
        segment = MD_LINK.sub(lambda m: m.group(1) + repo_relative(m.group(2), base) + m.group(3), segment)
        return HTML_HREF.sub(lambda m: m.group(1) + repo_relative(m.group(2), base) + m.group(3), segment)

    parts, last = [], 0
    for fence in FENCE.finditer(text):
        parts.append(fix(text[last:fence.start()]))
        parts.append(fence.group())
        last = fence.end()
    parts.append(fix(text[last:]))
    return "".join(parts)


def notebook_paths(root: Path = ROOT) -> list[Path]:
    files = sorted((root / "lessons").glob("module_[0-7][0-9]_*.Rmd"))
    # Module filenames are zero-padded 00 through 07.
    files = [p for p in files if int(p.name.split("_")[1]) in range(8)]
    if {int(p.name.split("_")[1]) for p in files} != set(range(8)) or len(files) != 8:
        raise ValueError("Exactly modules 0 to 7 must exist before a complete export.")
    return files


def split_blocks(body: str) -> dict[str, str]:
    positions = [(body.index(marker), name, marker) for name, marker in BLOCKS if marker in body]
    positions.sort()
    names = [name for _, name, _ in positions]
    required = [name for name, _ in BLOCKS if name not in OPTIONAL_BLOCKS]
    if [name for name in names if name in required] != required:
        raise ValueError("A step is missing a fixed block or uses the wrong block order.")
    if "under_the_hood" in names and names[-1] != "under_the_hood":
        raise ValueError("The 'Under the hood & literature' block must come after 'Files created'.")
    result = {}
    for i, (start, name, marker) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(body)
        content = body[start + len(marker):end].strip()
        if name in COLLAPSED_BLOCKS:
            content = re.sub(r"\s*</details>\s*$", "", content).strip()
        # Links are written relative to lessons/ in the notebooks; the export uses repository paths.
        result[name] = normalise_links(content)
    return result


def prose(text: str) -> str:
    return re.sub(r"^```.*?^```\s*$", "", text, flags=re.M | re.S)


def reading_word_count(text: str) -> int:
    """Count prose, tables, headings, answers and reference labels at 200 words/minute.

    Exclude the reading note itself, URLs, code fences and hidden figure metadata.
    Keep field names and numeric examples as words, including underscores.
    """
    visible = READING_NOTE.sub("", text)
    visible = re.sub(r"<!--.*?-->", "", visible, flags=re.S)
    visible = prose(visible)
    visible = re.sub(r"!?\[([^\]]*)\]\([^)]+\)", r"\1", visible)
    visible = re.sub(r"https?://\S+|\{#[^}]+\}|<[^>]+>", "", visible)
    return len(re.findall(r"\b\w+(?:[.'/-]\w+)*\b", visible))


def flag_explanation(flag: str, text: str) -> str | None:
    pattern = re.compile(r"(?<![\w-])" + re.escape(flag) + r"(?![\w-])")
    # Split prose only outside inline code, preserving decimals and option arguments.
    inline = []
    def protect(match):
        inline.append(match.group())
        return f"CODETOKEN{len(inline) - 1}END"
    protected = re.sub(r"`[^`]*`", protect, prose(text))
    clauses = re.split(r";\s*|(?<=[.!?])\s+(?=[A-Z])|\n\s*\n", protected)
    clauses = [re.sub(r"CODETOKEN(\d+)END", lambda m: inline[int(m.group(1))], clause)
               for clause in clauses]
    for clause in clauses:
        clause = clause.strip()
        if not pattern.search(clause) or clause.startswith("Plain PLINK"):
            continue
        if re.search(r"meanings given|meaning given|same .*settings|settings are used", clause):
            continue
        # An inline command is a usage example, not an explanation.
        if re.search(r"`bin[/\\]", clause) or clause.startswith("Terminal equivalent"):
            continue
        return clause
    return None


def screenshot_figures(body: str, root: Path = ROOT) -> list[dict]:
    """Read screenshot declarations without creating images or broken asset links."""
    figures = []
    seen = set()
    for match in SCREENSHOT.finditer(body):
        spec = json.loads(match.group(1))
        required = {"kind", "asset_path", "platform", "placement", "alt_text"}
        if not isinstance(spec, dict) or set(spec) != required or not all(
                isinstance(value, str) and value.strip() for value in spec.values()):
            raise ValueError("A screenshot needs kind, asset_path, platform, placement and alt_text.")
        path = PurePosixPath(spec["asset_path"])
        if (spec["kind"] != "screenshot" or spec["platform"] not in {"windows", "macos"} or
                spec["placement"] not in {name for name, _ in BLOCKS} or
                path.is_absolute() or ".." in path.parts or "\\" in spec["asset_path"] or
                path.parts[:2] != ("Figures", "screenshots") or path.suffix != ".png"):
            raise ValueError("A screenshot needs a local PNG path under Figures/screenshots and a valid platform and block.")
        candidate = (root / path).resolve()
        if not candidate.is_relative_to(root.resolve()) or spec["asset_path"] in seen:
            raise ValueError("Screenshot paths must stay inside the repository and be unique within a step.")
        seen.add(spec["asset_path"])
        figures.append({**spec, "asset": spec["asset_path"] if candidate.is_file() else None, "reviewed": False})
    return figures


def step_metadata(metadata: dict, record: dict) -> dict:
    """Validate optional UI metadata authored beside its canonical step."""
    if not isinstance(metadata, dict) or set(metadata) - {"actions", "where", "success_line"}:
        raise ValueError(f"Unknown step metadata in {record['id']}.")
    result = {}
    if "actions" in metadata:
        actions = metadata["actions"]
        if not isinstance(actions, list):
            raise ValueError("Step actions must be a list.")
        for action in actions:
            if (not isinstance(action, dict) or set(action) - {"label", "url", "kind", "os"}
                    or not {"label", "url", "kind"} <= set(action)
                    or not isinstance(action["label"], str) or not action["label"].strip()
                    or not isinstance(action["url"], str) or not action["url"].startswith("https://")
                    or action["kind"] not in {"download", "page"}
                    or ("os" in action and action["os"] not in {"windows", "macos", "linux"})):
                raise ValueError("An action needs a label, HTTPS URL, download/page kind and optional valid OS.")
        result["actions"] = actions
    where = metadata.get("where", {})
    if (not isinstance(where, dict)
            or set(where) - {c["label"] for c in record["r_commands"]}
            or any(value not in {"console", "terminal", "editor", "browser"} for value in where.values())):
        raise ValueError("Command locations must name an R chunk and a valid execution location.")
    for command in record["r_commands"]:
        if command["label"] in where:
            command["where"] = where[command["label"]]
    if "success_line" in metadata:
        line = metadata["success_line"]
        if (not isinstance(line, str) or not line.strip() or "\n" in line or len(line) > 180
                or line not in record["blocks"]["expected_result"]):
            raise ValueError(f"The success line must be a short exact excerpt of the expected result in {record['id']}.")
        result["success_line"] = line
    return result


def export_steps(root: Path = ROOT) -> list[dict]:
    records = []
    for path in notebook_paths(root):
        text = path.read_text(encoding="utf-8")
        matches = list(STEP.finditer(text))
        explained = {}
        # The explicit knit_setup chunk configures notebook rendering only.
        setup = [m.group(3).strip() for m in CHUNK.finditer(text[:matches[0].start()])
                 if m.group(1) != "knit_setup"]
        for i, match in enumerate(matches):
            # A step ends at the next level-2 heading, which may be a module recap.
            following = [h.start() for h in HEADING.finditer(text) if h.start() > match.start()]
            body = text[match.end():following[0] if following else len(text)]
            blocks = split_blocks(body)
            reading = READING_NOTE.search(body)
            if reading:
                words = reading_word_count(body)
                if int(reading.group(1)) != max(1, (words + 199) // 200):
                    raise ValueError(f"Update the reading time for step {match.group(1)}.{match.group(2)}: {words} words.")
                # Keep the opening note visible in the site's existing first block.
                blocks["what_we_do"] = reading.group() + "\n\n" + blocks["what_we_do"]
            commands = []
            for fence in re.findall(r"^```sh\s*\n(.*?)^```\s*$", blocks["command"], re.M | re.S):
                commands.extend(line.strip() for line in fence.splitlines() if line.strip().startswith("bin/"))
            commands.extend(code for code in re.findall(r"`([^`]+)`", prose(blocks["command"]))
                            if code.startswith("bin/") and "--" in code)
            commands = list(dict.fromkeys(commands))
            options = []
            flags = sorted({token for command in commands for token in shlex.split(command) if token.startswith("--")})
            for flag in flags:
                explanation = flag_explanation(flag, blocks["command"])
                previous = explained.get(flag)
                if not explanation and previous:
                    explanation = previous["explanation_markdown"]
                if not explanation:
                    raise ValueError(f"No notebook explanation for {flag} in step {match.group(1)}.{match.group(2)}")
                option = {"name": flag, "explanation_markdown": explanation}
                if not flag_explanation(flag, blocks["command"]):
                    option["explained_at"] = previous.get("explained_at", previous["step_id"])
                options.append(option)
                explained[flag] = {**option, "step_id": f"{match.group(1)}.{match.group(2)}"}
            r_commands = [{"label": m.group(1), "code": m.group(3).strip(),
                           "run_by_default": not bool(re.search(r"eval\s*=\s*FALSE", m.group(2)))}
                          for m in CHUNK.finditer(blocks["command"])]
            expected_render_code = [m.group(3).strip() for m in CHUNK.finditer(blocks["expected_result"])]
            # Notebook rendering helpers are author metadata, not student-facing website text.
            blocks["expected_result"] = CHUNK.sub("", blocks["expected_result"]).strip()
            figure_prompt = re.search(r"Figure placeholder\. Gemini prompt: (.*?)(?:\s*-->|\n\n|$)", body, re.S)
            figures = []
            command_text = re.sub(r"<!--.*?-->", "", blocks["command"], flags=re.S)
            if figure_prompt or ".png" in command_text:
                prompt = figure_prompt.group(1).strip() if figure_prompt else (
                    f"Create a labelled teaching schematic for {match.group(3)}. "
                    "Use shapes and text as well as colour. Do not invent numeric course results, "
                    "gene annotations or individual identities. This complements the tested R plot; it does not replace it.")
                alt = re.search(r'fig[.]alt="([^"]+)"', body)
                figures.append({"kind": "placeholder", "asset": None, "gemini_prompt": prompt,
                                "alt_text": alt.group(1) if alt else f"Teaching schematic: {match.group(3)}.", "reviewed": False})
            figures.extend(screenshot_figures(body, root))
            verified = "passed on Windows" in body or "executable preparation chunks passed on Windows" in text
            blocks = {name: re.sub(r"<!--.*?-->", "", content, flags=re.S).strip()
                      for name, content in blocks.items()}
            manual = not any(command["run_by_default"] for command in r_commands)
            verification = "manual_required" if manual else (
                "windows_executed" if verified and "UNVERIFIED" not in body and
                "pending executable Windows verification" not in body else "unverified")
            record = {"schema_version": SCHEMA_VERSION, "id": f"{match.group(1)}.{match.group(2)}",
                      "module": int(match.group(1)), "step": int(match.group(2)), "anchor": match.group(4),
                      "title": match.group(3), "source": path.relative_to(root).as_posix(),
                      "source_sha256": hashlib.sha256(text.encode()).hexdigest(),
                      "verification": verification,
                      "blocks": blocks, "setup_code": "\n\n".join(setup) if r_commands else "", "r_commands": r_commands,
                      "notebook_only_expected_code": expected_render_code,
                      "plink": {"applicable": bool(commands), "commands": commands, "options": options},
                      "figures": figures}
            metadata = STEP_META.findall(body)
            if len(metadata) > 1:
                raise ValueError(f"Duplicate step metadata in {record['id']}.")
            if metadata:
                record.update(step_metadata(json.loads(metadata[0]), record))
            interactive = re.search(r"<!-- interactive_data:\s*(.*?)\s*-->", body, re.S)
            if interactive:
                record["interactive_data"] = json.loads(interactive.group(1))
            records.append(record)
    if len(records) != 64 or len({r["id"] for r in records}) != 64:
        raise ValueError("The main path must have 64 unique steps.")
    return records


def section_text(text: str, start: re.Match) -> str:
    following = [h.start() for h in HEADING.finditer(text) if h.start() > start.start()]
    first_step = STEP.search(text, start.end())
    ends = following[:1] + ([first_step.start()] if first_step else [])
    return text[start.end():min(ends) if ends else len(text)].strip()


def export_modules(root: Path = ROOT) -> list[dict]:
    """Module overview and recap sections, for the website's module pages."""
    records = []
    for path in notebook_paths(root):
        text = path.read_text(encoding="utf-8")
        overview, recap = OVERVIEW.search(text), RECAP.search(text)
        if not overview or not recap:
            raise ValueError(f"{path.name} needs a 'Module N at a glance' and a 'Module N recap' section.")
        records.append({"schema_version": SCHEMA_VERSION, "module": int(overview.group(1)),
                        "title": re.search(r'^title: "Module \d+: (.*)"', text, re.M).group(1),
                        "source": path.relative_to(root).as_posix(),
                        "source_sha256": hashlib.sha256(text.encode()).hexdigest(),
                        "overview_markdown": normalise_links(re.sub(r"<!--.*?-->", "", section_text(text, overview), flags=re.S).strip()),
                        "recap_markdown": normalise_links(re.sub(r"<!--.*?-->", "", section_text(text, recap), flags=re.S).strip())})
    return records


def main_script(root: Path = ROOT) -> str:
    lines = ["# Generated from the tested modules 0 to 7; do not edit this copy.",
             "# Regenerate: python -B scripts/build_tutorial.py --export-main-script scripts/run_main_path.R",
             "# Run from the project root after installing tools and verifying course data.",
             "# COURSE_DATA_DIR and COURSE_OUTPUT_DIR may select external input/output folders.",
             "# Optional COURSE_CHAIN_FILE supplies the official local hg19-to-hg38 chain.",
             "# Interactive installation/download chunks are omitted; no password is stored here.", ""]
    for path in notebook_paths(root):
        text = path.read_text(encoding="utf-8")
        lines.extend([f"# Source: {path.relative_to(root).as_posix()}",
                      f"# SHA-256: {hashlib.sha256(text.encode()).hexdigest()}"])
        for match in CHUNK.finditer(text):
            if match.group(1) == "knit_setup" or re.search(r"eval\s*=\s*FALSE", match.group(2)):
                continue
            lines.extend([f"\n# Chunk: {match.group(1)}", match.group(3).strip(), ""])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export-steps", type=Path)
    parser.add_argument("--export-main-script", type=Path)
    args = parser.parse_args()
    if args.export_steps:
        records = export_steps()
        args.export_steps.mkdir(parents=True, exist_ok=True)
        for record in records:
            destination = args.export_steps / (record["anchor"] + ".json")
            destination.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        modules = export_modules()
        module_dir = args.export_steps.parent / "modules"
        module_dir.mkdir(parents=True, exist_ok=True)
        for record in modules:
            (module_dir / f"module-{record['module']}.json").write_text(
                json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        spec = importlib.util.spec_from_file_location("format_examples", ROOT / "scripts/author/make_format_examples.py")
        formats = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(formats)
        entries = formats.export_formats(args.export_steps.parent / "formats")
        print(f"Exported {len(records)} steps, {len(modules)} module pages and {len(entries)} format descriptions with tiny invented examples; no classroom data or website deployment created.")
    if args.export_main_script:
        args.export_main_script.write_text(main_script(), encoding="utf-8")
        print(f"Exported {args.export_main_script} from canonical notebook chunks.")


if __name__ == "__main__":
    main()
