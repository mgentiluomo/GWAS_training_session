"""Reference QC run of the simulated 2026 dataset: checkpoints and build report (author side only).

    python -I scripts/author/verify_sim2026.py --data C:/WEB_site/data_sources/sim2026

Runs the course steps with PLINK 2 on the files made by make_sim2026.py, compares what each step removes with
the answer key, and measures the association signals: the causal loci, lambda, and the false signals of the
analysis without QC and without principal components (step 7.7).

Writes:
    <data>/student/checkpoints/<step>/   samples and variants removed at the step; full filesets after 4.6 and 5.6
    <data>/instructor/build_report.md    the report (and build_report.json)

The thresholds here are the planned ones. The course notebooks are the final source: when they exist, the
checkpoints must be rebuilt from them.
"""

from __future__ import annotations

import argparse
import collections
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_sim2026  # noqa: E402
import sim2026_core as core  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
GENOME_WIDE = 5e-8
# Provisional long-range LD regions (GRCh38, 1-based) left out of pruning; the course fixes its own list later
HIGH_LD = [("2", 134_000_000, 138_000_000), ("5", 44_000_000, 51_500_000), ("6", 25_000_000, 34_000_000),
           ("8", 7_000_000, 13_000_000), ("11", 46_000_000, 57_000_000), ("17", 45_000_000, 48_000_000)]
HWE_STRUCTURE_NOTE = "population structure (North/South and the ancestry outliers still present at 4.4)"
MARKERS = {"rs4988235": "LCT", "rs12913832": "HERC2", "rs1426654": "SLC24A5"}   # ancestry-informative markers
FALSE_REGIONS = {"LCT": ("2", 134_000_000, 137_500_000), "HERC2/OCA2": ("15", 27_300_000, 28_800_000),
                 "SLC24A5": ("15", 47_600_000, 48_700_000)}


def table(path: Path) -> tuple[list[str], list[list[str]]]:
    """A tab- or space-delimited PLINK 2 report: header names (without '#') and rows."""
    with open(path, encoding="utf-8") as fh:
        lines = [line.rstrip("\n") for line in fh if not line.startswith("##")]
    split = (lambda x: x.split("\t")) if "\t" in lines[0] else (lambda x: x.split())
    return [h.lstrip("#") for h in split(lines[0])], [split(line) for line in lines[1:] if line]


def column(path: Path, name: str) -> list[str]:
    head, rows = table(path)
    k = head.index(name)
    return [r[k] for r in rows]


class Run:
    def __init__(self, data: Path, plink: Path, threads: int):
        self.data, self.plink, self.threads = data, plink, threads
        self.student, self.instructor = data / "student", data / "instructor"
        self.v = data / "work" / "verify"
        if self.v.exists():
            shutil.rmtree(self.v)
        self.v.mkdir(parents=True)
        self.ck = self.student / "checkpoints"
        if self.ck.exists():
            shutil.rmtree(self.ck)
        self.key = json.loads((self.instructor / "answer_key.json").read_text(encoding="utf-8"))
        self.steps: list[dict] = []
        self.timings: dict[str, float] = {}
        self.cur = ""

    def p(self, args: list, name: str = "") -> float:
        cmd = [str(self.plink)] + [str(a) for a in args] + ["--threads", str(self.threads), "--memory", "16000"]
        t = time.perf_counter()
        r = subprocess.run(cmd, capture_output=True, text=True)
        dt = round(time.perf_counter() - t, 1)
        if r.returncode:
            raise RuntimeError("PLINK 2 failed:\n" + " ".join(cmd) + "\n" + r.stdout[-3000:] + r.stderr[-2000:])
        if name:
            self.timings[name] = dt
        return dt

    def ids(self, prefix: str) -> tuple[list[str], list[str]]:
        return column(Path(prefix + ".psam"), "IID"), column(Path(prefix + ".pvar"), "ID")

    def step(self, step: str, title: str, new: str, expected_samples=None, expected_variants=None,
             note: str = "") -> None:
        """Record what a step removed, compare it with the answer key and write the checkpoint lists."""
        s0, v0 = self.ids(self.cur)
        s1, v1 = self.ids(new)
        gone_s, gone_v = sorted(set(s0) - set(s1)), sorted(set(v0) - set(v1))
        d = self.ck / step
        d.mkdir(parents=True, exist_ok=True)
        (d / "removed_samples.txt").write_text("".join(i + "\n" for i in gone_s), encoding="ascii", newline="\n")
        (d / "removed_variants.txt").write_text("".join(i + "\n" for i in gone_v), encoding="ascii", newline="\n")
        row = {"step": step, "title": title, "samples_removed": len(gone_s), "samples_left": len(s1),
               "variants_removed": len(gone_v), "variants_left": len(v1),
               "note": note}
        if expected_samples is not None:
            exp = set(expected_samples)
            row.update(samples_expected=len(exp), samples_unexpected=sorted(set(gone_s) - exp)[:20],
                       samples_missed=sorted(exp - set(gone_s))[:20])
        if expected_variants is not None:
            planned = set(expected_variants)
            exp = planned & set(v0)                    # planted variants still present when the step starts
            row.update(variants_expected=len(exp), variants_gone_earlier=len(planned - set(v0)),
                       variants_unexpected=len(set(gone_v) - exp),
                       variants_missed=len(exp - set(gone_v)),
                       variants_unexpected_examples=sorted(set(gone_v) - exp)[:5],
                       variants_missed_examples=sorted(exp - set(gone_v))[:5])
        self.steps.append(row)
        self.cur = new
        print(f"[{step}] {title}: samples -{len(gone_s)} -> {len(s1)}, variants -{len(gone_v)} -> {len(v1)}", flush=True)


