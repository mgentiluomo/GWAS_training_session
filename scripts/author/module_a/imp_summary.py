"""Compare imputed dosages with the true genotypes, variant by variant.

Author side only. Used for module A (genotype imputation).

Inputs: a dosage VCF (FORMAT with DS; INFO with R2 or DR2, MAF or AF, and IMPUTED/TYPED flags as written by
Minimac4) and a truth VCF with phased GT for the same samples in the same column order. Variants are matched
by ID (the truth may hold more variants). For every imputed variant the script computes the true r2 between
dosage and true allele count, and summarises R2 against true r2 overall and by MAF class.

Example:
    python -I imp_summary.py --dose chr22.dose.vcf.gz --truth imputation_truth_chr22.vcf.gz [--info chr22.info.gz]
"""

from __future__ import annotations

import argparse
import gzip
import statistics
import sys
from pathlib import Path

CLASSES = [("MAC 1", None), ("MAC 2-4", None), ("<0.5%", 0.005), ("0.5-1%", 0.01), ("1-5%", 0.05), (">=5%", 1.0)]


def r2(x: list[float], y: list[float]) -> float | None:
    mx, my = statistics.fmean(x), statistics.fmean(y)
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx == 0 or syy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) ** 2 / (sxx * syy)


def maf_class(mac: int, maf: float) -> str:
    if mac <= 1:
        return "MAC 1"
    if mac < 5:
        return "MAC 2-4"
    for name, top in CLASSES[2:]:
        if maf < top:
            return name
    return ">=5%"


def info_dict(field: str) -> dict:
    return dict(kv.split("=", 1) if "=" in kv else (kv, True) for kv in field.split(";"))


def read_truth(path: Path) -> tuple[list[str], dict[str, list[int]]]:
    samples, out = [], {}
    with gzip.open(path, "rt", encoding="ascii") as f:
        for line in f:
            if line.startswith("##"):
                continue
            p = line.rstrip("\n").split("\t")
            if line.startswith("#CHROM"):
                samples = p[9:]
                continue
            out[p[2]] = [int(g[0]) + int(g[2]) for g in p[9:]]
    return samples, out


def summarise(dose: Path, truth: Path) -> list[dict]:
    t_samples, truth_g = read_truth(truth)
    rows = []
    with gzip.open(dose, "rt", encoding="ascii") as f:
        for line in f:
            if line.startswith("##"):
                continue
            p = line.rstrip("\n").split("\t")
            if line.startswith("#CHROM"):
                if p[9:] != t_samples:
                    raise ValueError("sample columns of dose and truth differ")
                fmt = None
                continue
            fmt = p[8].split(":")
            info = info_dict(p[7])
            tg = truth_g.get(p[2])
            if tg is None or "IMPUTED" not in info:
                continue
            ds = [float(s.split(":")[fmt.index("DS")]) for s in p[9:]]
            ac = sum(tg)
            mac = min(ac, 2 * len(tg) - ac)
            rows.append({"id": p[2], "snv": len(p[3]) == 1 and len(p[4]) == 1, "mac": mac, "maf": mac / (2 * len(tg)),
                         "R2": float(info.get("R2", info.get("DR2", "nan"))), "true": r2(ds, [float(g) for g in tg])})
    return rows


def table(rows: list[dict], label: str) -> None:
    print(f"\n{label}: {len(rows)} imputed variants matched to the truth")
    print(f"   {'class':8} {'n':>6} {'med R2':>7} {'med true':>8} {'R2<0.3':>7} {'R2>=0.8':>8} {'r(R2,true)':>10} {'bias':>7}")
    for name, _ in CLASSES:
        sel = [r for r in rows if maf_class(r["mac"], r["maf"]) == name]
        val = [r for r in sel if r["true"] is not None]
        if not sel:
            continue
        corr = (statistics.correlation([r["R2"] for r in val], [r["true"] for r in val]) if len(val) > 2 else float("nan"))
        print(f"   {name:8} {len(sel):>6} {statistics.median(r['R2'] for r in sel):>7.3f} "
              f"{statistics.median(r['true'] for r in val) if val else float('nan'):>8.3f} "
              f"{sum(r['R2'] < 0.3 for r in sel) / len(sel):>7.0%} {sum(r['R2'] >= 0.8 for r in sel) / len(sel):>8.0%} "
              f"{corr:>10.3f} {statistics.fmean(r['R2'] - r['true'] for r in val) if val else float('nan'):>+7.3f}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dose", required=True, type=Path)
    ap.add_argument("--truth", required=True, type=Path)
    a = ap.parse_args(argv)
    rows = summarise(a.dose, a.truth)
    table(rows, "all")
    table([r for r in rows if r["snv"]], "SNVs")
    table([r for r in rows if not r["snv"]], "indels")
    return 0


if __name__ == "__main__":
    sys.exit(main())
