"""Build an AES-256 course ZIP outside the repository. No upload is performed.

The password comes only from COURSE_RELEASE_PASSWORD. It is sent to 7-Zip's
interactive prompt, never included in its command arguments or saved to disk.
MANIFEST.tsv is a sidecar: it lists every payload member, without a self-hash.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
from pathlib import Path
import shutil
import struct
import subprocess
import time
import zipfile

REPO = Path(__file__).resolve().parents[1]
SOURCE = Path(r"C:\WEB_site\data_sources\sim2026\student")
# Author work folder outside the repository. Set COURSE_RELEASE_WORK to use another folder.
WORK = Path(os.environ.get("COURSE_RELEASE_WORK") or r"C:\WEB_site\data_sources\codex_work")
FORBIDDEN = ("instructor", "answer_key", "build_record", "truth")
DIRECTORIES = {"array", "checkpoints", "final_report", "grch37_exercise",
               "imputation", "lab_export", "pca_reference", "phenotypes"}
# Module A (imputation) is a separate package with its own top folders and its own staging prefix.
# It also carries the module helpers, R/imputation.R, and no other R file. FORBIDDEN applies to both packages.
MODULE_A_DIRECTORIES = {"reference_panel", "genetic_map", "imputed", "true_genotypes"}
PACKAGES = {
    "main": {"directories": DIRECTORIES, "top_files": {"README_simulated.txt"}, "files": set(),
             "archive": "course-data-2026.1", "stage_prefix": "classroom-stage-",
             "source": "classroom-stage-2026.1", "output": "release-data-2026.1"},
    "module-a": {"directories": MODULE_A_DIRECTORIES, "top_files": {"README_simulated.txt", "panel_samples.tsv"},
                 "files": {"R/imputation.R"}, "archive": "module-a-data-2026.1", "stage_prefix": "stage-module-a-",
                 "source": "stage-module-a-2026.1", "output": "release-module-a-2026.1",
                 # A named file must equal its committed copy on this branch (read with git, so line ends
                 # of the working tree do not matter).
                 "pinned": {"R/imputation.R": "course/module-a-2026.4"}},
}


def committed_file(branch: str, name: str, repo: Path = REPO) -> bytes:
    """The bytes of a file on a branch: the local branch, or origin/<branch> when there is no local one."""
    for ref in (f"refs/heads/{branch}", f"refs/remotes/origin/{branch}"):
        found = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", ref],
                               capture_output=True, text=True)
        if found.returncode == 0:
            return subprocess.check_output(["git", "-C", str(repo), "show", f"{found.stdout.strip()}:{name}"])
    raise ValueError(f"Branch {branch} was not found in {repo}. Fetch it first.")


def check_pinned_files(source: Path, package: str, read=committed_file) -> None:
    """Stop when a named file of the stage differs from its copy on the course branch."""
    for name, branch in PACKAGES[package].get("pinned", {}).items():
        staged = source / name
        if not staged.is_file() or staged.read_bytes() != read(branch, name):
            raise ValueError(f"{name} in {source} is missing or differs from {name} on branch {branch}. "
                             f"Copy it again from that branch (git show {branch}:{name}) and run the packager again.")


def safe_path(path: Path) -> None:
    if any(word in str(path).lower() for word in FORBIDDEN):
        raise ValueError("Refusing a path containing a restricted name.")
    if any(c in str(path) for c in "\t\r\n"):
        raise ValueError("Paths must not contain tabs or line breaks.")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def inventory(source: Path, package: str = "main") -> list[tuple[Path, str]]:
    rule = PACKAGES[package]
    safe_path(source)
    if source.is_symlink() or source.is_junction():
        raise ValueError("The source must not be a link or junction.")
    source = source.resolve(strict=True)
    files = []
    for path in sorted(source.rglob("*")):
        safe_path(path)
        if path.is_symlink() or path.is_junction():
            raise ValueError("Links and junctions are not permitted.")
        path.resolve(strict=True).relative_to(source)
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        top_file = len(relative.parts) == 1 and relative.name in rule["top_files"]
        named_file = relative.as_posix() in rule["files"]
        folder = len(relative.parts) > 1 and relative.parts[0] in rule["directories"]
        if not (top_file or named_file or folder):
            raise ValueError("Unrecognised student file: " + relative.as_posix())
        # Author-machine paths and hostnames are not student inputs.
        if path.suffix.lower() == ".log":
            continue
        files.append((path, relative.as_posix()))
    if not files:
        raise ValueError("No student files were found.")
    names = [name.casefold() for _, name in files]
    if len(names) != len(set(names)):
        raise ValueError("File names must also be unique on Windows.")
    return files


def aes256_members(path: Path) -> list[str]:
    """Check the WinZip AES extra field of every regular member."""
    names = []
    with zipfile.ZipFile(path) as archive:
        for member in archive.infolist():
            safe_path(Path(member.filename))
            if member.is_dir():
                continue
            extra, strength = member.extra, None
            while len(extra) >= 4:
                tag, size = struct.unpack("<HH", extra[:4])
                data, extra = extra[4:4 + size], extra[4 + size:]
                if tag == 0x9901 and len(data) == 7:
                    strength = data[4]
            if not member.flag_bits & 1 or member.compress_type != 99 or strength != 3:
                raise ValueError("A ZIP member is not AES-256 encrypted.")
            names.append(member.filename)
    return names


def dry_run(source: Path, output: Path, package: str = "main") -> dict:
    """List the files the package would hold and write their MANIFEST.tsv. No copy, no ZIP, no password.

    MANIFEST.tsv has the format of a real build; members.txt is the list given to 7-Zip."""
    for path in (source, output):
        safe_path(path)
    source, output = source.resolve(strict=True), output.resolve()
    output.relative_to(WORK.resolve())
    if output == WORK.resolve() or output.is_relative_to(REPO) or output.exists():
        raise ValueError("Choose a new output directory beneath codex_work.")
    members = inventory(source, package)
    check_pinned_files(source, package)
    output.mkdir(parents=True)
    rows = [(name, original.stat().st_size, sha256(original)) for original, name in members]
    text = io.StringIO(newline="")
    writer = csv.writer(text, delimiter="\t", lineterminator="\n")
    writer.writerow(("path", "bytes", "sha256"))
    writer.writerows(rows)
    (output / "MANIFEST.tsv").write_text(text.getvalue(), encoding="utf-8", newline="\n")
    (output / "members.txt").write_text("\n".join(name for _, name in members) + "\n", encoding="utf-8")
    return {"dry_run": True, "package": package, "source": str(source), "files": len(rows),
            "input_bytes": sum(r[1] for r in rows), "manifest_sha256": sha256(output / "MANIFEST.tsv"),
            "would_create": f"{PACKAGES[package]['archive']}.zip"}


def build(source: Path, output: Path, sevenzip: Path, package: str = "main") -> dict:
    rule = PACKAGES[package]
    started = time.perf_counter()
    for path in (source, output, sevenzip):
        safe_path(path)
    source, output = source.resolve(strict=True), output.resolve()
    output.relative_to(WORK.resolve())
    if output == WORK.resolve() or output.is_relative_to(REPO) or output.exists():
        raise ValueError("Choose a new output directory beneath codex_work.")
    password = os.environ.get("COURSE_RELEASE_PASSWORD", "")
    if not password or any(c in password for c in "\r\n"):
        raise ValueError("Set a non-empty COURSE_RELEASE_PASSWORD without line breaks.")
    members = inventory(source, package)
    check_pinned_files(source, package)
    output.mkdir(parents=True)
    staging = output / "payload"
    staging.mkdir()
    rows = []
    for original, name in members:
        copy = staging / name
        copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, copy)
        rows.append((name, copy.stat().st_size, sha256(copy)))
    text = io.StringIO(newline="")
    writer = csv.writer(text, delimiter="\t", lineterminator="\n")
    writer.writerow(("path", "bytes", "sha256"))
    writer.writerows(rows)
    (output / "MANIFEST.tsv").write_text(text.getvalue(), encoding="utf-8", newline="\n")
    archive = output / f"{rule['archive']}.zip"
    # An explicit list avoids directory entries. The environment is scrubbed.
    listing = output / "members.txt"
    listing.write_text("\n".join(name for _, name in members) + "\n", encoding="utf-8")
    environment = dict(os.environ)
    environment.pop("COURSE_RELEASE_PASSWORD", None)
    result = subprocess.run([str(sevenzip), "a", "-tzip", "-mem=AES256", "-mx=6",
                             "-p", "-scsUTF-8", str(archive), "@" + str(listing)],
                            cwd=staging, input=password + "\n" + password + "\n",
                            text=True, capture_output=True, env=environment)
    if result.returncode:
        raise RuntimeError("7-Zip could not build the encrypted package. Exit code: " + str(result.returncode))
    if sorted(aes256_members(archive)) != sorted(name for _, name in members):
        raise ValueError("Archive members differ from the approved inventory.")
    # Prove that the password opens the archive before any checksum is recorded.
    check = subprocess.run([str(sevenzip), "t", str(archive)], input=password + "\n",
                           text=True, capture_output=True, env=environment)
    if check.returncode:
        raise RuntimeError("The finished archive failed its own 7-Zip test. Exit code: " + str(check.returncode))
    checksum = sha256(archive)
    manifest_checksum = sha256(output / "MANIFEST.tsv")
    # Both lines are in GNU format, so `sha256sum -c SHA256SUMS.txt` works beside the files.
    (output / "SHA256SUMS.txt").write_text(
        f"{checksum}  {archive.name}\n{manifest_checksum}  MANIFEST.tsv\n", encoding="ascii")
    return {"archive": str(archive), "files": len(rows), "input_bytes": sum(r[1] for r in rows),
            "zip_bytes": archive.stat().st_size, "archive_sha256": checksum,
            "manifest_sha256": manifest_checksum, "sha256": checksum,
            "seconds": round(time.perf_counter() - started, 3)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", choices=sorted(PACKAGES), default="main",
                        help="main: the course data; module-a: the imputation module (stage-module-a-* folder)")
    parser.add_argument("--source", type=Path,
                        help="main: the verified staging folder (default classroom-stage-2026.1) or the older "
                             "sim2026/student folder; module-a: a stage-module-a-* folder (default stage-module-a-2026.1)")
    parser.add_argument("--output", type=Path,
                        help="a NEW folder under codex_work; an existing folder is refused "
                             "(default release-data-2026.1 or release-module-a-2026.1)")
    parser.add_argument("--min-password-length", type=int, default=12)
    parser.add_argument("--sevenzip", type=Path, default=Path(r"C:\Program Files\7-Zip\7z.exe"))
    parser.add_argument("--dry-run", action="store_true",
                        help="write only MANIFEST.tsv and members.txt in the new output folder: no ZIP, no password")
    args = parser.parse_args()
    rule = PACKAGES[args.package]
    args.source = args.source or WORK / rule["source"]
    args.output = args.output or WORK / rule["output"]
    source = args.source.resolve()
    staged = source.parent == WORK.resolve() and source.name.startswith(rule["stage_prefix"])
    if args.package == "module-a" and not staged:
        parser.error("Module A input must be a verified stage-module-a-* folder directly under codex_work.")
    if args.package == "main" and source != SOURCE.resolve() and not staged:
        parser.error("Production input must be sim2026/student or a verified classroom-stage-* folder "
                     "directly under codex_work. Tests call build() on isolated copies.")
    import json
    if args.dry_run:
        print(json.dumps(dry_run(args.source, args.output, args.package), indent=2))
        return
    password = os.environ.get("COURSE_RELEASE_PASSWORD", "")
    if len(password) < args.min_password_length:
        parser.error(f"COURSE_RELEASE_PASSWORD must have at least {args.min_password_length} characters.")
    print(json.dumps(build(args.source, args.output, args.sevenzip, args.package), indent=2))


if __name__ == "__main__":
    main()
