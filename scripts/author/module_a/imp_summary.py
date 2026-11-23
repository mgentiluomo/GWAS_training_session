"""Compare imputed dosages with the true genotypes, by frequency class, for SNVs and indels.

Author side only. Used for module A (genotype imputation).

Inputs: a dosage VCF written by Minimac4 (FORMAT with DS; INFO with R2 and the IMPUTED, TYPED or TYPED_ONLY
flags) and a truth VCF with phased GT. Samples are matched by ID; variants by ID (chrom:pos:ref:alt). Every
variant of the truth that is polymorphic in the matched samples is counted, so the table also shows how many
true variants could not be imputed at all (absent from the reference panel). With --panel the share present
in the panel is reported too.

For each imputed variant: R2 (the Minimac estimate) and the true r2 (squared correlation between the dosage
and the true allele count). Classes by the minor allele count (MAC) and frequency in the matched samples:
MAC 1, MAC 2-4, below 0.5%, 0.5-1%, 1-5%, at least 5%.

Example:
    python -I imp_summary.py --dose chr22.dose.vcf.gz --truth imputation_truth_chr22.vcf.gz
        --panel panel_chr22.vcf.gz --tsv per_variant_chr22.tsv
"""

from __future__ import annotations

import argparse
import gzip
import math
import statistics
import sys
from pathlib import Path

CLASSES = ["MAC 1", "MAC 2-4", "<0.5%", "0.5-1%", "1-5%", ">=5%"]


def maf_class(mac: int, n_alleles: int) -> str:
    maf = mac / n_alleles
    return ("MAC 1" if mac == 1 else "MAC 2-4" if mac < 5 else "<0.5%" if maf < 0.005 else "0.5-1%" if maf < 0.01
            else "1-5%" if maf < 0.05 else ">=5%")


def r2(x: list[float], y: list[float]) -> float | None:
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx <= 0 or syy <= 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) ** 2 / (sxx * syy)


def vcf_rows(path: Path):
    """Yield the sample list once (as ('#', samples)), then the data lines split on tabs."""
    with gzip.open(path, "rt", encoding="ascii") as f:
        for line in f:
            if line.startswith("##"):
                continue
            p = line.rstrip("\r\n").split("\t")
            if line.startswith("#CHROM"):
                yield "#", p[9:]
            else:
                yield "v", p


def panel_ids(path: Path) -> set[str]:
    out = set()
    with gzip.open(path, "rt", encoding="ascii") as f:
        for line in f:
            if not line.startswith("#"):
                p = line.split("\t", 5)
                out.add(f"{p[0]}:{p[1]}:{p[3]}:{p[4]}")
    return out


def summarise(dose: Path, truth: Path, panel: set[str] | None) -> list[dict]:
    dose_samples: list[str] = []
    dose_rows: dict[str, tuple[dict, list[float]]] = {}
    for kind, p in vcf_rows(dose):
        if kind == "#":
            dose_samples = p
            continue
        info = dict(kv.split("=", 1) if "=" in kv else (kv, "1") for kv in p[7].split(";"))
        if "IMPUTED" not in info:
            continue
        k = p[8].split(":").index("DS")
        vid = f"{p[0]}:{p[1]}:{p[3]}:{p[4]}"
        dose_rows[vid] = (info, [float(s.split(":")[k]) for s in p[9:]])
    rows = []
    cols = None
    for kind, p in vcf_rows(truth):
        if kind == "#":
            where = {s: k for k, s in enumerate(p)}
            missing = [s for s in dose_samples if s not in where]
            if missing:
                raise ValueError(f"{len(missing)} dose samples are not in the truth, for example {missing[:3]}")
            cols = [where[s] for s in dose_samples]
            continue
        g = [int(p[9 + c][0]) + int(p[9 + c][2]) for c in cols]
        ac, n2 = sum(g), 2 * len(g)
        mac = min(ac, n2 - ac)
        if mac == 0:
            continue
        vid = f"{p[0]}:{p[1]}:{p[3]}:{p[4]}"
        row = {"id": vid, "snv": len(p[3]) == 1 and len(p[4]) == 1, "array": p[7] == "ARRAY", "mac": mac,
               "class": maf_class(mac, n2), "in_panel": (vid in panel) if panel is not None else None,
               "imputed": vid in dose_rows, "R2": None, "true": None}
        if row["imputed"]:
            info, ds = dose_rows[vid]
            row["R2"] = float(info.get("R2", "nan"))
            row["true"] = r2(ds, [float(x) for x in g])
        rows.append(row)
    return rows


def table(rows: list[dict], label: str) -> list[str]:
    out = [f"{label}: {len(rows)} true variants polymorphic in the samples, not on the array",
           "| Class | True variants | In panel | Imputed | Median R2 | Median true r2 | R2 < 0.3 | R2 >= 0.8 "
           "| r(R2, true r2) | Mean R2 - true r2 |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for name in CLASSES + ["all"]:
        sel = [r for r in rows if name == "all" or r["class"] == name]
        if not sel:
            continue
        imp = [r for r in sel if r["imputed"] and not math.isnan(r["R2"])]
        val = [r for r in imp if r["true"] is not None]
        panel = (f"{sum(bool(r['in_panel']) for r in sel) / len(sel):.0%}" if sel[0]["in_panel"] is not None else "n/a")
        if len(val) > 2 and len({r["R2"] for r in val}) > 1 and len({r["true"] for r in val}) > 1:
            corr = f"{statistics.correlation([r['R2'] for r in val], [r['true'] for r in val]):.2f}"
        else:
            corr = "n/a"
        med = lambda v: f"{statistics.median(v):.2f}" if v else "n/a"
        share = lambda c: f"{sum(c(r['R2']) for r in imp) / len(imp):.0%}" if imp else "n/a"
        bias = f"{statistics.fmean(r['R2'] - r['true'] for r in val):+.2f}" if val else "n/a"
        out.append(f"| {name} | {len(sel):,} | {panel} | {len(imp):,} | {med([r['R2'] for r in imp])} | "
                   f"{med([r['true'] for r in val])} | {share(lambda x: x < 0.3)} | {share(lambda x: x >= 0.8)} | "
                   f"{corr} | {bias} |")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dose", required=True, type=Path, help="Minimac4 dosage VCF (.vcf.gz)")
    ap.add_argument("--truth", required=True, type=Path, help="truth VCF with phased GT (.vcf.gz)")
    ap.add_argument("--panel", type=Path, help="reference panel VCF (.vcf.gz), for the share present in the panel")
    ap.add_argument("--tsv", type=Path, help="optional per-variant output")
    a = ap.parse_args(argv)
    rows = [r for r in summarise(a.dose, a.truth, panel_ids(a.panel) if a.panel else None) if not r["array"]]
    for label, sel in (("All variants", rows), ("SNVs", [r for r in rows if r["snv"]]),
                       ("Indels", [r for r in rows if not r["snv"]])):
        print("\n".join(table(sel, label)) + "\n")
    if a.tsv:
        with open(a.tsv, "w", encoding="utf-8", newline="\n") as f:
            f.write("id\tsnv\tmac\tclass\tin_panel\timputed\tR2\ttrue_r2\n")
            for r in rows:
                f.write(f"{r['id']}\t{int(r['snv'])}\t{r['mac']}\t{r['class']}\t{r['in_panel']}\t{int(r['imputed'])}\t"
                        f"{'' if r['R2'] is None else r['R2']}\t{'' if r['true'] is None else round(r['true'], 6)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
