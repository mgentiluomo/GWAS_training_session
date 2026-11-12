"""Export website step content and an executable script from canonical notebooks."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex

ROOT = Path(__file__).resolve().parents[1]
STEP = re.compile(r"^## (\d+)\.(\d+) (.*?) \{#(step-\d+-\d+)\}\s*$", re.M)
CHUNK = re.compile(r"^```\{r\s+([^,}\s]+)([^}]*)\}\s*\n(.*?)^```\s*$", re.M | re.S)
BLOCKS = [
    ("what_we_do", "### What we do"), ("why", "### Why"),
    ("you_need", "### You need"), ("command", "### Command"),
    ("expected_result", "<details><summary>Show the expected result</summary>"),
    ("troubleshooting", "<details><summary>If something goes wrong</summary>"),
    ("what_this_check_can_reveal", "### What this check can reveal"),
    ("quick_check", "### Quick check"), ("files_created", "### Files created"),
]


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
    required = [name for name, _ in BLOCKS if name != "what_this_check_can_reveal"]
    if [name for name in names if name in required] != required:
        raise ValueError("A step is missing a fixed block or uses the wrong block order.")
    result = {}
    for i, (start, name, marker) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(body)
        content = body[start + len(marker):end].strip()
        if name in {"expected_result", "troubleshooting"}:
            content = re.sub(r"\s*</details>\s*$", "", content).strip()
        result[name] = content
    return result


def prose(text: str) -> str:
    return re.sub(r"^```.*?^```\s*$", "", text, flags=re.M | re.S)


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


def export_steps(root: Path = ROOT) -> list[dict]:
    records = []
    for path in notebook_paths(root):
        text = path.read_text(encoding="utf-8")
        matches = list(STEP.finditer(text))
        explained = {}
        setup = [m.group(3).strip() for m in CHUNK.finditer(text[:matches[0].start()])]
        for i, match in enumerate(matches):
            body = text[match.end():matches[i + 1].start() if i + 1 < len(matches) else len(text)]
            blocks = split_blocks(body)
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
            if figure_prompt or ".png" in blocks["command"]:
                prompt = figure_prompt.group(1).strip() if figure_prompt else (
                    f"Create a labelled teaching schematic for {match.group(3)}. "
                    "Use shapes and text as well as colour. Do not invent numeric course results, "
                    "gene annotations or individual identities. This complements the tested R plot; it does not replace it.")
                alt = re.search(r'fig[.]alt="([^"]+)"', body)
                figures.append({"kind": "placeholder", "asset": None, "gemini_prompt": prompt,
                                "alt_text": alt.group(1) if alt else f"Teaching schematic: {match.group(3)}.", "reviewed": False})
            verified = "passed on Windows" in body or "executable preparation chunks passed on Windows" in text
            blocks = {name: re.sub(r"<!--.*?-->", "", content, flags=re.S).strip()
                      for name, content in blocks.items()}
            manual = bool(r_commands) and not any(command["run_by_default"] for command in r_commands)
            verification = "manual_required" if manual else (
                "windows_executed" if verified and "UNVERIFIED" not in body and
                "pending executable Windows verification" not in body else "unverified")
            record = {"schema_version": "1.0", "id": f"{match.group(1)}.{match.group(2)}",
                      "module": int(match.group(1)), "step": int(match.group(2)), "anchor": match.group(4),
                      "title": match.group(3), "source": path.relative_to(root).as_posix(),
                      "source_sha256": hashlib.sha256(text.encode()).hexdigest(),
                      "verification": verification,
                      "blocks": blocks, "setup_code": "\n\n".join(setup), "r_commands": r_commands,
                      "notebook_only_expected_code": expected_render_code,
                      "plink": {"applicable": bool(commands), "commands": commands, "options": options},
                      "figures": figures}
            interactive = re.search(r"<!-- interactive_data:\s*(.*?)\s*-->", body, re.S)
            if interactive:
                record["interactive_data"] = json.loads(interactive.group(1))
            records.append(record)
    if len(records) != 59 or len({r["id"] for r in records}) != 59:
        raise ValueError("The main path must have 59 unique steps.")
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
            if re.search(r"eval\s*=\s*FALSE", match.group(2)):
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
        print(f"Exported {len(records)} steps; no data files or website deployment created.")
    if args.export_main_script:
        args.export_main_script.write_text(main_script(), encoding="utf-8")
        print(f"Exported {args.export_main_script} from canonical notebook chunks.")


if __name__ == "__main__":
    main()
