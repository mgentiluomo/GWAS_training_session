"""Build the simulated 2026 course dataset (author side only; students never run this).

    python -I scripts/author/make_sim2026.py --out C:/WEB_site/data_sources/sim2026

Every individual is a mosaic of phased 1000 Genomes haplotypes (30x GRCh38 callset), so allele frequencies and
linkage disequilibrium look real, but no individual is a real person or a copy of one. Phenotypes, planted
problems and association signals are simulated. The inputs are local files that never enter the repository:
the 1000 Genomes callset, the GSA-like site list, the GRCh38 genetic map and PLINK 2 (docs/data_provenance.tsv).

Output (outside the repository):
    <out>/student/      files for the encrypted course release
    <out>/instructor/   answer key, build record with the seed, imputation truth: never given to students
    <out>/work/         intermediate files, safe to delete

The pure parts (mosaics, meiosis, kinship, planting, writers) are in sim2026_core.py and are tested on a
synthetic donor panel. The reference QC run, the checkpoints and the report are in verify_sim2026.py.
"""

from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import platform
import random
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sim2026_core as core  # noqa: E402
from sim2026_core import Person  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DATA = Path(r"C:\WEB_site\data_sources")                       # author machine: local inputs
REFERENCE_SOURCES = Path(r"K:\Software_DEV\reference_sources")  # author machine: read only
AUTOSOMES = [str(c) for c in range(1, 23)]
CHROM_ORDER = {c: k for k, c in enumerate(AUTOSOMES + ["X", "Y", "MT"])}

# Study design (agreed with the author, November 2026)
N_STUDY, N_REPLICATES, N_PLATES, BAD_PLATE = 2000, 16, 21, 14
QUOTA = {(2, "S"): 582, (2, "N"): 388, (1, "S"): 396, (1, "N"): 594}    # European subjects: 60% / 40% South
OUTLIERS = {"AFR": 15, "SAS": 10, "EAS": 8, "ADM": 7}                  # 30 cases, 10 controls
P_MALE = {2: 0.5427, 1: 0.4973}                                        # sex odds ratio 1.2, 52% men overall
LOCI = {"L1": dict(chrom="3", freq=0.30, odds_ratio=1.8, on_array=True),
        "L2": dict(chrom="9", freq=0.15, odds_ratio=2.0, on_array=True),
        "L3": dict(chrom="12", freq=0.45, odds_ratio=1.7, on_array=True),
        "L4": dict(chrom="18", freq=0.25, odds_ratio=1.4, on_array=False)}
FORCED_MARKERS = ("rs4988235", "rs1426654", "rs12913832")              # LCT, SLC24A5, HERC2
PROTECTED = [("2", 134_000_000, 137_500_000), ("15", 27_300_000, 28_800_000), ("15", 47_600_000, 48_700_000)]
IMPUTATION_CHR22 = ("22", 36_000_000, 36_500_000)
PLANTED = dict(strand_flip=400, palindromic=3000, palindromic_flipped=30, allele_mismatch=20, failed_variants=150,
               low_call_variants=800, differential_missingness=120, hwe_strong=150, hwe_mild=50, x_male_het=15,
               y_female_call=10, mt_het=8, duplicate_pairs=300, duplicate_discordant=20, par_sites=520)
# rsID -> (chromosome, GRCh37 position); checked against the chain file at build time
KNOWN_SNPS = {"rs4988235": ("2", 136608646), "rs7903146": ("10", 114758349), "rs12913832": ("15", 28365618),
              "rs1426654": ("15", 48426484), "rs429358": ("19", 45411941), "rs7412": ("19", 45412079),
              "rs1801133": ("1", 11856378), "rs9939609": ("16", 53820527), "rs1333049": ("9", 22125503),
              "rs6025": ("1", 169519049), "rs16891982": ("5", 33951693), "rs1800562": ("6", 26093141),
              "rs713598": ("7", 141673345), "rs671": ("12", 112241766), "rs1042522": ("17", 7579472),
              "rs2187668": ("6", 32605884), "rs334": ("11", 5248232)}
STUDENT_DIRS = ("lab_export", "phenotypes", "array", "pca_reference", "final_report", "grch37_exercise",
                "imputation")


@dataclass
class Settings:
    out: Path
    seed: int = 20261111
    plink: Path = REPO / "bin" / "plink2.exe"
    kg_dir: Path = DATA / "1000G_hg38_b38_2022-08-04"
    design_dir: Path = DATA / "gsa_like_design_grch38"
    map_dir: Path = DATA / "genetic_map_grch38_from_hapmap2"
    chain: Path = REFERENCE_SOURCES / "liftover" / "hg19ToHg38.over.chain.gz"
    map37_dir: Path = REFERENCE_SOURCES / "genetic_map_grch37" / "extracted"
    mean_segment_cm: float = 3.0
    max_copy_cm: float = 10.0
    allele_error_rate: float = 0.0005
    plate_het_loss: float = 0.04                 # bad plate: chance that a heterozygous call becomes homozygous
    template_share: float = 0.5
    only_chromosomes: tuple[str, ...] | None = None   # debugging: build a few chromosomes only
    threads: int = 16
    memory_mb: int = 24000


@dataclass
class Subject:
    """One study ID. Two subjects share a `person` when the same DNA was entered twice by mistake."""
    person: int
    status: int                                  # 2 case, 1 control
    sex: int = 0                                 # declared sex: 1 male, 2 female
    age: int = 0
    tags: list[str] = field(default_factory=list)
    sample_id: str = ""


@dataclass
class Roster:
    people: list[Person]
    subjects: list[Subject]
    wells: list[dict]                            # subject, person, sample_id, replicate_of, plate, position
    pairs: list[tuple[str, int, int]]            # planted relationships between subjects
    contaminants: dict[int, tuple[int, float]]   # subject -> (contaminating person, share)
    grch37_people: list[int]


# --- the study: who is in it --------------------------------------------------------------------------------

def make_roster(rng: np.random.Generator, n_grch37: int = 120) -> Roster:
    """People (genomes), subjects (study IDs) and wells, with every planted sample problem on its own subjects."""
    people: list[Person] = []
    subjects: list[Subject] = []
    used: collections.Counter = collections.Counter()
    pairs: list[tuple[str, int, int]] = []

    def person(pool, sex, **kw) -> int:
        people.append(Person(pool=pool, sex=sex, **kw))
        return len(people) - 1

    def subject(pid, status, tags) -> int:
        subjects.append(Subject(pid, status, tags=list(tags)))
        people[pid].status = status
        if people[pid].pool in ("N", "S"):
            used[(status, people[pid].pool)] += 1
        return len(subjects) - 1

    pool_ = lambda: "S" if rng.random() < 0.5 else "N"                       # noqa: E731
    status_ = lambda: 2 if rng.random() < 0.5 else 1                         # noqa: E731
    sex_ = lambda status=0: 1 if rng.random() < P_MALE.get(status, 0.5) else 2   # noqa: E731

    for _ in range(6):                                           # parent and child, the other parent is hidden
        pool, st = pool_(), status_()
        parent = person(pool, sex_(st), kind="parent")
        sp = subject(parent, st, ["relative", "parent"])
        other = person(pool, 3 - people[parent].sex, kind="hidden")
        mother, father = (parent, other) if people[parent].sex == 2 else (other, parent)
        st = status_()
        child = person(pool, sex_(st), kind="child", mother=mother, father=father)
        pairs.append(("parent-offspring", sp, subject(child, st, ["relative", "child"])))
    for _ in range(4):                                           # full siblings, both parents hidden
        pool = pool_()
        mother, father = person(pool, 2, kind="hidden"), person(pool, 1, kind="hidden")
        sibs = []
        for _ in range(2):
            st = status_()
            sibs.append(subject(person(pool, sex_(st), kind="sibling", mother=mother, father=father), st,
                                ["relative", "sibling"]))
        pairs.append(("full-siblings", sibs[0], sibs[1]))
    for kind in ["first_cousins"] * 3 + ["uncle_niece"] * 2:     # consanguineous: flagged and kept
        pool, st = pool_(), status_()
        g1, g2 = person(pool, 1, kind="hidden"), person(pool, 2, kind="hidden")
        if kind == "first_cousins":
            p1 = person(pool, 1, kind="hidden", mother=g2, father=g1)
            p2 = person(pool, 2, kind="hidden", mother=g2, father=g1)
            wife, husband = person(pool, 2, kind="hidden"), person(pool, 1, kind="hidden")
            father = person(pool, 1, kind="hidden", mother=wife, father=p1)
            mother = person(pool, 2, kind="hidden", mother=p2, father=husband)
        else:
            father = person(pool, 1, kind="hidden", mother=g2, father=g1)            # the uncle
            sister = person(pool, 2, kind="hidden", mother=g2, father=g1)
            husband = person(pool, 1, kind="hidden")
            mother = person(pool, 2, kind="hidden", mother=sister, father=husband)   # the niece
        subject(person(pool, sex_(st), kind="consanguineous", mother=mother, father=father), st,
                ["consanguineous", kind])
    out_pools = [p for p, k in OUTLIERS.items() for _ in range(k)]
    out_status = np.array([2] * 30 + [1] * 10)[rng.permutation(40)]
    for pool, st in zip(out_pools, out_status):
        subject(person(pool, sex_(int(st)), kind="outlier"), int(st), ["outlier", pool])
    duplicate_plan = [("coherent", (2, "S"), 2), ("coherent", (1, "N"), 1), ("discordant", (2, "S"), 1)]
    for _, (_, pool), second_status in duplicate_plan:           # the second ID of each unintended duplicate
        used[(second_status, pool)] += 1
    for (st, pool), quota in QUOTA.items():
        for _ in range(quota - used[(st, pool)]):
            subject(person(pool, sex_(st), kind="plain"), st, [])

    plain = [int(k) for k in rng.permutation([k for k, sub in enumerate(subjects) if not sub.tags])]

    def take(n, tag, ok=lambda sub: True) -> list[int]:
        got = []
        for k in list(plain):
            if len(got) == n:
                break
            if ok(subjects[k]):
                subjects[k].tags.append(tag)
                plain.remove(k)
                got.append(k)
        if len(got) < n:
            raise RuntimeError(f"not enough plain subjects for {tag}")
        return got

    take(3, "failed")
    take(22, "low_call_rate")
    take(4, "sex_declared_female_genetic_male", lambda sub: people[sub.person].sex == 1)
    take(3, "sex_declared_male_genetic_female", lambda sub: people[sub.person].sex == 2)
    for k in take(1, "sex_xxy", lambda sub: people[sub.person].sex == 1):
        people[subjects[k].person].two_x = True
    contaminants = {}
    for k in take(6, "contaminated"):
        pool = people[subjects[k].person].pool
        contaminants[k] = (person(pool, sex_(), kind="hidden"), float(rng.uniform(0.10, 0.25)))
    for kind, (st, pool), second_status in duplicate_plan:
        first = take(1, f"duplicate_{kind}", lambda sub: sub.status == st and people[sub.person].pool == pool)[0]
        subjects.append(Subject(subjects[first].person, second_status, tags=[f"duplicate_{kind}", "second_id"]))
        pairs.append((f"duplicate-{kind}", first, len(subjects) - 1))
    originals = take(N_REPLICATES, "replicate_original")

    for sub in subjects:                                         # declared sex and age
        p = people[sub.person]
        sub.sex = p.sex
        mean, sd = (60, 9) if sub.status == 2 else (57, 10)
        sub.age = int(np.clip(round(rng.normal(mean, sd)), 30, 85))
    for sub in subjects:
        if "sex_declared_female_genetic_male" in sub.tags:
            sub.sex = 2
        if "sex_declared_male_genetic_female" in sub.tags:
            sub.sex = 1
    for kind, a, b in pairs:
        if kind == "parent-offspring":
            subjects[a].age = max(subjects[a].age, 52)
            subjects[b].age = subjects[a].age - int(rng.integers(22, 33))
        elif kind == "full-siblings":
            subjects[b].age = int(np.clip(subjects[a].age + rng.integers(-5, 6), 30, 85))
        elif kind == "duplicate-coherent":
            subjects[b].age = subjects[a].age
        elif kind == "duplicate-discordant":
            subjects[b].age = int(np.clip(subjects[a].age - rng.integers(6, 15), 30, 85))
    if len(subjects) != N_STUDY:
        raise RuntimeError(f"{len(subjects)} subjects instead of {N_STUDY}")

    ids = [f"SIM26_{k:04d}" for k in rng.permutation(N_STUDY) + 1]
    for sub, sid in zip(subjects, ids):
        sub.sample_id = sid
    wells = [dict(subject=k, person=sub.person, sample_id=sub.sample_id, replicate_of="")
             for k, sub in enumerate(subjects)]
    for k in originals:
        wells.append(dict(subject=k, person=subjects[k].person, sample_id=subjects[k].sample_id + "_R2",
                          replicate_of=subjects[k].sample_id))
    special = np.array([bool(subjects[w["subject"]].tags) for w in wells])
    replicate_of = np.array([w["subject"] if w["replicate_of"] else -1 for w in wells])
    plate, position = core.assign_plates(len(wells), special, replicate_of, rng, bad_plate=BAD_PLATE)
    for w, pl, po in zip(wells, plate, position):
        w["plate"], w["position"] = int(pl), int(po)
    on_bad = [w["subject"] for w in wells if w["plate"] == BAD_PLATE]
    for n, k in enumerate(int(x) for x in rng.permutation(on_bad)):
        subjects[k].tags += ["plate14", "plate14_low"] if n < 20 else ["plate14"]
    wells.sort(key=lambda w: (w["plate"], w["position"]))
    grch37 = [person("N" if k % 2 == 0 else "S", sex_(), kind="grch37") for k in range(n_grch37)]
    return Roster(people, subjects, wells, pairs, contaminants, grch37)


