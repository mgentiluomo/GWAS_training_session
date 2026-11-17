"""Checks the versioned threshold trials in site_content/threshold_sweeps.json.

The structural checks always run. The comparison with the main path runs when the folder of a main-path run is
given in COURSE_OUTPUT_DIR (it must hold step_counts.tsv). Run: python -B scripts/tests/test_threshold_sweeps.py
"""
import csv
import json
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SWEEPS = json.loads((ROOT / "site_content" / "threshold_sweeps.json").read_text(encoding="utf-8"))["sweeps"]
# (step, option) -> (which count, where the main path keeps it). "step_counts" rows come from step_counts.tsv.
COURSE_STATE = {
    ("3.1", "--mind"): ("samples", "3.1"),
    ("3.1", "--geno"): ("variants", "3.1"),
    ("3.2", "--mind"): ("samples", "3.2"),
    ("3.3", "max-female-xf"): ("samples", "3.3"),
    ("3.3", "min-male-xf"): ("samples", "3.3"),
    ("3.4", "r2 limit"): ("variants", "prune"),
    ("3.4", "window (kb)"): ("variants", "prune"),
    ("3.5", "F cutoff (standard deviations)"): ("samples", "3.5"),
    ("3.6", "KING kinship cutoff"): ("samples", "3.6"),
    ("4.1", "--geno"): ("variants", "4.1"),
    ("4.2", "test-missing p-value cutoff"): ("variants", "4.2"),
    ("4.3", "--maf"): ("variants", "4.3"),
    ("4.4", "HWE p-value cutoff"): ("variants", "4.4"),
    ("5.6", "SD limit"): ("samples", "5.6"),
}
ALTERNATIVE = {("5.6", "MCD chi-squared quantile")}
PCS = {("5.7", "Number of PCs")}


class ThresholdSweepTests(unittest.TestCase):
    def test_every_trial_counts_add_up(self):
        for sweep in SWEEPS:
            if sweep.get("kind") == "pcs":
                continue
            for trial in sweep["trials"]:
                with self.subTest(step=sweep["step"], option=sweep["option"], trial=trial["label"]):
                    self.assertEqual(trial["samples_remaining"], sweep["input_samples"] - trial["samples_removed"])
                    self.assertEqual(trial["variants_remaining"], sweep["input_variants"] - trial["variants_removed"])

    def test_one_course_value_per_sweep(self):
        keys = {(s["step"], s["option"]) for s in SWEEPS}
        self.assertEqual(keys, set(COURSE_STATE) | ALTERNATIVE | PCS)
        for sweep in SWEEPS:
            expected = 0 if sweep.get("alternative") else 1
            with self.subTest(step=sweep["step"], option=sweep["option"]):
                self.assertEqual(sum(1 for t in sweep["trials"] if t["course_value"]), expected)

    def test_course_value_equals_main_path(self):
        folder = os.environ.get("COURSE_OUTPUT_DIR")
        counts_file = Path(folder) / "step_counts.tsv" if folder else None
        if not counts_file or not counts_file.exists():
            self.skipTest("Set COURSE_OUTPUT_DIR to the folder of a main-path run to compare with step_counts.tsv.")
        with counts_file.open(encoding="utf-8", newline="") as handle:
            counts = {row["step"]: row for row in csv.DictReader(handle, delimiter="\t")}
        main = {}
        with (Path(folder) / "s7-7_comparison.tsv").open(encoding="utf-8", newline="") as handle:
            main = next(r for r in csv.DictReader(handle, delimiter="\t") if r["model"] == "main")
        for sweep in SWEEPS:
            key = (sweep["step"], sweep["option"])
            if key in ALTERNATIVE:
                continue
            course = next(t for t in sweep["trials"] if t["course_value"])
            with self.subTest(step=sweep["step"], option=sweep["option"]):
                if key in PCS:
                    self.assertEqual(course["hits"], int(main["hits"]))
                    self.assertAlmostEqual(course["lambda"], float(main["lambda"]), places=4)
                    continue
                kind, step = COURSE_STATE[key]
                if step == "prune":
                    kept = len((Path(folder) / "s3-4_prune.prune.in").read_text(encoding="utf-8").split())
                    self.assertEqual(course["variants_remaining"], kept)
                else:
                    self.assertEqual(course[kind + "_remaining"], int(counts[step][kind]))


if __name__ == "__main__":
    unittest.main()
