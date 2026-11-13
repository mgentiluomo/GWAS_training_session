"""Build and verify the allowlisted student project ZIP outside the repository.

No uploads, release creation, passwords or classroom data are involved.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = ("lessons", "R", "examples/formats")
FILES = (
    "config.R", "GWAS_course.Rproj", "scripts/preflight.R",
    "scripts/run_main_path.R", "scripts/check_course.R", "scripts/install_packages.R",
    "bin/README.md", "README.md", "LICENSE", "LICENSE-CONTENT.md",
    "docs/setup.md", "docs/troubleshooting.md", "docs/glossary.md",
    "docs/international_setup.md", "docs/data.md",
)
FENCE = re.compile(r"^```.*?^```[^\S\n]*$", re.M | re.S)
COMMENTS = re.compile(r"<!--.*?-->", re.S)
LINK = re.compile(r"!?\[[^\]\n]*\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def external_folder(path: Path, root: Path) -> Path:
    path = path.resolve()
    if path == root.resolve() or path.is_relative_to(root.resolve()):
        raise ValueError("Project artifacts must stay outside the repository.")
    return path


def inventory(root: Path = ROOT) -> dict[str, bytes]:
    """Enumerate tracked allowlisted paths, reading their reviewed working bytes."""
    tracked = subprocess.check_output(
        ["git", "ls-files", "-z", "--", *FOLDERS], cwd=root).decode("utf-8").split("\0")
    paths = sorted(set(filter(None, tracked)) | set(FILES))
    result = {}
    for name in paths:
        path = root / name
        # Moved legacy sources can still be staged as deletions during review.
        if not path.exists() and name not in FILES:
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"Refusing a linked or escaping project member: {name}")
        if not path.is_file():
            raise ValueError(f"Required student source is missing: {name}")
        if name.startswith("lessons/") and not re.fullmatch(r"lessons/module_0[0-7]_[^/]+\.Rmd", name):
            raise ValueError(f"Unexpected student lesson source: {name}")
        if name.startswith("R/") and not name.endswith(".R"):
            raise ValueError(f"Unexpected student R source: {name}")
        result[name] = path.read_bytes()
    examples = [v for k, v in result.items() if k.startswith("examples/formats/")]
    if sum(map(len, examples)) >= 100_000:
        raise ValueError("Invented format examples must total less than 100,000 bytes.")
    if "GWAS_training_session.Rproj" in result:
        raise ValueError("The old project file must not be packaged.")
    return result


def visible(data: bytes) -> str:
    return FENCE.sub("", COMMENTS.sub("", data.decode("utf-8")))


def anchors(text: str) -> set[str]:
    found = set(re.findall(r"\{#([^}]+)\}|\b(?:id|name)=[\"']([^\"']+)[\"']", text))
    result = {a or b for a, b in found}
    counts = {}
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, re.M):
        if "{#" in heading:
            continue
        heading = re.sub(r"[`*_]", "", heading).lower()
        slug = re.sub(r"[^\w\s-]", "", heading)
        slug = re.sub(r"\s+", "-", slug.strip())
        number = counts.get(slug, 0)
        counts[slug] = number + 1
        result.add(slug + (f"-{number}" if number else ""))
    return result


def check_links(files: dict[str, bytes]) -> dict:
    """Resolve every visible local Markdown/HTML link and its target anchor."""
    local = []
    urls = set()
    for name, data in files.items():
        if not name.endswith((".md", ".Rmd")):
            continue
        text = visible(data)
        targets = LINK.findall(text)
        targets += re.findall(r"\b(?:href|src)=[\"']([^\"']+)[\"']", text)
        targets += re.findall(r"<(https?://[^>\s]+)>", text)
        for target in targets:
            parts = urlsplit(target)
            if parts.scheme in {"http", "https"}:
                urls.add(target)
                continue
            if parts.scheme == "mailto":
                continue
            if parts.scheme or target.startswith("/"):
                raise ValueError(f"Unsupported student link in {name}: {target}")
            resolved = urljoin(name, unquote(parts.path)) if parts.path else name
            if resolved.startswith("../") or resolved not in files and not any(k.startswith(resolved.rstrip("/") + "/") for k in files):
                raise ValueError(f"Student link leaves the ZIP inventory: {name}: {target}")
            if parts.fragment:
                if resolved not in files or unquote(parts.fragment) not in anchors(visible(files[resolved])):
                    raise ValueError(f"Student link has a missing anchor: {name}: {target}")
            local.append({"source": name, "target": target})
    return {"local_links_checked": len(local), "local_links": local, "website_urls": sorted(urls)}


def verify_archive(path: Path, files: dict[str, bytes]) -> None:
    expected = {"GWAS_course/" + name for name in files}
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError("The project ZIP failed its CRC check.")
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("The project ZIP inventory differs from its allowlist.")
        for name in names:
            member = PurePosixPath(name)
            if member.is_absolute() or ".." in member.parts or "\\" in name:
                raise ValueError(f"Unsafe project ZIP member: {name}")
            if archive.read(name) != files[name.removeprefix("GWAS_course/")]:
                raise ValueError(f"The project ZIP changed source bytes: {name}")


def clean_environment() -> dict[str, str]:
    return {k: v for k, v in os.environ.items()
            if k.upper() not in {"LANG", "LANGUAGE", "LC_ALL"}
            and not k.upper().startswith("LC_")}


def fresh_check(archive: Path, output: Path, rscript: Path, data: Path, plink: Path) -> dict:
    """Test extracted sources twice; never require a project-folder basename."""
    folder = Path(tempfile.mkdtemp(prefix="fresh-project-", dir=output))
    with zipfile.ZipFile(archive) as zipped:
        zipped.extractall(folder)
    project = folder / "GWAS_course"
    # Step 0.6 installs PLINK in bin/ after extraction. The executable is a
    # test prerequisite, never a member of the source ZIP.
    executable = "plink2.exe" if os.name == "nt" else "plink2"
    shutil.copy2(plink, project / "bin" / executable)
    runs = []
    for dirname in ("GWAS_course", "GWAS_training_session"):
        if project.name != dirname:
            renamed = folder / dirname
            project.rename(renamed)
            project = renamed
        env = clean_environment()
        env.update(COURSE_DATA_DIR=str(data.resolve()), PLINK2_BIN=str(project / "bin" / executable),
                   COURSE_OUTPUT_DIR=str(folder / (dirname + "-results")))
        env.pop("GWAS_RUN_DEMO_CHECK", None)
        commands = [
            [str(rscript), "--vanilla", "-e", 'stopifnot(file.exists("GWAS_course.Rproj"), file.exists("config.R"), file.exists("R/course.R")); cat(getwd(), "\\n"); print(R.version.string); stopifnot(identical(2 + 3, 5)); print(2 + 3)'],
            [str(rscript), "--vanilla", "scripts/check_course.R"],
            [str(rscript), "--vanilla", "-e", 'source("R/package_setup.R"); stopifnot(all(vapply(c("archive", "digest", "getPass", "knitr", "rmarkdown"), requireNamespace, logical(1), quietly=TRUE))); source("scripts/install_packages.R"); source("scripts/preflight.R")'],
        ]
        for number, command in enumerate(commands, 1):
            log = folder / f"{dirname}-{number}.log"
            with log.open("w", encoding="utf-8") as stream:
                result = subprocess.run(command, cwd=project, env=env, stdout=stream, stderr=subprocess.STDOUT)
            if result.returncode:
                raise RuntimeError(log.read_text(encoding="utf-8", errors="replace"))
        runs.append({"folder_name": dirname, "root_r_version_calculation": "PASS", "syntax_safeguards": "PASS", "packages_and_preflight": "PASS"})
    return {"runs": runs, "logs_folder": str(folder), "rstudio_gui": "not exercised",
            "plink_provisioning": "copied into extracted bin/ after extraction, as at step 0.6",
            "plink_sha256": digest(plink.read_bytes())}


def url_status(url: str, planned: str) -> dict:
    if url == planned:
        return {"url": url, "status": "pending_author_publication"}
    try:
        request = Request(url, headers={"User-Agent": "GWAS-course-project-link-check/1.0"})
        with urlopen(request, timeout=20) as response:
            return {"url": url, "status": response.status, "resolved_url": response.url}
    except HTTPError as error:
        return {"url": url, "status": error.code, "resolved_url": error.url}
    except (URLError, TimeoutError, OSError) as error:
        return {"url": url, "status": "unverified", "reason": str(error)}


def build(output: Path, version: str = "2026.1", root: Path = ROOT) -> tuple[Path, dict]:
    if not re.fullmatch(r"2026\.1(?:\.[1-9][0-9]*)?", version):
        raise ValueError("Use an explicit project release version, never latest.")
    output = external_folder(output, root)
    if output.exists():
        raise ValueError("Choose a new external output folder.")
    files = inventory(root)
    links = check_links(files)
    planned = f"https://github.com/mgentiluomo/GWAS_training_session/releases/download/project-{version}/GWAS_course-{version}.zip"
    source = files["lessons/module_00_preparation.Rmd"].decode("utf-8")
    if planned not in source or re.search(r"releases/(?:latest|download/latest)", source):
        raise ValueError("Step 0.3 must use the matching versioned project asset URL.")
    output.mkdir(parents=True)
    archive = output / f"GWAS_course-{version}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipped:
        for name, data in files.items():
            info = zipfile.ZipInfo("GWAS_course/" + name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zipped.writestr(info, data, compresslevel=9)
    verify_archive(archive, files)
    checksum = digest(archive.read_bytes())
    (output / (archive.name + ".sha256")).write_text(checksum + "  " + archive.name + "\n", encoding="ascii")
    report = {"tag": "project-" + version, "asset": archive.name,
              "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root).decode().strip(),
              "source_state": "reviewed working files; per-file hashes below are authoritative",
              "file_count": len(files), "uncompressed_bytes": sum(map(len, files.values())),
              "zip_bytes": archive.stat().st_size, "sha256": checksum,
              "allowlist_folders": FOLDERS, "allowlist_files": FILES,
              "files": [{"path": k, "bytes": len(v), "sha256": digest(v)} for k, v in files.items()],
              "links": links, "planned_asset_url": planned}
    return archive, report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--version", default="2026.1")
    parser.add_argument("--fresh-check", action="store_true")
    parser.add_argument("--check-urls", action="store_true")
    parser.add_argument("--rscript", type=Path)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--plink", type=Path)
    args = parser.parse_args()
    if args.fresh_check and not all(p and p.is_file() if name != "data_dir" else p and p.is_dir()
                                    for name, p in [("rscript", args.rscript), ("data_dir", args.data_dir), ("plink", args.plink)]):
        parser.error("The fresh check needs an existing --rscript, --data-dir and --plink.")
    archive, report = build(args.output, args.version)
    if args.fresh_check:
        report["fresh_folder_test"] = fresh_check(archive, args.output, args.rscript, args.data_dir, args.plink)
    if args.check_urls:
        with ThreadPoolExecutor(max_workers=6) as pool:
            report["website_checks"] = list(pool.map(lambda url: url_status(url, report["planned_asset_url"]), report["links"]["website_urls"]))
        report["website_links_verified"] = all(
            isinstance(row["status"], int) and 200 <= row["status"] < 300
            for row in report["website_checks"] if row["status"] != "pending_author_publication")
    destination = args.output / "project-verification.json"
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["tag", "asset", "file_count", "zip_bytes", "uncompressed_bytes", "sha256"]}, indent=2))
    print("Verification report:", destination)
    if args.check_urls and not report["website_links_verified"]:
        print("Website verification is incomplete; read the per-URL statuses in the report.")


if __name__ == "__main__":
    main()
