"""Compare linkage disequilibrium in the simulated study with a reference panel, on the same SNPs.

Author side only. Used for module A to check that the simulated data have realistic LD.

PLINK 2 computes unphased r2 between SNPs within a window (default 250 kb) in three sample sets: the study
state, the study restricted to a second sample list (for example the 5.7 cohort), and the reference samples
of one superpopulation. The script reports the Pearson and Spearman correlation of the r2 values and their
distribution by distance, for SNPs with MAF at or above a threshold in both sets.

Example:
    python -I ld_compare.py --state <4.6 prefix> --cohort-psam <5.7 .psam> --reference <panel prefix>
        --superpop EUR --chrom 22 --plink <plink2> --work <folder>
"""

from __future__ import annotations

import argparse
import math
import statistics
import subprocess
import sys
from pathlib import Path

BINS = [(0, 10), (10, 25), (25, 50), (50, 100), (100, 150), (150, 250)]


def ids(pvar: Path, chrom: str) -> set[str]:
    with open(pvar, encoding="utf-8") as f:
        return {l.split("\t")[2] for l in f if not l.startswith("#") and l.split("\t")[0] in (chrom, "chr" + chrom)}


def read_maf(path: Path) -> dict[str, float]:
    out = {}
    with open(path, encoding="utf-8") as f:
        h = f.readline().lstrip("#").split()
        for line in f:
            p = line.split()
            a = float(p[h.index("ALT_FREQS")])
            out[p[h.index("ID")]] = min(a, 1 - a)
    return out


def read_pairs(path: Path) -> dict[tuple[str, str], tuple[int, float]]:
    out = {}
    with open(path, encoding="utf-8") as f:
        h = f.readline().lstrip("#").split()
        for line in f:
            p = line.split()
            v = p[h.index("UNPHASED_R2")]
            if v.lower() != "nan":
                d = abs(int(p[h.index("POS_B")]) - int(p[h.index("POS_A")]))
                out[(p[h.index("ID_A")], p[h.index("ID_B")])] = (d, float(v))
    return out


def pearson(x: list[float], y: list[float]) -> float:
    mx, my = statistics.fmean(x), statistics.fmean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return sxy / math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))


def ranks(v: list[float]) -> list[float]:
    order = sorted(range(len(v)), key=v.__getitem__)
    r = [0.0] * len(v)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def compare(work: Path, a: str, b: str, min_maf: float) -> None:
    fa, fb = read_maf(work / f"{a}.afreq"), read_maf(work / f"{b}.afreq")
    pa, pb = read_pairs(work / f"{a}.vcor"), read_pairs(work / f"{b}.vcor")
    keys = [k for k in pa.keys() & pb.keys() if all(fa[s] >= min_maf and fb[s] >= min_maf for s in k)]
    x, y = [pa[k][1] for k in keys], [pb[k][1] for k in keys]
    print(f"\n== {a} vs {b}, MAF >= {min_maf} in both: {len({s for k in keys for s in k})} SNPs, {len(keys)} pairs")
    print(f"   Pearson {pearson(x, y):.3f} | Spearman {pearson(ranks(x), ranks(y)):.3f}"
          f" | mean |difference| {statistics.fmean(abs(p - q) for p, q in zip(x, y)):.3f}")
    print(f"   {'kb':>9} {'pairs':>6} | {a} mean, median, >0.2 | {b} mean, median, >0.2 | Pearson")
    for lo, hi in BINS:
        ks = [k for k in keys if lo * 1000 <= pa[k][0] < hi * 1000]
        if len(ks) < 3:
            continue
        xa, xb = [pa[k][1] for k in ks], [pb[k][1] for k in ks]
        share = lambda v: sum(z > 0.2 for z in v) / len(v)
        print(f"   {f'{lo}-{hi}':>9} {len(ks):>6} | {statistics.fmean(xa):.3f} {statistics.median(xa):.3f} {share(xa):.1%}"
              f" | {statistics.fmean(xb):.3f} {statistics.median(xb):.3f} {share(xb):.1%} | {pearson(xa, xb):.3f}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--state", required=True, help="study PLINK 2 prefix (for example the 4.6 state)")
    ap.add_argument("--cohort-psam", help="optional .psam whose IIDs form a second study set (for example 5.7)")
    ap.add_argument("--reference", required=True, help="reference panel PLINK 2 prefix with a SuperPop column")
    ap.add_argument("--superpop", default="EUR")
    ap.add_argument("--chrom", default="22")
    ap.add_argument("--window-kb", default="250")
    ap.add_argument("--min-maf", type=float, nargs="+", default=[0.01, 0.05])
    ap.add_argument("--plink", required=True)
    ap.add_argument("--work", required=True, type=Path)
    a = ap.parse_args(argv)
    w = a.work
    w.mkdir(parents=True, exist_ok=True)
    common = sorted(ids(Path(a.state + ".pvar"), a.chrom) & ids(Path(a.reference + ".pvar"), a.chrom))
    (w / "common.txt").write_text("\n".join(common) + "\n", encoding="utf-8")
    with open(a.reference + ".psam", encoding="utf-8") as f:
        head = f.readline().lstrip("#").rstrip("\n").split("\t")
        ref_ids = [l.split("\t")[0] for l in f if l.rstrip("\n").split("\t")[head.index("SuperPop")] == a.superpop]
    (w / "reference.keep").write_text("#IID\n" + "\n".join(ref_ids) + "\n", encoding="utf-8")
    print(f"common chr{a.chrom} SNPs: {len(common)} | {a.superpop} reference samples: {len(ref_ids)}")
    ld = ["--chr", a.chrom, "--extract", str(w / "common.txt"), "--r2-unphased", "--ld-window-kb", a.window_kb,
          "--ld-window", "100000", "--ld-window-r2", "0", "--freq", "--threads", "2"]
    runs = {"study": ["--pfile", a.state], "reference": ["--pfile", a.reference, "--keep", str(w / "reference.keep")]}
    if a.cohort_psam:
        with open(a.cohort_psam, encoding="utf-8") as f:
            f.readline()
            cohort = [l.split("\t")[1] for l in f]
        (w / "cohort.keep").write_text("#FID\tIID\n" + "".join(f"{i}\t{i}\n" for i in cohort), encoding="utf-8")
        runs["cohort"] = ["--pfile", a.state, "--keep", str(w / "cohort.keep")]
    for name, src in runs.items():
        r = subprocess.run([a.plink] + src + ld + ["--out", str(w / name)], capture_output=True, text=True)
        if r.returncode:
            sys.stderr.write(r.stdout + r.stderr)
            return 1
    for maf in a.min_maf:
        compare(w, "study", "reference", maf)
    if a.cohort_psam:
        compare(w, "cohort", "reference", max(a.min_maf))
    return 0


if __name__ == "__main__":
    sys.exit(main())
