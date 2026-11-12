"""Stage verified main-path inputs and boundary checkpoints outside the repository.

This creates a new directory only. It never changes source data, builds an
encrypted archive, publishes a release or handles a password.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
from pathlib import Path
import shutil

WORK = Path(r"C:\WEB_site\data_sources\codex_work")
STUDENT = Path(r"C:\WEB_site\data_sources\sim2026\student")
ALLOWED = ("array", "final_report", "grch37_exercise", "lab_export", "pca_reference", "phenotypes")
FORBIDDEN = ("instructor", "answer_key", "build_record", "truth")


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def copy_tree(source: Path, destination: Path) -> None:
    if source.is_symlink() or source.is_junction():
        raise ValueError("Source links and junctions are not permitted.")
    for path in sorted(source.rglob("*")):
        if path.is_symlink() or path.is_junction():
            raise ValueError("Source links and junctions are not permitted.")
        relative = path.relative_to(source)
        if any(word in relative.as_posix().lower() for word in FORBIDDEN):
            raise ValueError("Restricted material cannot be staged.")
        if not path.is_file() or path.suffix == ".log" or path.name.endswith((".command.txt", ".console.txt")):
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        if sha256(path) != sha256(target):
            raise ValueError("A staged copy failed verification.")


def stage(student: Path, run: Path, chain: Path, destination: Path) -> dict:
    student, run, chain = student.resolve(strict=True), run.resolve(strict=True), chain.resolve(strict=True)
    destination = destination.resolve()
    destination.relative_to(WORK.resolve())
    if destination == WORK.resolve() or destination.exists():
        raise ValueError("Choose a new staging folder beneath codex_work.")
    with (run / "checkpoints" / "index.tsv").open(encoding="utf-8") as stream:
        index = list(csv.DictReader(stream, delimiter="\t"))
    full = {row["step"] for row in index if row["kind"] == "full"}
    if full != {"2.8", "3.8", "4.6", "5.7"}:
        raise ValueError("Expected exactly the four full genotype boundaries.")
    if not {"6.7", "6.8", "7.8"}.issubset({row["step"] for row in index}):
        raise ValueError("Final analysis checkpoints are missing.")
    destination.mkdir(parents=True)
    for name in ALLOWED:
        copy_tree(student / name, destination / name)
    copy_tree(run / "checkpoints", destination / "checkpoints")
    shutil.copyfile(chain, destination / "grch37_exercise" / "hg19ToHg38.over.chain.gz")
    (destination / "README_simulated.txt").write_text(
        "Simulated guided GWAS course: modules 0 to 7. Genome assembly GRCh38.\n"
        "Full genotype boundaries: 2.8, 3.8, 4.6, 5.7. Intermediate steps replay stored lists.\n"
        "The initial BED/BIM/FAM export is the source for checkpoint 2.2, without an extra full copy.\n"
        "Analysis tables and figures have separate SHA-256 manifests.\n"
        "No instructor keys, local manufacturer manifest or imputation material is included.\n"
        "This is a local staging folder, not an approved published release.\n", encoding="utf-8")
    files = sorted(path for path in destination.rglob("*") if path.is_file())
    manifest = destination.with_name(destination.name + ".MANIFEST.tsv")
    with manifest.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(("path", "bytes", "sha256"))
        for path in files:
            writer.writerow((path.relative_to(destination).as_posix(), path.stat().st_size, sha256(path)))
    return {"files": len(files), "bytes": sum(path.stat().st_size for path in files),
            "full_boundaries": sorted(full), "manifest": str(manifest)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--student", type=Path, default=STUDENT)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--chain", type=Path, default=os.environ.get("COURSE_CHAIN_FILE"))
    parser.add_argument("--destination", type=Path, default=WORK / "classroom-stage-2026.1")
    args = parser.parse_args()
    if args.chain is None:
        parser.error("Supply --chain or COURSE_CHAIN_FILE for the official hg19-to-hg38 chain.")
    import json
    print(json.dumps(stage(args.student, args.run, Path(args.chain), args.destination), indent=2))


if __name__ == "__main__":
    main()
