"""Count the samples of an imputation reference panel and its variants in given regions.

Author side only. Used for module A (genotype imputation).

The panel is the 1000 Genomes 30x callset minus the template donors of the simulated data and minus the
related samples of the KING lists. For each region PLINK 2 counts the variants that are polymorphic in the
panel, split into SNVs and other variants (indels) and into frequency classes. With --donors-superpop the
script also reports how many variants polymorphic in those donors are polymorphic in the panel too.

Example:
    python -I panel_count.py --callset-dir <1000G folder> --donors <donors_all.keep> --plink <plink2>
        --work <folder> --region chr18_L4:18:36792715:39292715 --region chr22:22:35000000:37500000
"""

from __future__ import annotations

import argparse
import collections
import subprocess
import sys
from pathlib import Path

ORDER = ["MAC 1", "MAC 2-4", "MAF <0.5%", "MAF 0.5-1%", "MAF 1-5%", "MAF >=5%"]


def ids(path: Path) -> set[str]:
    return {l.split()[-1] for l in open(path, encoding="utf-8") if l.strip() and not l.startswith("#")}


def counts(path: Path) -> dict[tuple[str, str, str], tuple[int, int, bool]]:
    """Allele counts keyed by (position, REF, ALT): the callset IDs are rsIDs or '.', so they are not unique."""
    out = {}
    with open(path, encoding="utf-8") as f:
        h = f.readline().lstrip("#").split()
        for line in f:
            p = line.split()
            alts = p[h.index("ALT")].split(",")
            ac = sum(int(x) for x in p[h.index("ALT_CTS")].split(","))
            snv = len(alts) == 1 and len(p[h.index("REF")]) == 1 and len(alts[0]) == 1
            out[(p[h.index("POS")], p[h.index("REF")], p[h.index("ALT")])] = (ac, int(p[h.index("OBS_CT")]), snv)
    return out


def freq_class(ac: int, obs: int) -> str:
    mac = min(ac, obs - ac)
    maf = mac / obs
    return ("MAC 1" if mac == 1 else "MAC 2-4" if mac < 5 else "MAF <0.5%" if maf < 0.005
            else "MAF 0.5-1%" if maf < 0.01 else "MAF 1-5%" if maf < 0.05 else "MAF >=5%")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--callset-dir", required=True, type=Path,
                    help="folder with all_hg38.pgen, all_hg38_rs_noannot.pvar.zst, hg38_corrected.psam and the KING lists")
    ap.add_argument("--donors", required=True, type=Path, help="donors_all.keep of the simulated build")
    ap.add_argument("--plink", required=True)
    ap.add_argument("--work", required=True, type=Path)
    ap.add_argument("--region", action="append", required=True, help="name:chrom:start:end (bp, inclusive)")
    ap.add_argument("--donors-superpop", default="EUR", help="superpopulation of the donors to compare; empty to skip")
    a = ap.parse_args(argv)
    kg, w = a.callset_dir, a.work
    w.mkdir(parents=True, exist_ok=True)
    rows = [l.rstrip("\n").split("\t") for l in open(kg / "hg38_corrected.psam", encoding="utf-8")]
    h = [c.lstrip("#") for c in rows[0]]
    info = {r[0]: (r[h.index("SuperPop")], r[h.index("Population")]) for r in rows[1:]}
    donors = ids(a.donors)
    related = ids(kg / "deg2_hg38.king.cutoff.out.id") | ids(kg / "deg2_hg38_set2.king.cutoff.out.id")
    panel = sorted(set(info) - donors - related)
    print(f"callset {len(info)} | donors {len(donors)} | KING-related {len(related)} | both {len(donors & related)}"
          f" | panel {len(panel)}")
    print("panel by superpopulation:", dict(sorted(collections.Counter(info[i][0] for i in panel).items())))
    (w / "panel.keep").write_text("#IID\n" + "\n".join(panel) + "\n", encoding="utf-8")
    sel = [i for i in donors if info[i][0] == a.donors_superpop] if a.donors_superpop else []
    if sel:
        (w / "donors_sel.keep").write_text("#IID\n" + "\n".join(sorted(sel)) + "\n", encoding="utf-8")
    callset = ["--pgen", str(kg / "all_hg38.pgen"), "--pvar", str(kg / "all_hg38_rs_noannot.pvar.zst"),
               "--psam", str(kg / "hg38_corrected.psam")]
    for spec in a.region:
        name, chrom, lo, hi = spec.split(":")
        for who, keep in (("panel", "panel.keep"), ("donors", "donors_sel.keep")):
            if who == "donors" and not sel:
                continue
            r = subprocess.run([a.plink] + callset + ["--keep", str(w / keep), "--chr", chrom, "--from-bp", lo,
                                                      "--to-bp", hi, "--freq", "counts", "cols=+pos", "--nonfounders", "--threads",
                                                      "4", "--out", str(w / f"{name}_{who}")], capture_output=True, text=True)
            if r.returncode:
                sys.stderr.write(r.stdout[-2000:] + r.stderr[-2000:])
                return 1
        pc = counts(w / f"{name}_panel.acount")
        poly = {k: v for k, v in pc.items() if 0 < v[0] < v[1]}
        cls = collections.Counter(freq_class(v[0], v[1]) for v in poly.values())
        print(f"\n{name}: chr{chrom}:{int(lo):,}-{int(hi):,} | records {len(pc):,} | polymorphic in panel {len(poly):,}"
              f" (SNVs {sum(v[2] for v in poly.values()):,}, other {sum(not v[2] for v in poly.values()):,})")
        print("   " + ", ".join(f"{k} {cls[k]:,}" for k in ORDER))
        if sel:
            dc = counts(w / f"{name}_donors.acount")
            dpoly = {k: v for k, v in dc.items() if 0 < v[0] < v[1]}
            inp = sum(k in poly for k in dpoly)
            print(f"   polymorphic in {a.donors_superpop} donors {len(dpoly):,}; also in the panel {inp:,}"
                  f" ({inp / max(1, len(dpoly)):.0%})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
