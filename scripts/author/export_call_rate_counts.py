"""Store count-only step 3.2 metadata from a local state-3.1 PLINK sample report.

First run PLINK with --pfile <state-3.1> --missing sample-only --out <external-prefix>.
Then run this script with --smiss <external-prefix>.smiss. No row-level data are saved.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def aggregate(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 2013:
        raise ValueError("State 3.1 must contain 2,013 measured wells.")
    values = [(int(row["MISSING_CT"]), int(row["OBS_CT"])) for row in rows]
    if any(not 0 <= missing <= observed or observed <= 0 for missing, observed in values):
        raise ValueError("Invalid missing-call numerator or denominator.")
    # Integer cross-products preserve strict boundaries, without rounded F_MISS values.
    counts = [{"threshold_percent": half_percent / 2,
               "samples_below": sum((observed - missing) * 200 < half_percent * observed
                                    for missing, observed in values)}
              for half_percent in range(180, 200)]
    if counts[16]["samples_below"] != 42:
        raise ValueError("The 98% threshold must match the 42 exclusions at step 3.2.")
    return {"kind": "sample_call_rate_threshold_counts", "source_state": "3.1",
            "sample_count": len(values), "comparison": "strictly_below",
            "call_rate_definition": "100 * (OBS_CT - MISSING_CT) / OBS_CT",
            "source_report_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "rows": counts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smiss", type=Path, required=True)
    args = parser.parse_args()
    metadata = aggregate(args.smiss)
    notebook = ROOT / "lessons/module_03_sample_quality_control.Rmd"
    text = notebook.read_text(encoding="utf-8")
    marker = "<!-- interactive_data: " + json.dumps(metadata, indent=2) + " -->"
    if "<!-- interactive_data:" in text:
        text = re.sub(r"<!-- interactive_data:.*?-->", lambda _: marker, text, flags=re.S)
    else:
        target = "42 additional wells removed; 1,971 samples and 296,360 variants remain."
        if text.count(target) != 1:
            raise ValueError("Cannot locate the canonical step 3.2 result.")
        text = text.replace(target, target + "\n\n" + marker)
    notebook.write_text(text, encoding="utf-8")
    print("Stored 20 count-only thresholds in the canonical step 3.2 notebook.")


if __name__ == "__main__":
    main()