def association(run: Run, prefix: str, covar: Path, covar_names: str, out: str, label: str) -> dict:
    """Logistic regression of Disease on every variant; lambda and genome-wide hits by region."""
    dt = run.p(["--pfile", prefix, "--maf", "0.01", "--covar", covar, "--covar-name", covar_names,
                "--covar-variance-standardize", "--glm", "sex", "hide-covar", "firth-fallback", "--out", out], label)
    path = next(Path(out).parent.glob(Path(out).name + ".*.glm.logistic*"))
    head, rows = table(path)
    c, i, ps, pc = head.index("CHROM"), head.index("ID"), head.index("POS"), head.index("P")
    chrom = np.array([r[c] for r in rows])
    pos = np.array([int(r[ps]) for r in rows])
    ident = [r[i] for r in rows]
    p = np.array([float(r[pc]) if r[pc] not in ("NA", "") else np.nan for r in rows])
    auto = np.array([x.isdigit() for x in chrom])
    result = {"label": label, "seconds": dt, "variants_tested": int(np.isfinite(p).sum()),
              "lambda": round(core.lambda_gc(p[auto]), 3), "genome_wide_hits": int((p < GENOME_WIDE).sum()),
              "loci": {}, "false_regions": {}}
    claimed = np.zeros(len(p), dtype=bool)
    for name, v in run.key["loci"].items():
        near = (chrom == v["chrom"]) & (np.abs(pos - v["pos"]) <= 500_000) & np.isfinite(p)
        claimed |= near
        if near.any():
            k = np.flatnonzero(near)[np.argmin(p[near])]
            result["loci"][name] = {"lead": ident[k], "lead_pos": int(pos[k]), "lead_p": float(p[k]),
                                    "below_5e-8": int((p[near] < GENOME_WIDE).sum()),
                                    "below_1e-5": int((p[near] < 1e-5).sum()),
                                    "distance_to_causal": int(abs(pos[k] - v["pos"]))}
    for name, (ch, lo, hi) in FALSE_REGIONS.items():
        near = (chrom == ch) & (pos >= lo) & (pos <= hi) & np.isfinite(p)
        claimed |= near
        if near.any():
            k = np.flatnonzero(near)[np.argmin(p[near])]
            result["false_regions"][name] = {"lead": ident[k], "lead_pos": int(pos[k]), "lead_p": float(p[k]),
                                             "below_5e-8": int((p[near] < GENOME_WIDE).sum())}
    other = np.flatnonzero((p < GENOME_WIDE) & ~claimed)
    result["other_hits"] = len(other)
    result["other_hits_examples"] = [{"id": ident[k], "chrom": chrom[k], "pos": int(pos[k]), "p": float(p[k])}
                                     for k in other[np.argsort(p[other])][:15]]
    return result