def expected_flow(roster: Roster) -> dict:
    """Samples each QC step should remove, from the planted problems (the reference run checks the real counts)."""
    steps = {"3.1": ["failed"], "3.2": ["low_call_rate", "plate14_low"],
             "3.3": ["sex_declared_female_genetic_male", "sex_declared_male_genetic_female", "sex_xxy"],
             "3.5": ["contaminated", "ADM"], "3.7": ["plate14"], "5.6": ["outlier"]}
    # the 7 admixed AFR-EUR outliers leave at 3.5: excess heterozygosity from mixed ancestry (author, 2026-11-11)
    removed: dict[str, list[str]] = {}
    gone: set[str] = set()
    for step in ("3.1", "3.2", "3.3", "3.5"):
        ids = [s.sample_id for s in roster.subjects if any(t in s.tags for t in steps[step])]
        removed[step] = sorted(set(ids) - gone)
        gone |= set(ids)
    ids = [w["sample_id"] for w in roster.wells if w["replicate_of"]]
    for kind, a, b in roster.pairs:
        sa, sb = roster.subjects[a], roster.subjects[b]
        ids += [sa.sample_id, sb.sample_id] if kind == "duplicate-discordant" else [sb.sample_id]
    removed["3.6"] = sorted(set(ids) - gone)
    gone |= set(ids)
    for step in ("3.7", "5.6"):
        ids = [s.sample_id for s in roster.subjects if any(t in s.tags for t in steps[step])]
        removed[step] = sorted(set(ids) - gone)
        gone |= set(ids)
    counts, n = {}, len(roster.wells)
    for step, ids in removed.items():
        n -= len(ids)
        counts[step] = {"removed": len(ids), "remaining": n}
    return {"removed": removed, "counts": counts, "start": len(roster.wells), "final": n}


# --- inputs ---------------------------------------------------------------------------------------------------