def run_all(run: Run) -> dict:
    key, v, stu = run.key, str(run.v) + "/", run.student
    lab = stu / "lab_export" / "sim2026_lab"
    flow = key["expected_sample_flow"]["removed"]
    kv = key["variants"]
    sheet = [line.rstrip("\n").split(",") for line in open(stu / "lab_export" / "sample_sheet.csv", encoding="ascii")][1:]
    plate = {r[2]: r[0] for r in sheet}
    original = {r[2]: (r[3] or r[2]) for r in sheet}
    pheno = {r[0]: r[1:] for r in table(stu / "phenotypes" / "sim2026_phenotypes.tsv")[1]}

    # 2.2 binary format; 2.5 alleles and strand; 2.7 phenotype and covariates
    run.p(["--bfile", lab, "--make-pgen", "--out", v + "s2-2"], "2.2 make-pgen")
    run.cur = v + "s2-2"
    start_samples, start_variants = (len(x) for x in run.ids(run.cur))
    ann = {r[0]: (r[3], r[4]) for r in table(stu / "array" / "sim2026_array_annotation.tsv")[1]}
    groups = collections.defaultdict(list)
    for line in open(str(lab) + ".bim", encoding="ascii"):
        f = line.split("\t")
        groups[core.allele_check(f[4], f[5].strip(), *ann[f[1]])].append(f[1])
    Path(v + "flip.txt").write_text("\n".join(groups["flip"]) + "\n", encoding="ascii")
    Path(v + "exclude_2-5.txt").write_text("\n".join(groups["palindromic"] + groups["mismatch"]) + "\n", encoding="ascii")
    run.p(["--pfile", v + "s2-2", "--exclude", v + "exclude_2-5.txt", "--flip", v + "flip.txt", "--make-pgen",
           "--out", v + "s2-5"], "2.5 flip and exclude")
    head, rows = table(Path(v + "s2-5.pvar"))
    still_wrong = sum(core.allele_check(r[head.index("REF")], r[head.index("ALT")], *ann[r[head.index("ID")]]) != "same"
                      for r in rows)
    run.step("2.5", "alleles and strand", v + "s2-5", expected_variants=kv["palindromic"] + kv["allele_mismatch"],
             note=f"{len(groups['flip'])} variants flipped (expected {len(kv['strand_flip'])}); "
                  f"{still_wrong} variants still disagree with the annotation")
    with open(v + "pheno_all.tsv", "w", encoding="ascii", newline="\n") as fh:
        fh.write("#FID\tIID\tSEX\tAge\tDisease\n")
        for iid in run.ids(run.cur)[0]:
            sex, age, disease = pheno[original[iid]]
            fh.write(f"{iid}\t{iid}\t{sex}\t{age}\t{disease}\n")
    run.p(["--pfile", v + "s2-5", "--update-sex", v + "pheno_all.tsv", "--pheno", v + "pheno_all.tsv",
           "--pheno-name", "Disease", "--make-pgen", "--out", v + "s2-7"], "2.7 phenotype")
    run.cur = v + "s2-7"
    disease = {iid: pheno[original[iid]][2] for iid in original}

    # 3.1 rough clean, 3.2 call rate
    run.p(["--pfile", run.cur, "--mind", "0.10", "--make-pgen", "--out", v + "s3-1a"])
    run.p(["--pfile", v + "s3-1a", "--geno", "0.10", "--make-pgen", "--out", v + "s3-1"], "3.1 rough clean")
    run.step("3.1", "rough clean (samples and variants below 90% call rate)", v + "s3-1", flow["3.1"],
             list(kv["failed_variants"]))
    run.p(["--pfile", run.cur, "--mind", "0.02", "--make-pgen", "--out", v + "s3-2"], "3.2 call rate")
    run.step("3.2", "sample call rate 98%", v + "s3-2", flow["3.2"], [])

    # 3.3 sex check after moving the pseudo-autosomal variants out of chrX
    run.p(["--pfile", run.cur, "--split-par", "b38", "--make-pgen", "--out", v + "s3-3a"])
    run.p(["--pfile", v + "s3-3a", "--check-sex", "max-female-xf=0.2", "min-male-xf=0.8", "max-female-ycount=100",
           "min-male-ycount=1000", "--out", v + "s3-3"], "3.3 check-sex")
    head, rows = table(Path(v + "s3-3.sexcheck"))
    bad = [r[head.index("IID")] for r in rows if r[head.index("STATUS")] != "OK"]
    par = sum(c.startswith("PAR") for c in column(Path(v + "s3-3a.pvar"), "CHROM"))
    Path(v + "remove_3-3.txt").write_text("".join(f"{i}\t{i}\n" for i in bad), encoding="ascii")
    run.p(["--pfile", v + "s3-3a", "--remove", v + "remove_3-3.txt", "--make-pgen", "--out", v + "s3-3b"])
    run.step("3.3", "sex check", v + "s3-3b", flow["3.3"], [], note=f"{par} variants moved to PAR1/PAR2 by --split-par")

    # 3.4 pruning, 3.5 heterozygosity
    Path(v + "high_ld.bed1").write_text("".join(f"{c}\t{lo}\t{hi}\n" for c, lo, hi in HIGH_LD), encoding="ascii")
    run.p(["--pfile", run.cur, "--chr", "1-22", "--maf", "0.05", "--geno", "0.02", "--exclude", "bed1",
           v + "high_ld.bed1", "--indep-pairwise", "200kb", "0.2", "--out", v + "s3-4"], "3.4 pruning")
    pruned = sum(1 for _ in open(v + "s3-4.prune.in", encoding="ascii"))
    run.p(["--pfile", run.cur, "--extract", v + "s3-4.prune.in", "--het", "--out", v + "s3-5"], "3.5 het")
    head, rows = table(Path(v + "s3-5.het"))
    f = np.array([float(r[head.index("F")]) for r in rows])
    iid = [r[head.index("IID")] for r in rows]
    mean, sd = float(f.mean()), float(f.std())
    low = [i for i, x in zip(iid, f) if x < mean - 3 * sd]
    high = [i for i, x in zip(iid, f) if x > mean + 3 * sd]
    tags = {s["sample_id"]: s["tags"] for s in key["subjects"]}
    high_kinds = collections.Counter(next((t for t in ("consanguineous", "plate14", "outlier") if t in tags.get(original[i], [])),
                                          "other") for i in high)
    Path(v + "remove_3-5.txt").write_text("".join(f"{i}\t{i}\n" for i in low), encoding="ascii")
    run.p(["--pfile", run.cur, "--remove", v + "remove_3-5.txt", "--make-pgen", "--out", v + "s3-5b"])
    f_of = dict(zip(iid, f))
    consang = {i: round(float(f_of[i]), 4) for i, t in tags.items() if "consanguineous" in t and i in f_of}
    run.step("3.5", "heterozygosity (remove F below mean - 3 SD, flag F above mean + 3 SD)", v + "s3-5b", flow["3.5"], [],
             note=f"{pruned} pruned variants; F mean {mean:.4f}, SD {sd:.4f}; flagged high and kept: {len(high)} "
                  f"{dict(high_kinds)}; F of the consanguineous samples: {consang}")

    # 3.6 relatedness and duplicates
    run.p(["--pfile", run.cur, "--extract", v + "s3-4.prune.in", "--make-king-table", "--king-table-filter", "0.0442",
           "--out", v + "s3-6"], "3.6 KING")
    head, rows = table(Path(v + "s3-6.kin0"))
    a, c, kc = head.index("IID1"), head.index("IID2"), head.index("KINSHIP")
    degree = collections.Counter()
    remove = set()
    for r in sorted(rows, key=lambda r: -float(r[kc])):
        kin, i, j = float(r[kc]), r[a], r[c]
        cls = "duplicate" if kin > 0.354 else "first degree" if kin > 0.177 else "second degree" if kin > 0.0884 else "third degree"
        degree[cls] += 1
        if cls == "duplicate":
            if i.endswith("_R2") or j.endswith("_R2"):
                remove.add(i if i.endswith("_R2") else j)
            elif pheno[i] == pheno[j]:
                remove.add(max(i, j))
            else:
                remove |= {i, j}
        elif cls == "first degree" and i not in remove and j not in remove:
            remove.add(max(i, j))
    # pairs above the third-degree bound that are not planned relationships
    planned = {frozenset((p["id_1"], p["id_2"])) for p in key["pairs"]}
    planned |= {frozenset((r["id"], r["replicate_of"])) for r in key["replicates"]}
    tags = {s["sample_id"]: s["tags"] for s in key["subjects"]}
    spurious = []
    for r in rows:
        i, j = r[a], r[c]
        if frozenset((original[i], original[j])) in planned or frozenset((i, j)) in planned or original[i] == original[j]:
            continue
        spurious.append({"iid_1": i, "iid_2": j, "kinship": float(r[kc]),
                         "tags_1": tags.get(original[i], []), "tags_2": tags.get(original[j], [])})
    run.spurious = sorted(spurious, key=lambda x: -x["kinship"])
    Path(v + "remove_3-6.txt").write_text("".join(f"{i}\t{i}\n" for i in sorted(remove)), encoding="ascii")
    run.p(["--pfile", run.cur, "--remove", v + "remove_3-6.txt", "--make-pgen", "--out", v + "s3-6b"])
    # either member of a relative pair may be removed: compare numbers, not names, for those
    run.step("3.6", "relatedness and duplicates", v + "s3-6b", None, [],
             note=f"pairs: {dict(degree)}; removed {len(remove)} (expected {len(flow['3.6'])}); "
                  f"pairs above 0.0442 that are not planned relationships: {len(run.spurious)}")
    run.steps[-1]["samples_expected"] = len(flow["3.6"])

    # 3.7 batch effects: the plate with the worst median call rate
    run.p(["--pfile", run.cur, "--missing", "sample-only", "--out", v + "s3-7"], "3.7 missing")
    head, rows = table(Path(v + "s3-7.smiss"))
    by_plate = collections.defaultdict(list)
    for r in rows:
        by_plate[plate[r[head.index("IID")]]].append(float(r[head.index("F_MISS")]))
    med = {pl: float(np.median(x)) for pl, x in by_plate.items()}
    f_plate = collections.defaultdict(list)
    for i, x in f_of.items():
        f_plate[plate[i]].append(x)
    worst = max(med, key=med.get)
    others = float(np.median([m for pl, m in med.items() if pl != worst]))
    out_ids = [r[head.index("IID")] for r in rows if plate[r[head.index("IID")]] == worst]
    Path(v + "remove_3-7.txt").write_text("".join(f"{i}\t{i}\n" for i in out_ids), encoding="ascii")
    run.p(["--pfile", run.cur, "--remove", v + "remove_3-7.txt", "--make-pgen", "--out", v + "s3-7b"])
    run.step("3.7", "batch effects (remove the faulty plate)", v + "s3-7b", flow["3.7"], [],
             note=f"plate {worst}: median call rate {1 - med[worst]:.4f} against {1 - others:.4f}; mean F "
                  f"{np.mean(f_plate[worst]):+.4f} against {np.mean([x for pl, xs in f_plate.items() if pl != worst for x in xs]):+.4f}")

    # 4.1 to 4.5 variant QC
    run.p(["--pfile", run.cur, "--geno", "0.02", "--make-pgen", "--out", v + "s4-1"], "4.1 geno")
    run.step("4.1", "variant call rate 98%", v + "s4-1", [], list(kv["low_call_variants"]))
    run.p(["--pfile", run.cur, "--test-missing", "--out", v + "s4-2"], "4.2 test-missing")
    head, rows = table(Path(v + "s4-2.missing"))
    pcol = head.index("P")
    bad = [r[head.index("ID")] for r in rows if r[pcol] not in ("NA", "") and float(r[pcol]) < 1e-5]
    Path(v + "exclude_4-2.txt").write_text("\n".join(bad) + "\n", encoding="ascii")
    run.p(["--pfile", run.cur, "--exclude", v + "exclude_4-2.txt", "--make-pgen", "--out", v + "s4-2b"])
    run.step("4.2", "differential missingness (p < 1e-5)", v + "s4-2b", [], list(kv["differential_missingness"]))
    run.p(["--pfile", run.cur, "--maf", "0.01", "--make-pgen", "--out", v + "s4-3"], "4.3 maf")
    run.step("4.3", "minor allele frequency 1%", v + "s4-3", [], None, note="natural frequencies, no planted variants")
    controls = [i for i in run.ids(run.cur)[0] if disease[i] == "1"]
    Path(v + "controls.txt").write_text("".join(f"{i}\t{i}\n" for i in controls), encoding="ascii")
    run.p(["--pfile", run.cur, "--keep", v + "controls.txt", "--chr", "1-22", "--hardy", "midp", "--out", v + "s4-4"],
          "4.4 hardy")
    head, rows = table(Path(v + "s4-4.hardy"))
    pcol = head.index("MIDP") if "MIDP" in head else head.index("P")
    hwe_p = {r[head.index("ID")]: float(r[pcol]) for r in rows if r[pcol] not in ("NA", "")}
    bad = [i for i, x in hwe_p.items() if x < 1e-6]
    Path(v + "exclude_4-4.txt").write_text("\n".join(bad) + "\n", encoding="ascii")
    run.p(["--pfile", run.cur, "--exclude", v + "exclude_4-4.txt", "--make-pgen", "--out", v + "s4-4b"])
    mild = [hwe_p[i] for i in kv["hwe_mild"] if i in hwe_p]
    planted_hwe = set(kv["hwe_strong"]) | set(kv["hwe_mild"])
    pos_of = dict(zip(column(Path(run.cur + ".pvar"), "ID"), zip(column(Path(run.cur + ".pvar"), "CHROM"),
                                                                 column(Path(run.cur + ".pvar"), "POS"))))
    discordant_copies = {d["duplicate"] for d in kv["duplicated"] if d["genotypes_changed"] > 0}
    run.hwe_discordant_copies = [{"id": i, "p_controls": hwe_p[i],
                                  "note": "copy of a discordant duplicated variant (planted for 4.5): its changed "
                                          "genotypes also break HWE"}
                                 for i in sorted(bad, key=lambda x: hwe_p[x]) if i in discordant_copies]
    run.hwe_not_planted = [{"id": i, "chrom": pos_of[i][0], "pos": int(pos_of[i][1]), "p_controls": hwe_p[i],
                            "note": HWE_STRUCTURE_NOTE}
                           for i in sorted(bad, key=lambda x: hwe_p[x])
                           if i not in planted_hwe and i not in discordant_copies]
    gone = [m for m in MARKERS if any(x["id"] == m for x in run.hwe_not_planted)]
    run.markers_removed_at_4_4 = gone
    run.step("4.4", "Hardy-Weinberg in controls (p < 1e-6)", v + "s4-4b", [], kv["hwe_strong"],
             note=f"mild errors kept: {sum(x >= 1e-6 for x in mild)} of {len(mild)} (median p {np.median(mild) if mild else float('nan'):.2g}); "
                  f"{len(run.hwe_not_planted)} variants not planted also fail (listed apart); "
                  f"{len(run.hwe_discordant_copies)} copies of discordant duplicated variants also fail"
                  + (f"; {', '.join(f'{m} ({MARKERS[m]})' for m in gone)} removed here, so they do not reach module 5"
                     if gone else ""))
    run.p(["--pfile", run.cur, "--chr", "X,Y,MT", "--export", "A", "--out", v + "s4-5"], "4.5 export sex chromosomes")
    with open(v + "s4-5.raw", encoding="ascii") as fh:
        head = fh.readline().split()
        rows = [line.split() for line in fh]
    sex = np.array([r[head.index("SEX")] for r in rows])
    g = np.array([[-1 if x == "NA" else int(x) for x in r[6:]] for r in rows], dtype=np.int8)
    names = [h.rsplit("_", 1)[0] for h in head[6:]]
    chrom_of = dict(zip(column(Path(run.cur + ".pvar"), "ID"), column(Path(run.cur + ".pvar"), "CHROM")))
    bad = []
    for k, name in enumerate(names):
        ch = chrom_of[name]
        if ch == "X":
            wrong = (g[sex == "1", k] == 1).mean()
        elif ch == "Y":
            wrong = (g[sex == "2", k] >= 0).mean()
        else:
            wrong = (g[:, k] == 1).mean()
        if wrong > 0.01:
            bad.append(name)
    Path(v + "exclude_4-5.txt").write_text("\n".join(bad) + "\n", encoding="ascii")
    run.p(["--pfile", run.cur, "--exclude", v + "exclude_4-5.txt", "--make-pgen", "--out", v + "s4-5a"])
    expected = [d["name"] for group in ("x_male_het", "y_female_call", "mt_het") for d in kv[group]]
    run.step("4.5a", "sex chromosomes and MT (calls that do not fit the sex)", v + "s4-5a", [], expected)
    present = set(run.ids(run.cur)[1])
    n_before = len(present)
    run.p(["--pfile", run.cur, "--set-all-var-ids", "@:#:$r:$a", "--rm-dup", "exclude-mismatch", "list",
           "--make-pgen", "--out", v + "s4-5b"], "4.5 rm-dup")
    n_after = len(run.ids(v + "s4-5b")[1])
    # only pairs whose two copies both reached this step
    both = [d for d in kv["duplicated"] if d["name"] in present and d["duplicate"] in present]
    concordant = sum(d["genotypes_changed"] == 0 for d in both)
    discordant = len(both) - concordant
    run.steps.append({"step": "4.5b", "title": "duplicated variants (IDs become chr:pos:ref:alt)",
                      "samples_removed": 0, "samples_left": len(run.ids(v + "s4-5b")[0]),
                      "variants_removed": n_before - n_after, "variants_left": n_after,
                      "variants_expected": concordant + 2 * discordant,
                      "note": f"{concordant} concordant pairs lose one copy, {discordant} discordant pairs lose both"})
    run.cur = v + "s4-5b"
    print(f"[4.5b] duplicated variants: -{n_before - n_after} -> {n_after}", flush=True)
    for step, state in (("4.6", "s4-5b"),):
        (run.ck / step).mkdir(parents=True, exist_ok=True)
        run.p(["--pfile", v + state, "--make-pgen", "--out", run.ck / step / "sim2026_after_variant_qc"])

    # 5 population structure: reference PCA, projection, outliers
    ref = stu / "pca_reference" / "ref1000g_grch38"
    common = sorted(set(run.ids(run.cur)[1]) & set(column(Path(str(ref) + ".pvar"), "ID")))
    Path(v + "common.txt").write_text("\n".join(common) + "\n", encoding="ascii")
    run.p(["--pfile", ref, "--extract", v + "common.txt", "--freq", "--pca", "10", "allele-wts", "--out", v + "s5-4"],
          "5.4 reference PCA")
    head, _ = table(Path(v + "s5-4.eigenvec.allele"))
    id_col, a1_col, first = head.index("ID") + 1, head.index("A1") + 1, head.index("PC1") + 1
    score = ["--read-freq", v + "s5-4.afreq", "--score", v + "s5-4.eigenvec.allele", id_col, a1_col, "header-read",
             "no-mean-imputation", "variance-standardize", "--score-col-nums", f"{first}-{first + 9}"]
    run.p(["--pfile", ref, "--extract", v + "common.txt"] + score + ["--out", v + "s5-4_ref"])
    run.p(["--pfile", run.cur, "--extract", v + "common.txt"] + score + ["--out", v + "s5-4_study"], "5.4 projection")

    def scores(path):
        head, rows = table(Path(path))
        cols = [k for k, h in enumerate(head) if h.startswith("PC") and h.endswith("_AVG")]
        return [r[head.index("IID")] for r in rows], np.array([[float(r[k]) for k in cols] for r in rows])

    ref_ids, ref_pc = scores(v + "s5-4_ref.sscore")
    study_ids, study_pc = scores(v + "s5-4_study.sscore")
    superpop = dict(zip(column(Path(str(ref) + ".psam"), "IID"), column(Path(str(ref) + ".psam"), "SuperPop")))
    eur = np.array([superpop[i] == "EUR" for i in ref_ids])
    z = (study_pc[:, :4] - ref_pc[eur, :4].mean(axis=0)) / ref_pc[eur, :4].std(axis=0)
    outliers = [i for i, row in zip(study_ids, z) if np.abs(row).max() > 6]
    Path(v + "remove_5-6.txt").write_text("".join(f"{i}\t{i}\n" for i in outliers), encoding="ascii")
    run.p(["--pfile", run.cur, "--remove", v + "remove_5-6.txt", "--make-pgen", "--out", v + "s5-6"])
    run.step("5.6", "ancestry outliers (6 SD of the European reference on PC1 to PC4)", v + "s5-6", flow["5.6"], [],
             note=f"{len(common)} variants shared with the reference")
    (run.ck / "5.6").mkdir(parents=True, exist_ok=True)
    run.p(["--pfile", v + "s5-6", "--make-pgen", "--out", run.ck / "5.6" / "sim2026_after_ancestry"])

    # 5.7 / 6.3 principal components of the cohort, then the association
    run.p(["--pfile", run.cur, "--chr", "1-22", "--maf", "0.05", "--exclude", "bed1", v + "high_ld.bed1",
           "--indep-pairwise", "200kb", "0.2", "--out", v + "s5-7"])
    run.p(["--pfile", run.cur, "--extract", v + "s5-7.prune.in", "--pca", "10", "--out", v + "s5-7"], "5.7 cohort PCA")
    head, rows = table(Path(v + "s5-7.eigenvec"))
    pcs = {r[head.index("IID")]: r[head.index("PC1"):head.index("PC1") + 10] for r in rows}
    pool = {s["sample_id"]: s["pool"] for s in key["subjects"]}
    pc1 = np.array([float(pcs[i][0]) for i in pcs])
    south = np.array([pool[original[i]] == "S" for i in pcs])
    separation = abs(pc1[south].mean() - pc1[~south].mean()) / pc1.std()
    with open(v + "covar.tsv", "w", encoding="ascii", newline="\n") as fh:
        fh.write("#FID\tIID\tAge\t" + "\t".join(f"PC{k}" for k in range(1, 11)) + "\n")
        for iid in original:
            fh.write(f"{iid}\t{iid}\t{pheno[original[iid]][1]}\t" + "\t".join(pcs.get(iid, ["0"] * 10)) + "\n")
    results = {
        "with_qc_and_pcs": association(run, run.cur, Path(v + "covar.tsv"), "Age,PC1-PC10", v + "s6-4", "6.4 glm, QC and 10 PCs"),
        "with_qc_no_pcs": association(run, run.cur, Path(v + "covar.tsv"), "Age", v + "s6-3_nopc", "glm, QC, no PCs"),
        "no_qc_no_pcs": association(run, v + "s2-7", Path(v + "covar.tsv"), "Age", v + "s7-7", "7.7 glm, no QC, no PCs"),
    }
    king = table(Path(v + "s3-6.kin0"))
    sizes = {str(p.relative_to(run.student)).replace("\\", "/"): p.stat().st_size
             for p in sorted(run.student.rglob("*")) if p.is_file()}
    report = {"start": {"samples": start_samples, "variants": start_variants}, "steps": run.steps,
              "final": dict(zip(("samples", "variants"), (len(x) for x in run.ids(run.cur)))),
              "expected_final_samples": key["expected_sample_flow"]["final"], "association": results,
              "pc1_north_south_separation_sd": round(float(separation), 2),
              "pairs_above_third_degree_at_3.6": len(king[1]), "spurious_pairs_at_3.6": run.spurious,
              "hwe_failures_not_planted_at_4.4": run.hwe_not_planted,
              "hwe_failures_discordant_duplicate_copies_at_4.4": run.hwe_discordant_copies,
              "copy_check": key["copy_check"], "loci": key["loci"],
              "timings_s": run.timings, "student_file_bytes": sizes, "student_total_bytes": sum(sizes.values())}
    (run.instructor / "build_report.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    # the answer key also records what the reference run observed but was not planted
    key["observed_in_reference_run"] = {
        "hwe_failures_not_planted_at_4.4": run.hwe_not_planted,
        "markers_removed_at_4.4_not_reaching_module_5": {m: MARKERS[m] for m in run.markers_removed_at_4_4},
        "spurious_pairs_at_3.6": run.spurious}
    (run.instructor / "answer_key.json").write_text(json.dumps(key, indent=1) + "\n", encoding="utf-8")
    (run.instructor / "build_report.md").write_text(markdown(report), encoding="utf-8")
    (run.ck / "README.txt").write_text(CHECKPOINTS_README, encoding="ascii", newline="\n")
    return report


def markdown(r: dict) -> str:
    lines = ["# Simulated 2026 dataset: build report (instructor only)", "",
             f"Start: {r['start']['samples']} samples, {r['start']['variants']} variants. "
             f"End: {r['final']['samples']} samples (expected {r['expected_final_samples']}), {r['final']['variants']} variants.",
             "", "## QC steps", "", "| Step | What | Samples removed (expected) | Samples left | Variants removed (expected) | Variants left | Notes |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for s in r["steps"]:
        es = f" ({s['samples_expected']})" if "samples_expected" in s else ""
        ev = f" ({s['variants_expected']})" if "variants_expected" in s else ""
        extra = []
        if s.get("samples_unexpected") or s.get("samples_missed"):
            extra.append(f"unexpected {s.get('samples_unexpected')}, missed {s.get('samples_missed')}")
        if s.get("variants_unexpected") or s.get("variants_missed"):
            extra.append(f"variants: {s['variants_unexpected']} unexpected, {s['variants_missed']} missed")
        note = "; ".join([s.get("note", "")] + extra).strip("; ")
        lines.append(f"| {s['step']} | {s['title']} | {s['samples_removed']}{es} | {s['samples_left']} | "
                     f"{s['variants_removed']}{ev} | {s['variants_left']} | {note} |")
    lines += ["", "## Association", ""]
    for name, a in r["association"].items():
        lines += [f"### {a['label']}", "", f"Lambda {a['lambda']}; {a['variants_tested']} variants tested; "
                  f"{a['genome_wide_hits']} below 5e-8, of which {a['other_hits']} outside the loci and the known "
                  f"stratification regions ({a['seconds']} s).", "",
                  "| Region | Lead | p | Variants below 5e-8 |", "| --- | --- | --- | --- |"]
        for kind in ("loci", "false_regions"):
            for region, x in a[kind].items():
                lines.append(f"| {region} | {x['lead']} | {x['lead_p']:.2e} | {x['below_5e-8']} |")
        lines.append("")
    c = r["copy_check"]
    lines += ["## Kinship", ""] + make_sim2026.copy_check_markdown(c)
    lines += [f"Pairs above the third-degree bound at step 3.6: {r['pairs_above_third_degree_at_3.6']}, of which "
              f"{len(r['spurious_pairs_at_3.6'])} are not planned relationships:", ""]
    lines += [f"- {x['iid_1']} {x['tags_1']} and {x['iid_2']} {x['tags_2']}: {x['kinship']:.4f}"
              for x in r["spurious_pairs_at_3.6"][:30]]
    hw = r["hwe_failures_not_planted_at_4.4"]
    lines += ["", "## Variants not planted that fail HWE in the controls (step 4.4)", "",
              f"Cause: {HWE_STRUCTURE_NOTE}. The controls mix groups with different allele frequencies, so they "
              "show fewer heterozygotes than HWE predicts. These are not genotyping errors.", "",
              "| Variant | Chromosome | Position | p in controls |", "| --- | --- | --- | --- |"]
    lines += [f"| {x['id']} | {x['chrom']} | {x['pos']} | {x['p_controls']:.2e} |" for x in hw]
    gone = [m for m in MARKERS if any(x["id"] == m for x in hw)]
    if gone:
        lines += ["", ", ".join(f"{m} ({MARKERS[m]})" for m in gone) + " leave at step 4.4 and do not reach module 5."]
    lines += ["", f"PC1 separates North and South by {r['pc1_north_south_separation_sd']} SD.", "", "## Files and times", "",
              f"Student files: {r['student_total_bytes'] / 1e6:.1f} MB in total.", "", "| File | MB |", "| --- | --- |"]
    lines += [f"| {name} | {size / 1e6:.2f} |" for name, size in r["student_file_bytes"].items() if size > 200_000]
    lines += ["", "| PLINK 2 step | Seconds |", "| --- | --- |"]
    lines += [f"| {name} | {t} |" for name, t in r["timings_s"].items()]
    return "\n".join(lines) + "\n"


CHECKPOINTS_README = """\
Checkpoints of the simulated 2026 dataset

Each folder is one step of the course. removed_samples.txt and removed_variants.txt list what the step
removes (the IDs as they are at that step; from step 4.5 on, variant IDs have the form chr:pos:ref:alt).
The folders 4.6 and 5.6 also hold the full PLINK 2 fileset after the step.
"""


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--data", type=Path, required=True, help="the folder written by make_sim2026.py")
    p.add_argument("--threads", type=int, default=2, help="2 = a student's laptop")
    a = p.parse_args()
    data = a.data.resolve()
    if data == REPO or REPO in data.parents:
        sys.exit("--data must be outside the repository")
    report = run_all(Run(data, REPO / "bin" / "plink2.exe", a.threads))
    print(markdown(report))


if __name__ == "__main__":
    main()