class Build:
    def __init__(self, s: Settings):
        self.s = s
        self.out, self.work = Path(s.out), Path(s.out) / "work"
        self.student, self.instructor = self.out / "student", self.out / "instructor"
        for d in [self.work, self.instructor] + [self.student / name for name in STUDENT_DIRS]:
            d.mkdir(parents=True, exist_ok=True)
        self.commands: list[dict] = []
        self.timings: dict[str, float] = {}
        self.notes: dict = {}
        self._t = time.perf_counter()

    def rng(self, stream: int) -> np.random.Generator:
        return np.random.default_rng([self.s.seed, stream])

    def lap(self, name: str) -> None:
        now = time.perf_counter()
        self.timings[name] = round(now - self._t, 1)
        self._t = now
        print(f"[{name}] {self.timings[name]} s", flush=True)

    def plink(self, args: list[str]) -> None:
        cmd = [str(self.s.plink)] + [str(a) for a in args] + ["--threads", str(self.s.threads),
                                                                "--memory", str(self.s.memory_mb)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        self.commands.append({"args": [str(a) for a in args], "returncode": r.returncode})
        if r.returncode:
            raise RuntimeError("PLINK 2 failed:\n" + " ".join(cmd) + "\n" + r.stdout[-3000:] + r.stderr[-2000:])

    @property
    def full_callset(self) -> list[str]:
        kg = self.s.kg_dir
        return ["--pgen", kg / "all_hg38.pgen", "--pvar", kg / "all_hg38_rs_noannot.pvar.zst",
                "--psam", kg / "hg38_corrected.psam"]


def choose_donors(b: Build) -> dict:
    """Donor pools and the PCA reference. Related samples (both published lists) are removed; every population
    is split at random into template donors and reference samples; one of each donor pair with KING kinship
    above the third-degree bound is dropped."""
    kg = b.s.kg_dir
    rows = [line.rstrip("\n").split("\t") for line in open(kg / "hg38_corrected.psam", encoding="utf-8")]
    head = [h.lstrip("#") for h in rows[0]]
    iid, sexc, sp, pop = (head.index(c) for c in ("IID", "SEX", "SuperPop", "Population"))
    related = set()
    for name in ("deg2_hg38.king.cutoff.out.id", "deg2_hg38_set2.king.cutoff.out.id"):
        related |= {line.split()[-1] for line in open(kg / name, encoding="utf-8")
                    if line.strip() and not line.startswith("#")}
    by_pop = collections.defaultdict(list)
    info = {}
    for r in rows[1:]:
        info[r[iid]] = (r[sp], r[pop], int(r[sexc]) if r[sexc] in ("1", "2") else 0)
        if r[iid] not in related:
            by_pop[r[pop]].append(r[iid])
    pool_of = {"CEU": "N", "GBR": "N", "TSI": "S", "IBS": "S"}
    others = sorted({p for i, (s_, p, _) in info.items() if s_ in ("AFR", "SAS", "EAS")})
    for p in others:
        pool_of[p] = info[by_pop[p][0]][0]
    rng = random.Random(b.s.seed)
    pools, reference, split = collections.defaultdict(list), [], {}
    for p in ["CEU", "GBR", "TSI", "IBS"] + others:              # this order reproduces the trial split
        ids = sorted(by_pop[p])
        rng.shuffle(ids)
        h = round(len(ids) * b.s.template_share)
        pools[pool_of[p]] += sorted(ids[:h])
        reference += sorted(ids[h:])
        split[p] = {"pool": pool_of[p], "template": h, "reference": len(ids) - h}
    keep = b.work / "donors_all.keep"
    keep.write_text("\n".join(sorted(sum(pools.values(), []))) + "\n", encoding="ascii")
    b.plink(["--pfile", b.s.design_dir / "kg30x_design", "--keep", keep, "--chr", "1-22", "--make-king-table",
             "--king-table-filter", str(core.THIRD_DEGREE), "--out", b.work / "donor_king"])
    lines = [line.split("\t") for line in open(b.work / "donor_king.kin0", encoding="utf-8")]
    cols = [c.lstrip("#").strip() for c in lines[0]]
    pairs = sorted(((float(r[cols.index("KINSHIP")]), r[cols.index("IID1")], r[cols.index("IID2")])
                    for r in lines[1:]), reverse=True)
    dropped = []
    for kin, a, c in pairs:
        if a not in dropped and c not in dropped:
            dropped.append(max(a, c))
    pools = {name: [i for i in ids if i not in dropped] for name, ids in pools.items()}
    keep.write_text("\n".join(sorted(sum(pools.values(), []))) + "\n", encoding="ascii")
    return {"pools": pools, "reference": sorted(reference), "info": info, "split": split,
            "related_removed": len(related),
            "donor_pairs_above_third_degree": [{"kinship": k, "iid_1": a, "iid_2": c} for k, a, c in pairs],
            "donors_dropped": dropped}


def choose_sites(b: Build, donors: dict) -> dict:
    """The array: the local GSA-like site list, with the palindromic variants thinned to the planned number,
    without the chrY sites with missing calls in the male donors and the MT sites with missing calls in any donor
    (design_sites.tsv itself is left as it is), plus simulated pseudo-autosomal sites (the callset has none)."""
    rng = b.rng(1)
    rows = [line.rstrip("\n").split("\t") for line in open(b.s.design_dir / "design_sites.tsv", encoding="utf-8")][1:]
    if b.s.only_chromosomes:
        rows = [r for r in rows if r[1] in b.s.only_chromosomes]
    pal = [k for k, r in enumerate(rows) if core.is_palindromic(r[4], r[5]) and r[3] not in FORCED_MARKERS]
    share = min(1.0, PLANTED["palindromic"] / 3757) if b.s.only_chromosomes else None
    n_keep = int(round(len(pal) * share)) if share else PLANTED["palindromic"]
    drop = set(int(x) for x in rng.choice(pal, size=max(0, len(pal) - n_keep), replace=False))
    rows = [r for k, r in enumerate(rows) if k not in drop]
    gaps = haploid_gaps(b, donors)
    dropped_gaps = [r for r in rows if r[0] in gaps]
    rows = [r for r in rows if r[0] not in gaps]
    excluded = {c: sum(1 for r in dropped_gaps if r[1] == c) for c in ("Y", "MT")}
    if any(r[1] not in ("Y", "MT") for r in dropped_gaps):
        raise RuntimeError("the chrY/MT exclusion touched another chromosome")
    rows.sort(key=lambda r: (CHROM_ORDER[r[1]], int(r[2])))
    names = [r[3] for r in rows]
    if len(set(names)) != len(names) or any(" " in n or ";" in n or "\t" in n for n in names):
        raise RuntimeError("array names must be unique and free of spaces and semicolons")
    par = []
    if not b.s.only_chromosomes or "X" in b.s.only_chromosomes:
        seen, taken_names = set(), set(names)
        for line in list(open(b.s.design_dir / "manifest_sites.tsv", encoding="utf-8"))[1:]:
            chrom, pos, name, a, c, _, _, cls = line.rstrip("\n").split("\t")
            pos = int(pos)
            in_par = pos <= core.PAR1_END_B38 or pos >= core.PAR2_START_B38
            if cls == "XY" and in_par and pos not in seen and name not in taken_names and not core.is_palindromic(a, c):
                seen.add(pos)
                par.append((pos, name, a, c))
        par = sorted(par[int(k)] for k in rng.choice(len(par), size=min(len(par), PLANTED["par_sites"]), replace=False))
    return {"kg_id": [r[0] for r in rows], "chrom": [r[1] for r in rows], "pos": np.array([int(r[2]) for r in rows]),
            "name": names, "ref": [r[4] for r in rows], "alt": [r[5] for r in rows], "par": par,
            "palindromic_dropped": len(drop), "haploid_sites_excluded": excluded}


Y_INCOMPLETE_DONOR = 0.05          # a male donor missing more than 5% of the chrY sites is not a chrY source


def read_plink_table(path: Path) -> tuple[list[str], list[list[str]]]:
    rows = [line.rstrip("\n").split("\t") for line in open(path, encoding="ascii")]
    return [h.lstrip("#") for h in rows[0]], rows[1:]


def haploid_gaps(b: Build, donors: dict) -> dict[str, str]:
    """IDs of the chrY sites with a missing call in any male donor and of the MT sites with a missing call in any
    donor (all donor pools). Male donors whose chrY is mostly missing (above Y_INCOMPLETE_DONOR) are left out of
    the chrY count and never used as a chrY source: they are listed in donors["y_incomplete"]."""
    everyone = sorted(sum(donors["pools"].values(), []))
    men = [i for i in everyone if donors["info"][i][2] == 1]
    donors["y_incomplete"] = []
    if not b.s.only_chromosomes or "Y" in b.s.only_chromosomes:
        keep = b.work / "donors_Y_all.keep"
        keep.write_text("".join(i + "\n" for i in men), encoding="ascii")
        b.plink(["--pfile", b.s.design_dir / "kg30x_design", "--keep", keep, "--chr", "Y", "--missing",
                 "sample-only", "--out", b.work / "gaps_Y_samples"])
        head, rows = read_plink_table(b.work / "gaps_Y_samples.smiss")
        donors["y_incomplete"] = sorted(r[head.index("IID")] for r in rows
                                        if float(r[head.index("F_MISS")]) > Y_INCOMPLETE_DONOR)
        donors["y_incomplete_missing"] = {r[head.index("IID")]: round(float(r[head.index("F_MISS")]), 4)
                                          for r in rows if r[head.index("IID")] in donors["y_incomplete"]}
        men = [i for i in men if i not in donors["y_incomplete"]]
    gaps = {}
    for chrom, ids in (("Y", men), ("MT", everyone)):
        if b.s.only_chromosomes and chrom not in b.s.only_chromosomes:
            continue
        keep = b.work / f"donors_{chrom}.keep"
        keep.write_text("".join(i + "\n" for i in ids), encoding="ascii")
        b.plink(["--pfile", b.s.design_dir / "kg30x_design", "--keep", keep, "--chr", chrom, "--missing",
                 "variant-only", "--out", b.work / f"gaps_{chrom}"])
        head, rows = read_plink_table(b.work / f"gaps_{chrom}.vmiss")
        for r in rows:
            if int(r[head.index("MISSING_CT")]) > 0:
                gaps[r[head.index("ID")]] = chrom
    return gaps


def known_snps(b: Build, chain: core.Chain, sites: dict) -> dict:
    """Well-known SNPs for the build exercise: GRCh38 position from the array list, GRCh37 position from the
    table above, kept only when the chain file lifts one onto the other."""
    wanted: dict = {}
    by_name: dict[str, tuple[str, int]] = {}
    alleles: dict[str, set[str]] = {}                            # plus-strand alleles from the manifest
    for line in list(open(b.s.design_dir / "manifest_sites.tsv", encoding="utf-8"))[1:]:
        f = line.rstrip("\n").split("\t")
        if f[2] in KNOWN_SNPS:
            by_name[f[2]] = (f[0], int(f[1]))
            alleles[f[2]] = {f[3], f[4]}
    # callset variants at the manifest positions (PLINK 2 output of the design step, IDs chrom:pos:ref:alt)
    matched: dict[tuple[str, int], list] = {}
    for line in open(b.s.design_dir / "kg30x_manifestpos.pvar", encoding="utf-8"):
        if line.startswith("#"):
            continue
        c, p, vid, ref, alt = line.rstrip("\n").split("\t")[:5]
        matched.setdefault((c, int(p)), []).append((vid, {ref, alt}))
    for rs, (chrom, pos37) in KNOWN_SNPS.items():
        if rs not in by_name or by_name[rs][0] != chrom:
            continue
        hits = [vid for vid, pair in matched.get(by_name[rs], []) if pair == alleles[rs]]
        if not hits:
            continue
        if b.s.only_chromosomes and chrom not in b.s.only_chromosomes:
            continue
        contig, lifted = chain.lift(f"chr{chrom}", np.array([pos37]))
        if contig[0] == f"chr{chrom}" and int(lifted[0]) == by_name[rs][1]:
            wanted[rs] = {"chrom": chrom, "pos38": by_name[rs][1], "pos37": pos37, "kg_id": hits[0]}
    return wanted


def search_loci(b: Build, donors: dict, sites: dict) -> dict:
    """One causal variant per planned chromosome, from the dense callset on the North and South templates."""
    templates = donors["pools"]["N"] + donors["pools"]["S"]
    keep = b.work / "templates.keep"
    keep.write_text("\n".join(templates) + "\n", encoding="ascii")
    array_ids = set(sites["kg_id"])
    usable = {i for i, r, a in zip(sites["kg_id"], sites["ref"], sites["alt"]) if not core.is_palindromic(r, a)}
    found = {}
    for name, spec in LOCI.items():
        chrom = spec["chrom"]
        if b.s.only_chromosomes and chrom not in b.s.only_chromosomes:
            continue
        prefix = b.work / f"dense_chr{chrom}"
        b.plink(b.full_callset + ["--keep", keep, "--chr", chrom, "--snps-only", "just-acgt", "--max-alleles", "2",
                                  "--maf", "0.01", "--set-all-var-ids", "@:#:$r:$a", "--export", "haps",
                                  "--out", prefix])
        rows, samples, haps = core.read_haps(str(prefix))
        (prefix.with_suffix(".haps")).unlink()
        pos = np.array([r[2] for r in rows])
        ids = [r[1] for r in rows]
        on_array = np.array([i in usable for i in ids])
        in_array = np.array([i in array_ids for i in ids])
        pal = np.array([core.is_palindromic(r[3], r[4]) for r in rows])
        allowed = ~pal & (pos > pos[0] + 2_000_000) & (pos < pos[-1] - 2_000_000)
        order = {sid: k for k, sid in enumerate(samples)}
        north = np.array([2 * order[i] + h for i in donors["pools"]["N"] for h in (0, 1)])
        south = np.array([2 * order[i] + h for i in donors["pools"]["S"] for h in (0, 1)])
        hit = core.find_locus(haps, pos, on_array, allowed, north, south, spec["freq"], spec["on_array"],
                              candidate=on_array if spec["on_array"] else ~in_array)
        if hit is None:
            raise RuntimeError(f"no causal variant found for {name} on chromosome {chrom}")
        j = hit["col"]
        ref, alt = ids[j].split(":")[2:4]
        risk_allele = rows[j][4] if hit["risk"] == 1 else rows[j][3]
        found[name] = {**spec, "kg_id": ids[j], "pos": int(pos[j]), "risk_allele": risk_allele,
                       "risk_is_alt": risk_allele == alt, "ref": ref, "alt": alt,
                       "risk_freq_templates": round(hit["risk_freq"], 4), "freq_north": round(hit["freq_north"], 4),
                       "freq_south": round(hit["freq_south"], 4), "array_neighbours_r2_0_5": hit["array_neighbours"],
                       "array_neighbours_r2_0_2": hit["array_neighbours_r2_0_2"],
                       "dense_neighbours_r2_0_5": hit["dense_neighbours"]}
        if hit["tag"]:
            found[name]["tag"] = {"kg_id": ids[hit["tag"][0]], "pos": int(pos[hit["tag"][0]]),
                                  "r2": round(hit["tag"][1], 3)}
        del haps
        b.lap(f"locus {name}")
    return found


def extract_donors(b: Build, sites: dict, hidden_points: list[tuple[str, int]],
                   regions: list[tuple[str, int, int]]) -> None:
    """One PLINK 2 fileset with the donors at the array positions, the hidden points and the dense regions."""
    ranges = sorted({(c, int(p), int(p)) for c, p in zip(sites["chrom"], sites["pos"])}
                    | {(c, p, p) for c, p in hidden_points} | set(regions), key=lambda r: (CHROM_ORDER[r[0]], r[1]))
    bed = b.work / "donor_ranges.bed1"
    bed.write_text("".join(f"{c}\t{lo}\t{hi}\n" for c, lo, hi in ranges), encoding="ascii")
    b.plink(b.full_callset + ["--keep", b.work / "donors_all.keep", "--extract", "bed1", bed, "--snps-only",
                              "just-acgt", "--max-alleles", "2", "--set-all-var-ids", "@:#:$r:$a",
                              "--make-pgen", "--out", b.work / "donors"])


# --- genomes ---------------------------------------------------------------------------------------------------

def read_map(map_dir: Path, name: str) -> tuple[np.ndarray, np.ndarray]:
    rows = [line.split() for line in open(map_dir / f"genetic_map_GRCh38_chr{name}.txt", encoding="ascii")][1:]
    return np.array([int(r[1]) for r in rows]), np.array([float(r[3]) for r in rows])


def read_traw(prefix: Path) -> tuple[list[str], list[str], np.ndarray]:
    """A PLINK 2 `--export A-transpose` file as ALT counts [variant, sample] (-1 missing)."""
    lines = [line.rstrip("\n").split("\t") for line in open(f"{prefix}.traw", encoding="utf-8")]
    samples = [h.split("_", 1)[1] for h in lines[0][6:]]
    ids = [r[1] for r in lines[1:]]
    g = np.array([[-1 if x == "NA" else int(float(x)) for x in r[6:]] for r in lines[1:]], dtype=np.int8)
    counted_is_ref = np.array([r[4] == r[1].split(":")[2] for r in lines[1:]])
    alt = np.where(g < 0, -1, np.where(counted_is_ref[:, None], 2 - g, g)).astype(np.int8)
    return ids, samples, alt.reshape(len(ids), len(samples))


def simulate_genomes(b: Build, donors: dict, sites: dict, roster: Roster, loci: dict, hidden_ids: set[str],
                     regions: dict[str, tuple[str, int, int]]) -> dict:
    """Genotypes of every well at the array sites [variant, well], plus what later steps need from the hidden
    sites: the haplotypes in the imputation regions, the genotypes of the people of the GRCh37 exercise, and a
    thinned set of genotypes for the copy check."""
    s, people = b.s, roster.people
    well_person = np.array([w["person"] for w in roster.wells])
    study_people = np.array(sorted({w["person"] for w in roster.wells}))
    g37_people = np.array(roster.grch37_people)
    contaminated = {k: (q, a) for k, (q, a) in roster.contaminants.items()}
    well_of_subject = {w["subject"]: n for n, w in enumerate(roster.wells) if not w["replicate_of"]}
    info = donors["info"]
    array_index = {i: k for k, i in enumerate(sites["kg_id"])}
    m = len(sites["kg_id"])
    w_all = np.full((m, len(roster.wells)), -1, dtype=np.int8)
    freq_n, freq_s = np.zeros(m), np.zeros(m)
    out = {"regions": {}, "g37": {"ids": [], "g": []}, "king_people": [], "king_donors": collections.defaultdict(list),
           "longest_cm": np.zeros(len(people)), "loci": {}}
    chroms = [c for c in AUTOSOMES if c in set(sites["chrom"])]
    for chrom in chroms + (["X"] if "X" in set(sites["chrom"]) else []):
        prefix = b.work / f"donors_chr{chrom}"
        b.plink(["--pfile", b.work / "donors", "--chr", chrom, "--export", "haps", "--out", prefix])
        rows, samples, haps = core.read_haps(str(prefix))
        prefix.with_suffix(".haps").unlink()
        pos_all = np.array([r[2] for r in rows])
        maf_t = None
        order = {sid: k for k, sid in enumerate(samples)}
        hap_rows = {pool: np.array([2 * order[i] + h for i in ids for h in (0, 1)])
                    for pool, ids in donors["pools"].items()}
        templates = np.concatenate([hap_rows["N"], hap_rows["S"]])
        if chrom != "X":
            f_t = haps[templates].mean(axis=0)
            maf_t = np.minimum(f_t, 1 - f_t)
        in_region = {name: (pos_all >= lo) & (pos_all <= hi) for name, (c, lo, hi) in regions.items() if c == chrom}
        keep = np.array([r[1] in array_index or r[1] in hidden_ids
                         or any(mask[k] and maf_t[k] >= 0.01 for mask in in_region.values())
                         for k, r in enumerate(rows)])
        rows = [r for r, ok in zip(rows, keep) if ok]
        haps = haps[:, keep]
        in_region = {name: mask[keep] for name, mask in in_region.items()}   # same columns as `haps` now
        ids = [r[1] for r in rows]
        pos = np.array([r[2] for r in rows])
        alt_is_one = np.array([r[4] == r[1].split(":")[3] for r in rows])
        haps = np.where((haps == core.NO_HAP) | alt_is_one[None, :], haps, 1 - haps).astype(np.uint8)
        is_array = np.array([i in array_index for i in ids])
        array_rows = np.array([array_index[i] for i in ids if i in array_index])
        expected = sum(1 for c in sites["chrom"] if c == chrom)
        if len(array_rows) != expected:
            raise RuntimeError(f"chr{chrom}: {len(array_rows)} of {expected} array sites found in the donor fileset")
        map_pos, map_cm = read_map(s.map_dir, chrom)
        cm = core.interpolate_cm(pos, map_pos, map_cm)
        rng = b.rng(100 + CHROM_ORDER[chrom])
        if chrom == "X":
            pools = {pool: haps[r][(haps[r] != core.NO_HAP).all(axis=1)] for pool, r in hap_rows.items()}
            pools["EUR"] = np.concatenate([pools["N"], pools["S"]])
            freq_n[array_rows] = pools["N"][:, is_array].mean(axis=0)
            freq_s[array_rows] = pools["S"][:, is_array].mean(axis=0)
            h1, h2, one = core.simulate_x(people, pools, cm, rng, s.mean_segment_cm, s.max_copy_cm)
            w = core.well_genotypes(h1[:, is_array], h2[:, is_array], well_person, s.allele_error_rate, rng, one)
        else:
            pools = {pool: haps[r] for pool, r in hap_rows.items()}
            pools["EUR"] = haps[templates]
            freq_n[array_rows] = pools["N"][:, is_array].mean(axis=0)
            freq_s[array_rows] = pools["S"][:, is_array].mean(axis=0)
            locus = None
            for name, spec in loci.items():
                if spec["chrom"] == chrom:
                    col = ids.index(spec["kg_id"])
                    locus = {"col": col, "risk": 1 if spec["risk_is_alt"] else 0, "or": spec["odds_ratio"]}
                    locus_name = name
            # labels of the donor haplotypes: N, S, AFR, SAS, EAS one after the other (EUR = N then S)
            offsets, start = {}, 0
            for pool in LABEL_POOLS:
                offsets[pool], start = start, start + len(hap_rows[pool])
            offsets["EUR"] = offsets["N"]
            track = {"offset": offsets}
            h1, h2, longest = core.simulate_autosome(people, pools, cm, rng, s.mean_segment_cm, s.max_copy_cm, locus,
                                                     track)
            weights = core.column_weights(cm)
            for which in ("l1", "l2"):
                got = core.copied_cm(track[which], weights, start)
                out["copied_" + which] = got if "copied_" + which not in out else out["copied_" + which] + got
            out["total_cm"] = out.get("total_cm", 0.0) + float(weights.sum())
            out["label_offsets"] = {p: (offsets[p], len(hap_rows[p])) for p in LABEL_POOLS}
            del track
            out["longest_cm"] = np.maximum(out["longest_cm"], longest)
            if locus is not None:
                carried = (h1[:, locus["col"]] == locus["risk"]).astype(int) + (h2[:, locus["col"]] == locus["risk"])
                out["loci"][locus_name] = carried
            w = core.well_genotypes(h1[:, is_array], h2[:, is_array], well_person, s.allele_error_rate, rng)
            for k, (q, alpha) in contaminated.items():
                other = (h1[q, is_array] + h2[q, is_array]).astype(np.int8)
                col = well_of_subject[k]
                w[:, col] = core.contaminate(w[:, col], other, alpha, rng)
            # copy check: every autosomal array site with template MAF >= 0.01
            thin = np.flatnonzero(is_array & (maf_t[keep] >= 0.01))
            out["king_people"].append((h1[:, thin] + h2[:, thin]).astype(np.int8))
            for pool, r in hap_rows.items():
                out["king_donors"][pool].append((haps[r][0::2, thin] + haps[r][1::2, thin]).astype(np.int8))
            out["g37"]["ids"] += ids
            out["g37"]["g"].append((h1[g37_people] + h2[g37_people]).astype(np.int8).T)
            for name, mask in in_region.items():
                cols = np.flatnonzero(mask)
                out["regions"][name] = {"ids": [ids[k] for k in cols], "pos": pos[cols], "is_array": is_array[cols],
                                        "h1": h1[np.ix_(study_people, cols)], "h2": h2[np.ix_(study_people, cols)],
                                        "people": study_people}
        w_all[array_rows] = w
        del haps, h1, h2, w
        b.lap(f"genomes chr{chrom}")
    out["freq_n"], out["freq_s"] = freq_n, freq_s
    out["g37"]["g"] = np.concatenate(out["g37"]["g"], axis=0) if out["g37"]["g"] else np.zeros((0, len(g37_people)), np.int8)

    # chrY and MT: copied whole from one donor (a son from his father, everybody from the mother)
    rng = b.rng(130)
    male_person = np.array([p.sex == 1 for p in people])
    for chrom in ("Y", "MT"):
        rows_here = np.array([k for k, c in enumerate(sites["chrom"]) if c == chrom], dtype=int)
        if len(rows_here) == 0:
            continue
        prefix = b.work / f"donors_chr{chrom}"
        b.plink(["--pfile", b.work / "donors", "--chr", chrom, "--export", "A-transpose", "--out", prefix])
        ids, samples, alt = read_traw(prefix)
        order = {i: k for k, i in enumerate(ids)}
        alt = alt[[order[i] for i in (sites["kg_id"][k] for k in rows_here)]]
        alt[alt == 1] = 2                                          # a haploid call is never heterozygous
        column = {sid: k for k, sid in enumerate(samples)}
        source = np.full(len(people), -1)
        for k, p in enumerate(people):
            if chrom == "Y" and p.sex != 1:
                continue
            if p.founder:
                pool = "AFR" if p.pool == "ADM" else p.pool
                ok = [i for i in donors["pools"][pool]
                      if chrom == "MT" or (info[i][2] == 1 and i not in donors.get("y_incomplete", []))]
                source[k] = column[ok[int(rng.integers(len(ok)))]]
            else:
                source[k] = source[p.father if chrom == "Y" else p.mother]
        block = np.full((len(rows_here), len(roster.wells)), -1, dtype=np.int8)
        has = source[well_person] >= 0
        block[:, has] = alt[:, source[well_person][has]]
        w_all[rows_here] = block
    out["w"], out["male_person"] = w_all, male_person
    return out


# --- planting ---------------------------------------------------------------------------------------------------

def plant_problems(b: Build, sites: dict, roster: Roster, sim: dict, loci: dict, regions: dict) -> dict:
    """Plant the variant and sample problems into the genotype matrix (in place) and add the simulated
    pseudo-autosomal rows and the duplicated variants. Returns the final variant table and the answer key part."""
    rng = b.rng(3)
    people, subjects, wells = roster.people, roster.subjects, roster.wells
    w = sim["w"]
    n_wells = w.shape[1]
    chrom, pos = np.array(sites["chrom"]), sites["pos"]
    ref, alt, names = list(sites["ref"]), list(sites["alt"]), list(sites["name"])
    well_subject = np.array([x["subject"] for x in wells])
    well_tags = [set(subjects[k].tags) for k in well_subject]
    case_well = np.array([subjects[k].status == 2 for k in well_subject])
    male_well = np.array([people[x["person"]].sex == 1 for x in wells])
    two_x_well = np.array([people[x["person"]].two_x for x in wells])
    key: dict = {}

    # pseudo-autosomal sites: diploid in both sexes, no LD, frequencies from the autosomal spectrum
    auto = np.array([c in CHROM_ORDER and CHROM_ORDER[c] < 22 for c in chrom])
    spectrum = ((sim["freq_n"] + sim["freq_s"]) / 2)[auto]
    spectrum = spectrum[(spectrum > 0.01) & (spectrum < 0.99)]
    par = sites["par"]
    if par:
        par_freq = rng.choice(spectrum, size=len(par))
        person_g = (rng.random((len(par), len(people))) < par_freq[:, None]).astype(np.int8) \
            + (rng.random((len(par), len(people))) < par_freq[:, None])
        par_w = person_g[:, [x["person"] for x in wells]].astype(np.int8)
        w = np.concatenate([w, par_w], axis=0)
        chrom = np.concatenate([chrom, np.array(["X"] * len(par))])
        pos = np.concatenate([pos, np.array([p[0] for p in par])])
        names += [p[1] for p in par]
        ref += [p[2] for p in par]
        alt += [p[3] for p in par]
    is_par = np.zeros(len(names), dtype=bool)
    is_par[len(sites["name"]):] = True
    m = len(names)
    f_template = np.zeros(m)
    f_template[:len(sites["name"])] = (sim["freq_n"] + sim["freq_s"]) / 2
    maf = np.minimum(f_template, 1 - f_template)
    auto = np.array([CHROM_ORDER[c] < 22 for c in chrom]) & ~is_par
    pal = np.array([core.is_palindromic(r, a) for r, a in zip(ref, alt)])

    # variants that must stay clean: the loci, the stratification markers and the imputation regions
    protected = np.zeros(m, dtype=bool)
    zones = list(PROTECTED) + [(v["chrom"], v["pos"] - 1_000_000, v["pos"] + 1_000_000) for v in loci.values()]
    zones += [(c, lo - 250_000, hi + 250_000) for c, lo, hi in regions.values()]
    for c, lo, hi in zones:
        protected |= (chrom == c) & (pos >= lo) & (pos <= hi)
    free = auto & ~pal & ~protected
    taken = np.zeros(m, dtype=bool)

    def pick(n, mask, label):
        pool = np.flatnonzero(mask & ~taken)
        if len(pool) < n:
            if b.s.only_chromosomes:
                n = len(pool)
            else:
                raise RuntimeError(f"not enough variants for {label}: {len(pool)} of {n}")
        chosen = np.sort(rng.choice(pool, size=n, replace=False))
        taken[chosen] = True
        return chosen

    scale = (auto.sum() / 284_580) if b.s.only_chromosomes else 1.0     # a partial build plants fewer
    n_ = lambda name: max(2, int(round(PLANTED[name] * scale)))          # noqa: E731
    v_flip = pick(n_("strand_flip"), free, "strand errors")
    v_mismatch = pick(n_("allele_mismatch"), free, "allele mismatches")
    v_failed = pick(n_("failed_variants"), free, "failed variants")
    v_low = pick(n_("low_call_variants"), free, "low call rate variants")
    v_diff = pick(n_("differential_missingness"), free & (maf > 0.05), "differential missingness")
    v_hwe_strong = pick(n_("hwe_strong"), free & (maf > 0.12), "HWE errors")
    v_hwe_mild = pick(n_("hwe_mild"), free & (maf > 0.12), "mild HWE errors")
    v_dup = pick(n_("duplicate_pairs"), free & (maf > 0.05), "duplicated variants")
    v_pal_flip = pick(n_("palindromic_flipped"), auto & pal & ~protected & (maf > 0.10) & (maf < 0.40),
                      "flipped palindromic variants")
    x_non_par = (chrom == "X") & ~is_par & ~pal
    called = np.where(w >= 0, w, 0).sum(axis=1) / np.maximum(1, 2 * (w >= 0).sum(axis=1))
    common = np.minimum(called, 1 - called) >= 0.05          # observed frequency, so chrY and MT count too
    x_non_par &= common
    v_x = pick(PLANTED["x_male_het"], x_non_par, "chrX variants") if x_non_par.any() else np.array([], dtype=int)
    v_y = pick(PLANTED["y_female_call"], (chrom == "Y") & ~pal & common, "chrY variants") if (chrom == "Y").any() else np.array([], dtype=int)
    v_mt = pick(PLANTED["mt_het"], (chrom == "MT") & ~pal & common, "MT variants") if (chrom == "MT").any() else np.array([], dtype=int)

    # genotype errors first, missing calls after
    bad_wells = np.flatnonzero([x["plate"] == BAD_PLATE for x in wells])
    rows_gt = np.flatnonzero(auto | ((chrom == "X") & ~is_par))
    block = w[np.ix_(rows_gt, bad_wells)]
    lost = core.plant_het_loss(block, np.arange(len(bad_wells)), rng, b.s.plate_het_loss)
    w[np.ix_(rows_gt, bad_wells)] = block
    everyone = np.ones(n_wells, dtype=bool)
    for v in v_hwe_strong:
        core.plant_hwe_failure(w, v, everyone, rng, 0.25)
    for v in v_hwe_mild:
        core.plant_hwe_failure(w, v, everyone, rng, 0.10)
    x_key = []
    for v in v_x:                                                 # heterozygous calls in men
        men = np.flatnonzero(male_well & ~two_x_well & (w[v] >= 0))
        hit = men[rng.random(len(men)) < rng.uniform(0.10, 0.40)]
        w[v, hit] = 1
        x_key.append({"name": names[v], "men_heterozygous": int(len(hit))})
    y_key = []
    for v in v_y:                                                 # calls in women
        women = np.flatnonzero(~male_well)
        hit = women[rng.random(len(women)) < rng.uniform(0.20, 0.60)]
        w[v, hit] = np.where(rng.random(len(hit)) < 0.7, 0, 2)
        y_key.append({"name": names[v], "women_called": int(len(hit))})
    mt_key = []
    for v in v_mt:                                                # heteroplasmy read as heterozygous
        called = np.flatnonzero(w[v] >= 0)
        hit = called[rng.random(len(called)) < rng.uniform(0.05, 0.20)]
        w[v, hit] = 1
        mt_key.append({"name": names[v], "heterozygous": int(len(hit))})

    # missing calls: per well first, then per variant
    weights = rng.gamma(2.0, 0.5, size=m)
    weights[v_diff] = 0.0
    rate_class = {"failed": (0.20, 0.30), "low_call_rate": (0.0265, 0.0485), "plate14_low": (0.0215, 0.0240),
                  "plate14": (0.0120, 0.0175)}
    well_rates = {}
    for col in range(n_wells):
        cls = next((c for c in rate_class if c in well_tags[col]), None)
        if cls:
            lo, hi = rate_class[cls]
            well_rates.update(core.plant_sample_missingness(w, [col], rng, lo, hi, weights, exact=True))
        else:
            rate = float(np.clip(0.0004 + rng.gamma(2.0, 0.0006), 0.0004, 0.008))
            well_rates.update(core.plant_sample_missingness(w, [col], rng, rate, rate, weights))
    failed_share = core.plant_variant_missingness(w, list(v_failed), rng, 0.12, 0.70, exact=True)
    low_share = core.plant_variant_missingness(w, list(v_low), rng, 0.032, 0.090, exact=True)
    diff_counts = [core.plant_differential_missingness(w, v, case_well, ~case_well, rng) for v in v_diff]

    # duplicated variants: the same site listed twice; the copy is exact unless the pair is planted as discordant
    discordant = set(int(x) for x in rng.choice(v_dup, size=min(len(v_dup), n_("duplicate_discordant")), replace=False))
    dup_rows, dup_key = [], []
    for n, v in enumerate(v_dup):
        row = w[v].copy()
        changed = 0
        if int(v) in discordant:
            called = np.flatnonzero(row >= 0)
            hit = called[rng.random(len(called)) < rng.uniform(0.05, 0.15)]
            row[hit] = (row[hit] + rng.integers(1, 3, size=len(hit))) % 3
            changed = int(len(hit))
        dup_rows.append(row)
        # a name that already starts with "GSA-" gets the suffix, never a second prefix
        use_suffix = n % 2 == 0 or names[v].startswith("GSA-")
        new_name = f"{names[v]}_ilmndup1" if use_suffix else f"GSA-{names[v]}"
        dup_key.append({"name": names[v], "duplicate": new_name, "genotypes_changed": changed})
    if dup_rows:
        w = np.concatenate([w, np.array(dup_rows, dtype=np.int8)], axis=0)
        chrom = np.concatenate([chrom, chrom[v_dup]])
        pos = np.concatenate([pos, pos[v_dup]])
        names += [d["duplicate"] for d in dup_key]
        ref += [ref[v] for v in v_dup]
        alt += [alt[v] for v in v_dup]
        is_par = np.concatenate([is_par, np.zeros(len(v_dup), dtype=bool)])
    if len(set(names)) != len(names):
        raise RuntimeError("variant names are not unique after adding the duplicates")
    order = np.array(sorted(range(len(names)), key=lambda k: (CHROM_ORDER[chrom[k]], pos[k], k)))
    index_after = np.empty(len(order), dtype=int)
    index_after[order] = np.arange(len(order))

    # what the laboratory export shows: complemented alleles, changed alleles, palindromic variants read backwards
    file_a1, file_a2 = list(alt), list(ref)                       # A1 = ALT (counted), A2 = REF
    for v in v_flip:
        file_a2[v], file_a1[v] = core.complement_alleles(ref[v], alt[v])
    for v in v_mismatch:
        file_a2[v], file_a1[v] = core.incompatible_alleles(ref[v], alt[v])
    inverted = np.zeros(len(names), dtype=bool)
    inverted[v_pal_flip] = True

    name_of = lambda rows: [names[v] for v in rows]              # noqa: E731
    key["variants"] = {
        "strand_flip": name_of(v_flip), "allele_mismatch": name_of(v_mismatch),
        "palindromic": [names[k] for k in range(len(names)) if core.is_palindromic(ref[k], alt[k])],
        "palindromic_flipped": name_of(v_pal_flip),
        "failed_variants": {names[v]: round(1 - sh, 4) for v, sh in failed_share.items()},
        "low_call_variants": {names[v]: round(1 - sh, 4) for v, sh in low_share.items()},
        "differential_missingness": {names[v]: {"cases_missing": c, "controls_missing": k}
                                     for v, (c, k) in zip(v_diff, diff_counts)},
        "hwe_strong": name_of(v_hwe_strong), "hwe_mild": name_of(v_hwe_mild),
        "x_male_het": x_key, "y_female_call": y_key, "mt_het": mt_key, "duplicated": dup_key,
        "pseudo_autosomal": [p[1] for p in par]}
    key["plate14"] = {"heterozygote_loss_probability": b.s.plate_het_loss,
                      "share_of_genotypes_changed": round(lost, 4)}
    key["well_missing_rate"] = {wells[c]["sample_id"]: round(r, 5) for c, r in well_rates.items()
                                if well_tags[c] & set(rate_class)}
    table = {"chrom": chrom[order], "pos": pos[order], "name": [names[k] for k in order],
             "ref": [ref[k] for k in order], "alt": [alt[k] for k in order],
             "file_a1": [file_a1[k] for k in order], "file_a2": [file_a2[k] for k in order],
             "is_par": is_par[order], "inverted": inverted[order], "freq_template": None,
             "source_row": order, "index_after": index_after}
    f_all = np.zeros(len(names))
    f_all[:len(f_template)] = f_template
    if dup_rows:
        f_all[len(f_template):] = f_template[v_dup]
    table["freq_template"] = f_all[order]
    table["protected"] = np.concatenate([protected, protected[v_dup]])[order] if dup_rows else protected[order]
    table["planted"] = np.concatenate([taken, np.ones(len(v_dup), dtype=bool)])[order] if dup_rows else taken[order]
    return {"w": w[order], "table": table, "key": key}


# --- writers ----------------------------------------------------------------------------------------------------

def write_lab_export(b: Build, w: np.ndarray, table: dict, roster: Roster) -> None:
    """The laboratory export: PLINK 1 binary files of every well, a PED/MAP pair for chromosome 22, the sample
    sheet, the phenotype file and the array annotation."""
    d = b.student / "lab_export"
    exported = np.where(table["inverted"][:, None] & (w >= 0), 2 - w, w).astype(np.int8)
    core.write_bed(str(d / "sim2026_lab.bed"), exported)
    with open(d / "sim2026_lab.bim", "w", encoding="ascii", newline="\n") as fh:
        for c, n, p, a1, a2 in zip(table["chrom"], table["name"], table["pos"], table["file_a1"], table["file_a2"]):
            fh.write(f"{c}\t{n}\t0\t{p}\t{a1}\t{a2}\n")
    with open(d / "sim2026_lab.fam", "w", encoding="ascii", newline="\n") as fh:
        for x in roster.wells:
            fh.write(f"{x['sample_id']}\t{x['sample_id']}\t0\t0\t0\t-9\n")
    rows22 = np.flatnonzero(table["chrom"] == "22")
    if len(rows22):
        with open(d / "sim2026_lab_chr22.map", "w", encoding="ascii", newline="\n") as fh:
            for k in rows22:
                fh.write(f"22\t{table['name'][k]}\t0\t{table['pos'][k]}\n")
        letters = [core.genotype_letters(exported[k], table["file_a1"][k], table["file_a2"][k]) for k in rows22]
        with open(d / "sim2026_lab_chr22.ped", "w", encoding="ascii", newline="\n") as fh:
            for col, x in enumerate(roster.wells):
                alleles = "\t".join(f"{letters[r][col][0]} {letters[r][col][1]}" for r in range(len(rows22)))
                fh.write(f"{x['sample_id']}\t{x['sample_id']}\t0\t0\t0\t-9\t{alleles}\n")
    with open(d / "sample_sheet.csv", "w", encoding="ascii", newline="\n") as fh:
        fh.write("Plate,Well,Sample_ID,Replicate_of\n")
        for x in roster.wells:
            fh.write(f"P{x['plate']:02d},{core.well_label(x['position'])},{x['sample_id']},{x['replicate_of']}\n")
    with open(b.student / "phenotypes" / "sim2026_phenotypes.tsv", "w", encoding="ascii", newline="\n") as fh:
        fh.write("Sample_ID\tSex\tAge\tDisease\n")
        for sub in sorted(roster.subjects, key=lambda s_: s_.sample_id):
            fh.write(f"{sub.sample_id}\t{sub.sex}\t{sub.age}\t{sub.status}\n")
    with open(b.student / "array" / "sim2026_array_annotation.tsv", "w", encoding="ascii", newline="\n") as fh:
        fh.write("Name\tChr\tPosition_GRCh38\tRef_Plus\tAlt_Plus\n")
        for c, n, p, r, a, par in zip(table["chrom"], table["name"], table["pos"], table["ref"], table["alt"],
                                      table["is_par"]):
            fh.write(f"{n}\t{'XY' if par else c}\t{p}\t{r}\t{a}\n")


def write_final_reports(b: Build, w: np.ndarray, table: dict, roster: Roster, duplicates: set[str]) -> list[str]:
    """Illumina Final Report text files for three wells, one of them with a low call rate. Rows are sorted by
    SNP Name, as GenomeStudio usually exports them; a planted duplicated variant never comes first."""
    rng = b.rng(4)
    order = sorted(range(len(table["name"])), key=lambda k: (table["name"][k] in duplicates, table["name"][k]))
    first = sorted(range(len(table["name"])), key=lambda k: table["name"][k])
    order = first if table["name"][first[0]] not in duplicates else order
    names = [table["name"][k] for k in order]
    if names[0] in duplicates:
        raise RuntimeError("a planted duplicated variant would open the Final Report")
    ref, alt = [table["ref"][k] for k in order], [table["alt"][k] for k in order]
    w = w[order]
    tags = [set(roster.subjects[x["subject"]].tags) for x in roster.wells]
    low = [k for k, t in enumerate(tags) if "low_call_rate" in t]
    plain = [k for k, t in enumerate(tags) if not t and not roster.wells[k]["replicate_of"]]
    chosen = [plain[0], plain[len(plain) // 2]] + low[:1]
    written = []
    for col in chosen:
        x = roster.wells[col]
        text = core.final_report(x["sample_id"], names, ref, alt, w[:, col],
                                 core.gc_scores(w[:, col], rng), "SimArray-24v1-0_simulated.bpm", 96,
                                 x["position"] + 1)
        name = f"{x['sample_id']}_FinalReport_simulated.txt"
        (b.student / "final_report" / name).write_bytes(text)
        written.append(name)
    return written


def write_pca_reference(b: Build, donors: dict) -> dict:
    """The PCA reference: the reference halves of the four European populations plus AFR, SAS and EAS, at about
    50,000 common, LD-pruned autosomal array sites."""
    keep = b.work / "reference.keep"
    keep.write_text("\n".join(donors["reference"]) + "\n", encoding="ascii")
    design = b.s.design_dir / "kg30x_design"
    chroms = ",".join(c for c in AUTOSOMES if not b.s.only_chromosomes or c in b.s.only_chromosomes)
    b.plink(["--pfile", design, "--keep", keep, "--chr", chroms, "--maf", "0.05", "--geno", "0",
             "--indep-pairwise", "200kb", "0.15", "--out", b.work / "reference_prune"])
    ids = [line.strip() for line in open(b.work / "reference_prune.prune.in", encoding="ascii") if line.strip()]
    target = 50_000 if not b.s.only_chromosomes else len(ids)
    if len(ids) > target:
        chosen = set(int(k) for k in b.rng(5).choice(len(ids), size=target, replace=False))
        ids = [i for k, i in enumerate(ids) if k in chosen]
    (b.work / "reference.extract").write_text("\n".join(ids) + "\n", encoding="ascii")
    b.plink(["--pfile", design, "--keep", keep, "--extract", b.work / "reference.extract", "--make-pgen",
             "--out", b.student / "pca_reference" / "ref1000g_grch38"])
    (b.student / "pca_reference" / "ref1000g_grch38.log").unlink(missing_ok=True)
    return {"samples": len(donors["reference"]), "variants": len(ids)}


def write_grch37_exercise(b: Build, chain: core.Chain, sim: dict, sites: dict, known: dict, table: dict,
                          roster: Roster) -> dict:
    """A small file in GRCh37 coordinates for step 2.6: new European individuals, array variants whose GRCh37
    position lifts back to the GRCh38 one, the well-known SNPs, and positions that do not convert."""
    rng = b.rng(6)
    d = b.student / "grch37_exercise"
    inverse = chain.inverted()
    col_of = {i: k for k, i in enumerate(sim["g37"]["ids"])}
    name_of = dict(zip(sites["kg_id"], sites["name"]))
    planted = {n for n, p in zip(table["name"], table["planted"]) if p}
    rows = []                                                     # (chrom, pos37, name, ref, alt, genotype row)
    for rs, v in known.items():
        if v["kg_id"] in col_of:
            ref, alt = v["kg_id"].split(":")[2:4]
            rows.append((v["chrom"], v["pos37"], rs, ref, alt, sim["g37"]["g"][col_of[v["kg_id"]]]))
    n_fixed = len(rows)
    pool = [i for i in sites["kg_id"] if i in col_of and name_of[i].startswith("rs") and name_of[i] not in planted
            and name_of[i] not in known and not core.is_palindromic(*i.split(":")[2:4])]
    n_target = 10_000 - 30 - len(rows) if not b.s.only_chromosomes else min(500, len(pool))
    for chrom in sorted({i.split(":")[0] for i in pool}, key=lambda c: CHROM_ORDER[c]):
        here = [i for i in pool if i.split(":")[0] == chrom]
        p38 = np.array([int(i.split(":")[1]) for i in here])
        contig, p37 = inverse.lift(f"chr{chrom}", p38)
        back_contig, back = chain.lift(f"chr{chrom}", np.where(p37 > 0, p37, 1))
        ok = (contig == f"chr{chrom}") & (back_contig == f"chr{chrom}") & (back == p38)
        for i, good, p in zip(here, ok, p37):
            if good:
                ref, alt = i.split(":")[2:4]
                rows.append((chrom, int(p), name_of[i], ref, alt, sim["g37"]["g"][col_of[i]]))
    fixed, rest = rows[:n_fixed], rows[n_fixed:]
    chosen = [rest[int(k)] for k in rng.choice(len(rest), size=min(n_target, len(rest)), replace=False)]
    # positions of the GRCh37 genetic map that the chain cannot convert, or that change chromosome
    unconvertible, moved = [], []
    spectrum = table["freq_template"][(table["freq_template"] > 0.05) & (table["freq_template"] < 0.95)]
    pairs = [("A", "G"), ("C", "T"), ("A", "C"), ("G", "T")]
    for chrom in AUTOSOMES:
        if len(unconvertible) >= 24 and len(moved) >= 6:
            break
        path = b.s.map37_dir / f"genetic_map_GRCh37_chr{chrom}.txt"
        p37 = np.array([int(line.split()[1]) for line in list(open(path, encoding="ascii"))[1:]])
        contig, lifted = chain.lift(f"chr{chrom}", p37)
        lost = p37[lifted < 0]
        other = p37[(lifted > 0) & (contig != f"chr{chrom}")]
        for group, source, limit in ((unconvertible, lost, 3), (moved, other, 2)):
            if len(source):
                for p in rng.choice(source, size=min(limit, len(source)), replace=False):
                    f = float(rng.choice(spectrum))
                    g = (rng.random(len(roster.grch37_people)) < f).astype(np.int8) + (rng.random(len(roster.grch37_people)) < f)
                    ref, alt = pairs[int(rng.integers(len(pairs)))]
                    group.append((chrom, int(p), f"GSA-{chrom}:{int(p)}", ref, alt, g.astype(np.int8)))
    extra = unconvertible[:24] + moved[:6]
    final = sorted({(r[0], r[1]): r for r in fixed + chosen + extra}.values(), key=lambda r: (CHROM_ORDER[r[0]], r[1]))
    g = np.array([r[5] for r in final], dtype=np.int8)
    g[rng.random(g.shape) < 0.001] = -1
    core.write_bed(str(d / "legacy_grch37.bed"), g)
    with open(d / "legacy_grch37.bim", "w", encoding="ascii", newline="\n") as fh:
        for c, p, n, ref, alt, _ in final:
            fh.write(f"{c}\t{n}\t0\t{p}\t{alt}\t{ref}\n")
    with open(d / "legacy_grch37.fam", "w", encoding="ascii", newline="\n") as fh:
        for k, pid in enumerate(roster.grch37_people):
            fh.write(f"LEG37_{k + 1:03d}\tLEG37_{k + 1:03d}\t0\t0\t{roster.people[pid].sex}\t-9\n")
    return {"samples": len(roster.grch37_people), "variants": len(final), "known_snps": {r[2]: [r[0], r[1]] for r in fixed},
            "not_convertible": [r[2] for r in unconvertible[:24]], "change_chromosome": [r[2] for r in moved[:6]]}


def write_imputation(b: Build, sim: dict, table: dict, roster: Roster, flow: dict, loci: dict) -> dict:
    """Simulated imputation server output for two regions, in the Minimac4 layout of the Michigan and HMIS
    servers: dosage VCF (GT:DS:GP) and info file. The true genotypes go to the instructor folder."""
    rng = b.rng(7)
    removed = {i for ids in flow["removed"].values() for i in ids}
    final_subjects = [k for k, sub in enumerate(roster.subjects) if sub.sample_id not in removed]
    planted = {(c, int(p)) for c, p, pl, r, a in zip(table["chrom"], table["pos"], table["planted"], table["ref"],
                                                     table["alt"]) if pl or core.is_palindromic(r, a)}
    summary = {}
    for name, region in sim["regions"].items():
        chrom = region["ids"][0].split(":")[0]
        row_of = {int(p): k for k, p in enumerate(region["people"])}
        rows = np.array([row_of[roster.subjects[k].person] for k in final_subjects])
        haps = np.concatenate([region["h1"][rows], region["h2"][rows]], axis=0)       # [2n, variant]
        n = len(rows)
        freq = haps.mean(axis=0)
        maf = np.minimum(freq, 1 - freq)
        pos = region["pos"]
        typed = region["is_array"] & (maf >= 0.01) & np.array([(chrom, int(p)) not in planted for p in pos])
        keep = typed | (~region["is_array"] & (maf >= 0.01))
        x = haps[:, keep].astype(np.float32)
        x -= x.mean(axis=0)
        x /= np.where(x.std(axis=0) > 0, x.std(axis=0), 1)
        typed_k = typed[keep]
        r2 = (x.T @ x[:, typed_k] / x.shape[0]) ** 2                              # [variant, typed]
        r2[np.flatnonzero(typed_k), np.arange(typed_k.sum())] = 0.0               # a typed site: best other site
        best = r2.max(axis=1) if typed_k.any() else np.zeros(keep.sum())
        maf_k = maf[keep]
        target = np.clip((0.30 + 0.69 * np.sqrt(best)) * (1 - 0.5 * np.exp(-maf_k / 0.01)), 0.03, 0.99)
        true = haps[:, keep]
        dose = core.simulate_hap_dosages(true, target, rng)
        typed_only = np.zeros(keep.sum(), dtype=bool)
        t_idx = np.flatnonzero(typed_k)
        if len(t_idx):
            typed_only[rng.choice(t_idx, size=max(1, len(t_idx) // 50), replace=False)] = True
        loo = minimac = core.minimac_r2(dose)
        out_dose = np.where(typed_k[None, :], true.astype(np.float32), dose)
        ids = [f"chr{i}" for i, k in zip(region["ids"], keep) if k]
        samples = [roster.subjects[k].sample_id for k in final_subjects]
        d = b.student / "imputation"
        with gzip.open(d / f"chr{chrom}.dose.vcf.gz", "wt", encoding="ascii", newline="\n", compresslevel=6) as fh, \
                gzip.open(b.instructor / f"imputation_truth_chr{chrom}.vcf.gz", "wt", encoding="ascii", newline="\n") as tr, \
                gzip.open(d / f"chr{chrom}.info.gz", "wt", encoding="ascii", newline="\n") as info:
            head = ["##fileformat=VCFv4.1", "##source=simulated for the GWAS practical course (Minimac4 layout)",
                    f"##contig=<ID=chr{chrom}>", '##INFO=<ID=AF,Number=1,Type=Float,Description="Estimated Alternate Allele Frequency">',
                    '##INFO=<ID=MAF,Number=1,Type=Float,Description="Estimated Minor Allele Frequency">',
                    '##INFO=<ID=R2,Number=1,Type=Float,Description="Estimated Imputation Accuracy (R-square)">',
                    '##INFO=<ID=ER2,Number=1,Type=Float,Description="Empirical (Leave-One-Out) R-square (available only for genotyped variants)">',
                    '##INFO=<ID=IMPUTED,Number=0,Type=Flag,Description="Marker was imputed but NOT genotyped">',
                    '##INFO=<ID=TYPED,Number=0,Type=Flag,Description="Marker was genotyped AND imputed">',
                    '##INFO=<ID=TYPED_ONLY,Number=0,Type=Flag,Description="Marker was genotyped but NOT imputed">',
                    '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">',
                    '##FORMAT=<ID=DS,Number=1,Type=Float,Description="Estimated Alternate Allele Dosage : [P(0/1)+2*P(1/1)]">',
                    '##FORMAT=<ID=GP,Number=3,Type=Float,Description="Estimated Posterior Probabilities for Genotypes 0/0, 0/1 and 1/1">']
            columns = "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t" + "\t".join(samples)
            fh.write("\n".join(head) + "\n" + columns + "\n")
            tr.write("##fileformat=VCFv4.1\n##source=simulated truth (instructor only)\n"
                     '##FORMAT=<ID=GT,Number=1,Type=String,Description="True genotype">\n' + columns + "\n")
            info.write("SNP\tREF(0)\tALT(1)\tALT_Frq\tMAF\tAvgCall\tRsq\tGenotyped\tLooRsq\tEmpR\tEmpRsq\tDose0\tDose1\n")
            for j, vid in enumerate(ids):
                _, p, ref, alt = vid.split(":")
                d1, d2 = out_dose[:n, j], out_dose[n:, j]
                af = float(out_dose[:, j].mean())
                call = float(np.maximum(out_dose[:, j], 1 - out_dose[:, j]).mean())
                if typed_only[j]:
                    flag, rsq, kind, loo_txt = "TYPED_ONLY", "-", "Typed_Only", "-\t-\t-\t-\t-"
                    info_field = f"AF={af:.5f};MAF={min(af, 1 - af):.5f};TYPED_ONLY"
                elif typed_k[j]:
                    emp = float(np.clip(loo[j], 0, 1))
                    flag, rsq, kind = "TYPED", f"{min(0.99999, 0.9 + 0.1 * emp):.5f}", "Genotyped"
                    loo_txt = f"{emp:.5f}\t{emp ** 0.5:.5f}\t{emp:.5f}\t{0.5 - 0.4 * emp:.5f}\t{0.5 + 0.4 * emp:.5f}"
                    info_field = f"AF={af:.5f};MAF={min(af, 1 - af):.5f};R2={rsq};ER2={emp:.5f};TYPED"
                else:
                    flag, rsq, kind, loo_txt = "IMPUTED", f"{float(np.clip(minimac[j], 0, 1)):.5f}", "Imputed", "-\t-\t-\t-\t-"
                    info_field = f"AF={af:.5f};MAF={min(af, 1 - af):.5f};R2={rsq};IMPUTED"
                fh.write(f"chr{chrom}\t{p}\t{vid}\t{ref}\t{alt}\t.\tPASS\t{info_field}\tGT:DS:GP\t"
                         + "\t".join(core.dosage_fields(d1, d2)) + "\n")
                tr.write(f"chr{chrom}\t{p}\t{vid}\t{ref}\t{alt}\t.\tPASS\t{flag}\tGT\t"
                         + "\t".join(f"{a}|{c}" for a, c in zip(true[:n, j], true[n:, j])) + "\n")
                info.write(f"{vid}\t{ref}\t{alt}\t{af:.5f}\t{min(af, 1 - af):.5f}\t{call:.5f}\t{rsq}\t{kind}\t{loo_txt}\n")
        imputed = ~typed_k
        ds = out_dose[:n] + out_dose[n:]
        tg = (true[:n] + true[n:]).astype(float)
        with np.errstate(divide="ignore", invalid="ignore"):
            emp = np.array([np.corrcoef(ds[:, j], tg[:, j])[0, 1] ** 2 if tg[:, j].std() > 0 else 0 for j in range(ds.shape[1])])
        summary[name] = {"chrom": chrom, "start": int(pos[keep].min()), "end": int(pos[keep].max()), "samples": n,
                         "genotyped": int((typed_k & ~typed_only).sum()), "typed_only": int(typed_only.sum()),
                         "imputed": int(imputed.sum()), "median_rsq_imputed": round(float(np.median(minimac[imputed])), 3),
                         "median_true_r2_imputed": round(float(np.nanmedian(emp[imputed])), 3)}
        for lname, v in loci.items():
            if f"chr{v['kg_id']}" in ids:
                j = ids.index(f"chr{v['kg_id']}")
                summary[name][f"{lname}_causal"] = {"id": ids[j], "rsq": round(float(minimac[j]), 3),
                                                    "true_r2": round(float(emp[j]), 3), "typed": bool(typed_k[j])}
    return summary


# --- the build ---------------------------------------------------------------------------------------------------

LABEL_POOLS = ("N", "S", "AFR", "SAS", "EAS")
MAX_DONOR_SHARE = 0.03                                   # blocking: share of a genome copied from one donor
FULL_AUTOSOMAL_CM = 3543.0                               # autosomal length of the GRCh38 map (full build)
COPY_GROUPS = {"N": ("N",), "S": ("S",), "AFR": ("AFR",), "SAS": ("SAS",), "EAS": ("EAS",),
               "ADM": ("AFR", "N", "S")}                 # admixed AFR-EUR people against an AFR + EUR pool


def king_chunked(a: np.ndarray, b: np.ndarray, rows: int = 200) -> np.ndarray:
    """king_kinship in blocks of rows of `a`, to keep the float32 work matrices small."""
    return np.concatenate([core.king_kinship(a[k:k + rows], b) for k in range(0, len(a), rows)], axis=0)


def distribution(values: np.ndarray) -> dict:
    return {"pairs": int(values.size), "mean": round(float(values.mean()), 4),
            "p99": round(float(np.quantile(values, 0.99)), 4), "p999": round(float(np.quantile(values, 0.999)), 4),
            "max": round(float(values.max()), 4)}


def share_cap(two_over_h: float, autosomal_cm: float, partial: bool) -> float:
    """The blocking cap on the share copied from one donor: 3% in a full build. A partial build has fewer cM,
    so the share varies more; its cap is 2/H + (0.03 - 2/H) x sqrt(3,543 / cM of the build)."""
    if not partial:
        return MAX_DONOR_SHARE
    return two_over_h + (MAX_DONOR_SHARE - two_over_h) * (FULL_AUTOSOMAL_CM / autosomal_cm) ** 0.5


def copy_check(sim: dict, roster: Roster, donors: dict, partial: bool = False) -> dict:
    """Is any simulated person a copy, even partial, of a 1000 Genomes donor?

    Blocking: the share of a person's autosomal cM copied from one donor individual (both haplotypes, all
    segments, through meiosis too), computed from the mosaic's own choices, must stay below MAX_DONOR_SHARE;
    the expected value is 2/H with H donor haplotypes in the pool. Admixed people: the AFR haplotype against
    the AFR pool and the EUR haplotype against the EUR pool (N + S), each over one haplotype's cM.
    Descriptive only: KING kinship (every autosomal array site with MAF >= 0.01) simulated-donor and
    donor-donor, with the expected mosaic margin 1/H. Background kinship among unrelated study people."""
    total = sim["total_cm"]
    c1, c2 = sim["copied_l1"], sim["copied_l2"]
    offsets = sim["label_offsets"]
    pools_of = [p.pool for p in roster.people]
    result = {"total_autosomal_cm": round(total, 1), "max_donor_share": MAX_DONOR_SHARE, "shares": {},
              "note": "partial build: cap rescaled" if partial else "full build: cap 3%",
              "failures": [], "longest_copied_stretch_cm": round(float(sim["longest_cm"].max()), 2), "king": {}}

    def block(c, pools):
        return np.concatenate([c[:, offsets[p][0]:offsets[p][0] + offsets[p][1]] for p in pools], axis=1)

    plans = [(p, p, (p,), "both") for p in LABEL_POOLS] + [("ADM (AFR haplotype)", "ADM", ("AFR",), "l1"),
                                                           ("ADM (EUR haplotype)", "ADM", ("N", "S"), "l2")]
    for label, group, pools, which in plans:
        idx = [k for k, g in enumerate(pools_of) if g == group]
        if not idx:
            continue
        h = sum(offsets[p][1] for p in pools)
        if which == "both":
            share = core.donor_shares(block(c1, pools)[idx] + block(c2, pools)[idx], total, 2)
        else:
            share = core.donor_shares(block(c1 if which == "l1" else c2, pools)[idx], total, 1)
        row = {"people": len(idx), "donor_haplotypes": h, "expected_2_over_H": round(2 / h, 5),
               "mean": round(float(share.mean()), 5), "p99": round(float(np.quantile(share, 0.99)), 5),
               "max": round(float(share.max()), 5)}
        row["cap_used"] = round(share_cap(2 / h, total, partial), 5)
        row["passed"] = row["max"] < row["cap_used"]
        if not row["passed"]:
            result["failures"].append(label)
        result["shares"][label] = row

    people_g = np.concatenate(sim["king_people"], axis=1)
    donor_g = {pool: np.concatenate(parts, axis=1) for pool, parts in sim["king_donors"].items()}
    result["king"]["variants_used"] = int(people_g.shape[1])
    for group, pools in COPY_GROUPS.items():
        idx = [k for k, p in enumerate(roster.people) if p.pool == group]
        if not idx or any(p not in donor_g for p in pools):
            continue
        d = np.concatenate([donor_g[p] for p in pools], axis=0)
        sim_donor = king_chunked(people_g[idx], d)
        among = king_chunked(d, d)
        among = among[~np.eye(len(d), dtype=bool)]
        result["king"][group] = {"people": len(idx), "donors": len(d), "expected_margin_1_over_H": round(1 / (2 * len(d)), 5),
                                 "simulated_vs_donor": distribution(sim_donor), "donor_vs_donor": distribution(among)}
    unrelated = [k for k, p in enumerate(roster.people) if p.founder and p.kind in ("plain", "parent")][:600]
    kin = king_chunked(people_g[unrelated], people_g[unrelated])
    result["background_kinship_unrelated"] = {"people": len(unrelated),
                                              **distribution(kin[~np.eye(len(unrelated), dtype=bool)])}
    return result


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def build(s: Settings) -> dict:
    """Generate the dataset; returns the answer key (also written into instructor/)."""
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    b = Build(s)
    chain = core.Chain.from_file(str(s.chain))
    donors = choose_donors(b)
    sites = choose_sites(b, donors)
    known = known_snps(b, chain, sites)
    b.lap("donors and sites")
    loci = search_loci(b, donors, sites)
    regions = {}
    if "L4" in loci:
        regions["L4"] = ("18", loci["L4"]["pos"] - 250_000, loci["L4"]["pos"] + 250_000)
    if not s.only_chromosomes or "22" in s.only_chromosomes:
        regions["chr22"] = IMPUTATION_CHR22
    hidden_ids = {v["kg_id"] for v in loci.values()} | {v["kg_id"] for v in known.values()}
    hidden_points = [(i.split(":")[0], int(i.split(":")[1])) for i in hidden_ids]
    extract_donors(b, sites, hidden_points, list(regions.values()))
    b.lap("donor fileset")
    roster = make_roster(b.rng(2))
    flow = expected_flow(roster)
    sim = simulate_genomes(b, donors, sites, roster, loci, hidden_ids, regions)
    check = copy_check(sim, roster, donors, partial=bool(s.only_chromosomes))
    print(json.dumps(check, indent=1), flush=True)
    if check["failures"] or check["longest_copied_stretch_cm"] > s.max_copy_cm + 1e-6:
        raise RuntimeError(f"copy check failed: {check}")       # blocking in every build, partial or full
    if check["background_kinship_unrelated"]["max"] >= core.THIRD_DEGREE:
        if not s.only_chromosomes:
            raise RuntimeError(f"background kinship above the third-degree bound: {check}")
        check["warning"] = "partial build: background kinship above 0.0442 reported, not enforced"
    b.lap("copy check")
    planted = plant_problems(b, sites, roster, sim, loci, regions)
    w, table = planted["w"], planted["table"]
    b.lap("planting")
    write_lab_export(b, w, table, roster)
    b.lap("laboratory export")
    reports = write_final_reports(b, w, table, roster, {d["duplicate"] for d in planted["key"]["variants"]["duplicated"]})
    reference = write_pca_reference(b, donors)
    b.lap("final reports and PCA reference")
    grch37 = write_grch37_exercise(b, chain, sim, sites, known, table, roster)
    imputation = write_imputation(b, sim, table, roster, flow, loci)
    b.lap("GRCh37 exercise and imputation")

    status = np.array([p.status for p in roster.people])
    plain = np.array([p.founder and p.pool in ("N", "S") and p.status > 0 for p in roster.people])
    for name, carried in sim["loci"].items():
        loci[name]["risk_freq_cases"] = round(float(carried[plain & (status == 2)].mean() / 2), 4)
        loci[name]["risk_freq_controls"] = round(float(carried[plain & (status == 1)].mean() / 2), 4)
    subjects = [{"sample_id": sub.sample_id, "status": sub.status, "declared_sex": sub.sex,
                 "genetic_sex": roster.people[sub.person].sex, "age": sub.age, "pool": roster.people[sub.person].pool,
                 "kind": roster.people[sub.person].kind, "tags": sub.tags} for sub in roster.subjects]
    key = {
        "dataset": {"seed": s.seed, "wells": len(roster.wells), "subjects": len(roster.subjects),
                    "variants": int(len(table["name"])), "cases": sum(sub.status == 2 for sub in roster.subjects),
                    "controls": sum(sub.status == 1 for sub in roster.subjects),
                    "partial_build": list(s.only_chromosomes) if s.only_chromosomes else None,
                    "variants_by_chromosome": dict(collections.Counter(str(c) for c in table["chrom"]))},
        "loci": loci, "expected_sample_flow": flow, "copy_check": check,
        "donors": {"split": donors["split"], "pool_sizes": {k: len(v) for k, v in donors["pools"].items()},
                   "related_removed": donors["related_removed"], "dropped": donors["donors_dropped"],
                   "pairs_above_third_degree": donors["donor_pairs_above_third_degree"]},
        "pairs": [{"kind": kind, "id_1": roster.subjects[a].sample_id, "id_2": roster.subjects[c].sample_id}
                  for kind, a, c in roster.pairs],
        "replicates": [{"id": x["sample_id"], "replicate_of": x["replicate_of"]} for x in roster.wells if x["replicate_of"]],
        "contaminated": [{"sample_id": roster.subjects[k].sample_id, "share": round(a, 3)}
                         for k, (_, a) in roster.contaminants.items()],
        "admixed_outliers_leave_at_3_5": [
            {"sample_id": sub.sample_id, "status": sub.status,
             "note": "leaves at step 3.5 (F below mean - 3 SD): excess heterozygosity from mixed AFR-EUR ancestry, "
                     "so it is no longer there at the ancestry step 5.6"}
            for sub in roster.subjects if "ADM" in sub.tags],
        "haploid_sites_excluded": sites["haploid_sites_excluded"],
        "y_incomplete_donors_not_used_for_chrY": {
            "rule": "male donors with more than 5% missing chrY calls are not chrY sources and are left out of the "
                    "chrY missing-call count (approved by the author, 2026-11-11)",
            "missing_share": donors.get("y_incomplete_missing", {})},
        "subjects": subjects, **planted["key"],
        "palindromic_dropped_from_design": sites["palindromic_dropped"],
        "final_reports": reports, "pca_reference": reference, "grch37_exercise": grch37, "imputation": imputation,
    }
    (b.instructor / "answer_key.json").write_text(json.dumps(key, indent=1) + "\n", encoding="utf-8")
    (b.instructor / "answer_key.md").write_text(answer_key_markdown(key), encoding="utf-8")
    files = {str(p.relative_to(b.student)).replace("\\", "/"): {"bytes": p.stat().st_size, "sha256": sha256(p)}
             for p in sorted(b.student.rglob("*")) if p.is_file()}
    record = {"started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "seed": s.seed, "settings": {k: str(v) for k, v in asdict(s).items()}, "python": platform.python_version(),
              "numpy": np.__version__, "platform": platform.platform(), "timings_s": b.timings,
              "y_incomplete_donors": donors.get("y_incomplete_missing", {}),
              "haploid_sites_excluded": sites["haploid_sites_excluded"],
              "plink_commands": b.commands, "student_files": files}
    (b.instructor / "build_record.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    (b.student / "README_simulated.txt").write_text(README, encoding="ascii", newline="\n")
    return key


def answer_key_markdown(key: dict) -> str:
    d = key["dataset"]
    lines = ["# Simulated 2026 dataset: answer key (instructor only, never in the student release)", "",
             f"{d['wells']} wells, {d['subjects']} study IDs ({d['cases']} cases, {d['controls']} controls), "
             f"{d['variants']} variants. Seed {d['seed']}.", "", "## Causal loci", "",
             "| Locus | Variant | Risk allele | Odds ratio | Frequency controls | Frequency cases | Array neighbours r2 > 0.5 |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for name, v in key["loci"].items():
        lines.append(f"| {name} | {v['kg_id']} | {v['risk_allele']} | {v['odds_ratio']} | "
                     f"{v.get('risk_freq_controls', '')} | {v.get('risk_freq_cases', '')} | {v['array_neighbours_r2_0_5']} |")
    lines += ["", "## Expected sample flow", "", "| Step | Removed | Remaining |", "| --- | --- | --- |"]
    for step, c in key["expected_sample_flow"]["counts"].items():
        lines.append(f"| {step} | {c['removed']} | {c['remaining']} |")
    lines += ["", "## Planted variant problems", ""]
    for name, value in key["variants"].items():
        lines.append(f"- {name.replace('_', ' ')}: {len(value)}")
    c = key["copy_check"]
    return "\n".join(lines + [""] + copy_check_markdown(c))


def copy_check_markdown(c: dict) -> list[str]:
    """The copy check as Markdown tables (also used by the build report)."""
    lines = ["## Copy check", "", f"Share of the genome copied from one donor individual (blocking: maximum below "
             f"the cap used), over {c['total_autosomal_cm']} autosomal cM. {c.get('note', '')}.", "",
             "| Pool | People | Donor haplotypes H | Expected 2/H | Mean | p99 | Maximum | Cap used | Passed |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    lines += [f"| {g} | {x['people']} | {x['donor_haplotypes']} | {x['expected_2_over_H']} | {x['mean']} | {x['p99']} | "
              f"{x['max']} | {x.get('cap_used', c['max_donor_share'])} | {x['passed']} |" for g, x in c["shares"].items()]
    k = c["king"]
    lines += ["", f"KING kinship, descriptive only ({k['variants_used']} autosomal array variants with MAF >= 0.01). "
              "A mosaic is expected to sit about 1/H above the donor-donor values.", "",
              "| Pool | Expected margin 1/H | Simulated-donor mean / p99 / max | Donor-donor mean / p99 / max |",
              "| --- | --- | --- | --- |"]
    lines += [f"| {g} | {x['expected_margin_1_over_H']} | {x['simulated_vs_donor']['mean']} / {x['simulated_vs_donor']['p99']} / "
              f"{x['simulated_vs_donor']['max']} | {x['donor_vs_donor']['mean']} / {x['donor_vs_donor']['p99']} / "
              f"{x['donor_vs_donor']['max']} |" for g, x in k.items() if isinstance(x, dict)]
    lines += ["", f"Longest stretch copied from one donor haplotype: {c['longest_copied_stretch_cm']} cM (blocking cap 10). "
              f"Background KING among unrelated study people: {c['background_kinship_unrelated']}.", ""]
    return lines


README = """\
Simulated data for the GWAS practical course (2026)

Every individual in these files is simulated. Each genome is a mosaic of short segments of 1000 Genomes
haplotypes, so allele frequencies and linkage disequilibrium look real, but no individual is a real person
or a copy of one. Phenotypes are simulated, and the genetic effects are much stronger than real ones so that
a classroom-sized study shows clear signals. Some problems were planted on purpose: finding them is part of
the course. The Illumina Final Report files and the imputation output are simulated too.
"""


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--out", type=Path, required=True, help="output folder, outside the repository")
    p.add_argument("--seed", type=int, default=20261111)
    p.add_argument("--only-chromosomes", default=None, help="debugging: comma-separated chromosomes for a partial build")
    a = p.parse_args()
    out = a.out.resolve()
    if out == REPO or REPO in out.parents:
        sys.exit("--out must be outside the repository")
    only = tuple(a.only_chromosomes.split(",")) if a.only_chromosomes else None
    key = build(Settings(out=out, seed=a.seed, only_chromosomes=only))
    d = key["dataset"]
    print(f"{d['wells']} wells, {d['variants']} variants; copy check: {key['copy_check']}")


if __name__ == "__main__":
    main()
