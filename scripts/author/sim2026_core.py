"""Pure functions of the simulated 2026 course dataset (author side only; students never run this).

The haplotype mosaic, meiosis, allele errors, KING kinship, .bed packing, haplotype reading, LD neighbours and
the planting helpers follow the logic of the author's earlier generator (gwasx, tools/make_course_dataset.py),
rewritten here without any dependency on that project. New in this file: forced segments at causal loci,
chromosome X, contamination, differential missingness, plate layout, locus search, chain lift-over,
Illumina Final Report text and simulated imputation dosages.

Everything here works on arrays only, so it is tested on a synthetic donor panel
(scripts/author/tests/test_sim2026.py). Reading the real inputs and writing the dataset is in make_sim2026.py.
"""

from __future__ import annotations

import gzip
import math
from dataclasses import dataclass
from statistics import NormalDist

import numpy as np

THIRD_DEGREE = 0.0442                               # KING bound between third degree and unrelated
COMPLEMENT = {"A": "T", "C": "G", "G": "C", "T": "A"}
PAR1_END_B38, PAR2_START_B38 = 2_781_479, 155_701_383   # GRCh38 pseudo-autosomal boundaries on chrX
NO_HAP = 9                                          # marker of an absent second haplotype (male chrX)


# --- genetic map and mosaics ------------------------------------------------------------------------------

def interpolate_cm(positions: np.ndarray, map_pos: np.ndarray, map_cm: np.ndarray) -> np.ndarray:
    """Genetic position (cM) of each base-pair position; flat beyond the ends of the map."""
    return np.interp(positions, map_pos, map_cm)


def segment_breaks(total_cm: float, mean_cm: float, rng: np.random.Generator) -> np.ndarray:
    """Breakpoints (cM) of a Poisson process with the given mean distance on [0, total_cm]."""
    n = rng.poisson(total_cm / mean_cm) if total_cm > 0 else 0
    return np.sort(rng.uniform(0.0, total_cm, size=n))


def capped_breaks(total_cm: float, mean_cm: float, max_cm: float | None, rng: np.random.Generator) -> np.ndarray:
    """Poisson breakpoints, plus extra ones that split every segment longer than `max_cm` into equal parts."""
    breaks = segment_breaks(total_cm, mean_cm, rng)
    if max_cm is None:
        return breaks
    edges = np.concatenate([[0.0], breaks, [total_cm]])
    extra = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        parts = math.ceil((hi - lo) / max_cm)
        extra += [lo + (hi - lo) * k / parts for k in range(1, parts)]
    return np.sort(np.concatenate([breaks, extra])) if extra else breaks


def donor_sequence(n_segments: int, n_donors: int, rng: np.random.Generator) -> np.ndarray:
    """A random donor for every segment, never the same donor twice in a row."""
    choice = rng.integers(0, n_donors, size=n_segments)
    if n_donors > 1:
        for k in range(1, n_segments):
            while choice[k] == choice[k - 1]:
                choice[k] = rng.integers(0, n_donors)
    return choice


def mosaic(donors: np.ndarray, cm: np.ndarray, n_haps: int, mean_cm: float, rng: np.random.Generator,
           max_cm: float | None = None, forced_at: np.ndarray | None = None,
           forced_alleles: np.ndarray | None = None,
           labels_out: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """`n_haps` new haplotypes, each a sequence of segments copied from random donor haplotypes (rows of
    `donors`, 0/1 alleles, one column per variant in position order), with a new donor at every breakpoint.
    With `max_cm` no segment is longer than that, so no stretch longer than `max_cm` comes from one donor.

    Forced segments: `forced_at` lists variant columns and `forced_alleles[h, j]` the allele haplotype `h` must
    carry at column `forced_at[j]` (-1 = no constraint). The segment that covers the column then copies a donor
    that carries the allele, so the linkage disequilibrium around a causal variant stays that of the donors.

    With `labels_out` ([n_haps, variant] integers), the donor row copied at every variant is written into it.

    Returns the haplotypes and, per haplotype, the longest stretch (cM) copied from one donor haplotype."""
    n_donors, m = donors.shape
    out = np.empty((n_haps, m), dtype=np.uint8)
    longest = np.zeros(n_haps)
    start_cm, total = (cm[0], cm[-1] - cm[0]) if m else (0.0, 0.0)
    cols = np.arange(m)
    for h in range(n_haps):
        breaks = capped_breaks(total, mean_cm, max_cm, rng) + start_cm
        choice = donor_sequence(len(breaks) + 1, n_donors, rng)
        seg = np.searchsorted(breaks, cm, side="right")             # segment of each variant
        if forced_at is not None:
            for j, col in enumerate(forced_at):
                want = int(forced_alleles[h, j])
                k = int(seg[col])
                if want < 0 or donors[choice[k], col] == want:
                    continue
                carriers = np.flatnonzero(donors[:, col] == want)
                if len(carriers) == 0:
                    continue                                        # the allele does not exist in this pool
                near = [choice[k - 1] if k else -1, choice[k + 1] if k + 1 < len(choice) else -1]
                free = carriers[~np.isin(carriers, near)]
                choice[k] = rng.choice(free if len(free) else carriers)
        out[h] = donors[choice[seg], cols]
        if labels_out is not None:
            labels_out[h] = choice[seg]
        edges = np.concatenate([[start_cm], breaks, [start_cm + total]])
        run, best = 0.0, 0.0
        for k in range(len(choice)):
            run = run + (edges[k + 1] - edges[k]) if k and choice[k] == choice[k - 1] else edges[k + 1] - edges[k]
            best = max(best, run)
        longest[h] = best
    return out, longest


def meiosis_mask(cm: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Which parental haplotype (True = the first) a gamete takes at each variant: crossovers at 1 per Morgan."""
    total = cm[-1] - cm[0] if len(cm) else 0.0
    breaks = segment_breaks(total, 100.0, rng) + (cm[0] if len(cm) else 0.0)
    seg = np.searchsorted(breaks, cm, side="right")
    first = rng.integers(0, 2)
    return (seg + first) % 2 == 0


def meiosis(hap_a: np.ndarray, hap_b: np.ndarray, cm: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """One gamete from a parent with haplotypes a and b: crossovers at 1 per Morgan (100 cM)."""
    return np.where(meiosis_mask(cm, rng), hap_a, hap_b).astype(np.uint8)


def column_weights(cm: np.ndarray) -> np.ndarray:
    """The genetic length (cM) each variant stands for: half the distance to each neighbour, so the weights
    of a chromosome add up to its length between the first and the last variant."""
    if len(cm) < 2:
        return np.zeros(len(cm))
    edges = np.concatenate([[cm[0]], (cm[1:] + cm[:-1]) / 2, [cm[-1]]])
    return np.diff(edges)


def copied_cm(labels: np.ndarray, weights: np.ndarray, n_labels: int) -> np.ndarray:
    """cM copied from each donor haplotype: labels [person, variant] (donor haplotype copied at each variant,
    -1 none) and the variant weights; returns [person, n_labels]."""
    n = labels.shape[0]
    ok = labels >= 0
    rows = np.broadcast_to(np.arange(n)[:, None], labels.shape)
    flat = rows[ok] * n_labels + labels[ok]
    w = np.broadcast_to(weights[None, :], labels.shape)[ok]
    return np.bincount(flat, weights=w, minlength=n * n_labels).reshape(n, n_labels)


def donor_shares(cm_per_hap: np.ndarray, total_cm: float, n_haplotypes_per_person: int) -> np.ndarray:
    """Share of a person's genome copied from each donor individual: cM [person, donor haplotype] (two
    haplotypes per donor, in order), summed over the donor's two haplotypes, over the person's total."""
    per_donor = cm_per_hap[:, 0::2] + cm_per_hap[:, 1::2]
    return per_donor / (n_haplotypes_per_person * total_cm)


def add_allele_errors(haps: np.ndarray, rate: float, rng: np.random.Generator) -> int:
    """Flip each allele with probability `rate` (in place); returns the number flipped."""
    flips = rng.random(haps.shape) < rate
    haps[flips] ^= 1
    return int(flips.sum())


def tilted_frequency(freq: float, odds_ratio: float) -> float:
    """Allele frequency among cases when the per-allele odds ratio is `odds_ratio` and controls have `freq`
    (retrospective sampling under an additive logistic model: each case haplotype carries the allele
    independently with this probability)."""
    return freq * odds_ratio / (freq * odds_ratio + 1.0 - freq)


# --- people -------------------------------------------------------------------------------------------------

@dataclass
class Person:
    """One simulated genome. `pool` names the donor pool of a founder; `mother` and `father` are indices of
    earlier people for someone made by meiosis; `status` is 2 for a case, 1 for a control, 0 outside the study."""
    pool: str
    sex: int                                    # genetic sex: 1 male, 2 female
    status: int = 0
    kind: str = "plain"
    mother: int = -1
    father: int = -1
    two_x: bool = False                         # XXY profile: male with two X haplotypes
    conditioned: bool = True                    # causal alleles drawn given the status (founders only)
    note: str = ""

    @property
    def founder(self) -> bool:
        return self.mother < 0


def simulate_autosome(people: list[Person], donors: dict[str, np.ndarray], cm: np.ndarray,
                      rng: np.random.Generator, mean_cm: float = 3.0, max_cm: float | None = 10.0,
                      locus: dict | None = None, track: dict | None = None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Two haplotypes per person on one autosome: [person, variant] maternal and paternal, and the longest
    stretch (cM) copied from one donor haplotype (founders only).

    `donors[pool]` is [donor haplotype, variant]. The pool "ADM" (admixed) takes one haplotype from "AFR" and
    one from "EUR". `locus` = {"col": column, "risk": allele value 0/1, "or": odds ratio}: founders who are
    cases and `conditioned` get the risk allele on each haplotype with the tilted frequency of their pool.

    `track` = {"offset": {pool: first label}}: the donor haplotype copied at every variant is recorded as
    offset + donor row in track["l1"] and track["l2"] ([person, variant]), through meiosis too."""
    n, m = len(people), len(cm)
    h1 = np.zeros((n, m), dtype=np.uint8)
    h2 = np.zeros((n, m), dtype=np.uint8)
    longest = np.zeros(n)
    if track is not None:
        track["l1"] = np.full((n, m), -1, dtype=np.int32)
        track["l2"] = np.full((n, m), -1, dtype=np.int32)
    jobs: dict[str, list[tuple[int, int]]] = {}                    # pool -> (person, which haplotype)
    for k, p in enumerate(people):
        if not p.founder:
            continue
        pools = ("AFR", "EUR") if p.pool == "ADM" else (p.pool, p.pool)
        for which, pool in enumerate(pools):
            jobs.setdefault(pool, []).append((k, which))
    for pool, todo in jobs.items():
        pool_donors = donors[pool]
        forced_at = forced = None
        if locus is not None:
            col, risk = locus["col"], locus["risk"]
            freq = float((pool_donors[:, col] == risk).mean())
            forced = np.full((len(todo), 1), -1, dtype=np.int8)
            for row, (k, _) in enumerate(todo):
                p = people[k]
                if p.status == 2 and p.conditioned and p.pool in ("N", "S"):
                    carries = rng.random() < tilted_frequency(freq, locus["or"])
                    forced[row, 0] = risk if carries else 1 - risk
            forced_at = np.array([col])
        lab = np.zeros((len(todo), m), dtype=np.int32) if track is not None else None
        haps, long = mosaic(pool_donors, cm, len(todo), mean_cm, rng, max_cm, forced_at, forced, lab)
        for row, (k, which) in enumerate(todo):
            (h1 if which == 0 else h2)[k] = haps[row]
            longest[k] = max(longest[k], long[row])
            if track is not None:
                track["l1" if which == 0 else "l2"][k] = lab[row] + track["offset"][pool]
    for k, p in enumerate(people):                                 # parents always come before their children
        if p.founder:
            continue
        for key_h, key_l, parent in ((h1, "l1", p.mother), (h2, "l2", p.father)):
            mask = meiosis_mask(cm, rng)
            key_h[k] = np.where(mask, h1[parent], h2[parent])
            if track is not None:
                track[key_l][k] = np.where(mask, track["l1"][parent], track["l2"][parent])
    return h1, h2, longest


def simulate_x(people: list[Person], donors: dict[str, np.ndarray], cm: np.ndarray, rng: np.random.Generator,
               mean_cm: float = 3.0, max_cm: float | None = 10.0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Chromosome X outside the pseudo-autosomal regions. Women (and the XXY profile) get two haplotypes, men
    one. Returns [person, variant] first and second haplotype and a mask of the people with one haplotype only
    (their second row repeats the first). A daughter receives her father's X; a son receives none from him."""
    n, m = len(people), len(cm)
    h1 = np.zeros((n, m), dtype=np.uint8)
    h2 = np.zeros((n, m), dtype=np.uint8)
    one = np.array([p.sex == 1 and not p.two_x for p in people])
    for pool in sorted({p.pool for p in people if p.founder}):
        todo = [(k, w) for k, p in enumerate(people) if p.founder and p.pool == pool
                for w in range(1 if one[k] else 2)]
        if not todo:
            continue
        if pool == "ADM":
            parts = {0: donors["AFR"], 1: donors["EUR"]}
            for w, pool_donors in parts.items():
                sub = [(k, ww) for k, ww in todo if ww == w]
                haps, _ = mosaic(pool_donors, cm, len(sub), mean_cm, rng, max_cm)
                for row, (k, ww) in enumerate(sub):
                    (h1 if ww == 0 else h2)[k] = haps[row]
            continue
        haps, _ = mosaic(donors[pool], cm, len(todo), mean_cm, rng, max_cm)
        for row, (k, w) in enumerate(todo):
            (h1 if w == 0 else h2)[k] = haps[row]
    for k, p in enumerate(people):
        if p.founder:
            continue
        h1[k] = meiosis(h1[p.mother], h2[p.mother], cm, rng)       # the mother always has two X
        if not one[k]:
            h2[k] = h1[p.father]
    h2[one] = h1[one]
    return h1, h2, one


def well_genotypes(h1: np.ndarray, h2: np.ndarray, well_person: np.ndarray, error_rate: float,
                   rng: np.random.Generator, one_haplotype: np.ndarray | None = None) -> np.ndarray:
    """Genotypes [variant, well] (ALT counts) of each well's person, with independent allele errors per well,
    so a person typed in two wells gives two slightly different calls. People with one haplotype (men on chrX)
    are written as homozygous."""
    a = h1[well_person].copy()
    b = h2[well_person].copy()
    add_allele_errors(a, error_rate, rng)
    add_allele_errors(b, error_rate, rng)
    if one_haplotype is not None:
        single = one_haplotype[well_person]
        b[single] = a[single]
    return (a.astype(np.int8) + b.astype(np.int8)).T.copy()


# --- kinship and LD -------------------------------------------------------------------------------------------

def king_kinship(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """KING-robust kinship between the rows of `a` and the rows of `b` (genotypes 0/1/2, -1 missing):
    (N_AaAa - 2 N_AA,aa) / (N_Aa(i) + N_Aa(j)), over the variants both have called."""
    def parts(g):
        called = (g >= 0).astype(np.float32)
        return (g == 1).astype(np.float32), (g == 0).astype(np.float32), (g == 2).astype(np.float32), called
    het_a, ref_a, alt_a, call_a = parts(a)
    het_b, ref_b, alt_b, call_b = parts(b)
    both_het = het_a @ het_b.T
    opposite = ref_a @ alt_b.T + alt_a @ ref_b.T
    het_i = het_a @ call_b.T                      # heterozygotes of i where j is called
    het_j = call_a @ het_b.T
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(het_i + het_j > 0, (both_het - 2 * opposite) / (het_i + het_j), 0.0)


def hwe_chi2_p(g: np.ndarray) -> float:
    """Chi-square (1 df) Hardy-Weinberg p-value of one variant's genotypes (0/1/2, -1 missing); a check only."""
    g = g[g >= 0]
    n = len(g)
    if n == 0:
        return 1.0
    obs = np.array([(g == 0).sum(), (g == 1).sum(), (g == 2).sum()], dtype=float)
    p = (2 * obs[2] + obs[1]) / (2 * n)
    exp = n * np.array([(1 - p) ** 2, 2 * p * (1 - p), p ** 2])
    stat = float(((obs - exp) ** 2 / np.where(exp > 0, exp, 1)).sum())
    return math.erfc(math.sqrt(stat / 2))


def r2_with(haps: np.ndarray, index: int) -> np.ndarray:
    """Squared correlation between column `index` and every column of `haps` [observation, variant]
    (0 where a column does not vary)."""
    x = haps.astype(np.float32)
    x -= x.mean(axis=0)
    sd = x.std(axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = (x * x[:, [index]]).mean(axis=0) / (sd * sd[index])
    return np.nan_to_num(r ** 2, nan=0.0, posinf=0.0)


def ld_neighbours(haps: np.ndarray, pos: np.ndarray, index: int, window_bp: int = 250_000, r2: float = 0.5) -> int:
    """Number of other variants within `window_bp` of variant `index` with r^2 above `r2`."""
    lo, hi = np.searchsorted(pos, [pos[index] - window_bp, pos[index] + window_bp + 1])
    values = r2_with(haps[:, lo:hi], index - lo)
    return int((values > r2).sum()) - int(values[index - lo] > r2)


def find_locus(haps: np.ndarray, pos: np.ndarray, on_array: np.ndarray, allowed: np.ndarray, north: np.ndarray,
               south: np.ndarray, target_freq: float, want_on_array: bool, freq_tol: float = 0.02,
               ns_max: float = 0.03, window_bp: int = 250_000, r2_min: float = 0.5, min_dense: int = 20,
               tag_r2: tuple[float, float] = (0.75, 0.85), candidate: np.ndarray | None = None) -> dict | None:
    """Choose a causal variant on one chromosome from donor haplotypes [haplotype, variant].

    Conditions: risk-allele frequency within `freq_tol` of the target, North/South difference below `ns_max`,
    at least `min_dense` neighbours with r^2 above `r2_min`, and `allowed`. Among those, the variant with the
    most array neighbours above `r2_min` wins. An off-array variant also needs one array tag with r^2 inside
    `tag_r2` and no array variant above it. `candidate` restricts which variants may be chosen (default: the
    array variants, or the others when `want_on_array` is False). Returns None when nothing qualifies."""
    f = haps.mean(axis=0)
    f_n, f_s = haps[north].mean(axis=0), haps[south].mean(axis=0)
    risk_is_one = np.abs(f - target_freq) <= np.abs(1 - f - target_freq)
    risk_freq = np.where(risk_is_one, f, 1 - f)
    candidates = np.flatnonzero((np.abs(risk_freq - target_freq) <= freq_tol) & (np.abs(f_n - f_s) < ns_max)
                                & allowed & ((on_array == want_on_array) if candidate is None else candidate))
    best = None
    for j in candidates:
        lo, hi = np.searchsorted(pos, [pos[j] - window_bp, pos[j] + window_bp + 1])
        values = r2_with(haps[:, lo:hi], j - lo)
        values[j - lo] = 0.0
        if int((values > r2_min).sum()) < min_dense:
            continue
        array_here = on_array[lo:hi]
        tag = None
        if not want_on_array:
            if (values[array_here] > tag_r2[1]).any():
                continue
            ok = np.flatnonzero(array_here & (values >= tag_r2[0]) & (values <= tag_r2[1]) & allowed[lo:hi])
            if len(ok) == 0:
                continue
            t = ok[np.argmin(np.abs(values[ok] - 0.8))]
            tag = (int(lo + t), float(values[t]))
        score = (int((values[array_here] > r2_min).sum()), int((values > r2_min).sum()),
                 -abs(float(risk_freq[j]) - target_freq))
        if best is None or score > best["score"]:
            best = {"score": score, "col": int(j), "risk": int(risk_is_one[j]), "risk_freq": float(risk_freq[j]),
                    "freq_north": float(f_n[j] if risk_is_one[j] else 1 - f_n[j]),
                    "freq_south": float(f_s[j] if risk_is_one[j] else 1 - f_s[j]),
                    "array_neighbours": score[0], "dense_neighbours": score[1],
                    "array_neighbours_r2_0_2": int((values[array_here] > 0.2).sum()), "tag": tag}
    return best


# --- alleles and strand ---------------------------------------------------------------------------------------

def is_palindromic(a: str, b: str) -> bool:
    """A/T and C/G variants read the same on both strands."""
    return COMPLEMENT.get(a) == b


def complement_alleles(a: str, b: str) -> tuple[str, str]:
    return COMPLEMENT[a], COMPLEMENT[b]


def incompatible_alleles(ref: str, alt: str) -> tuple[str, str]:
    """An allele pair that matches (ref, alt) on neither strand and is not palindromic."""
    return ref, COMPLEMENT[alt]


def allele_check(file_a: str, file_b: str, ref: str, alt: str) -> str:
    """How a file's allele pair relates to the annotated pair: 'palindromic', 'same', 'flip' or 'mismatch'."""
    if is_palindromic(ref, alt):
        return "palindromic"
    if {file_a, file_b} == {ref, alt}:
        return "same"
    if {file_a, file_b} == set(complement_alleles(ref, alt)):
        return "flip"
    return "mismatch"


# --- planting -------------------------------------------------------------------------------------------------

def plant_sample_missingness(g: np.ndarray, samples: list[int], rng: np.random.Generator, low: float = 0.04,
                             high: float = 0.08, weights: np.ndarray | None = None,
                             exact: bool = False) -> dict[int, float]:
    """Set a share (uniform in [low, high]) of each listed sample's genotypes missing; g is [variant, sample].
    `weights` are relative per-variant chances (0 = never). With `exact` the number of missing calls is exactly
    the share of the variants with a positive weight."""
    m = g.shape[0]
    w = np.ones(m) if weights is None else np.asarray(weights, dtype=float)
    shares = {}
    for s in samples:
        share = float(rng.uniform(low, high))
        if exact:
            eligible = np.flatnonzero(w > 0)
            rows = rng.choice(eligible, size=int(round(share * len(eligible))), replace=False,
                              p=w[eligible] / w[eligible].sum())
            g[rows, s] = -1
        else:
            g[rng.random(m) < share * w / w.mean(), s] = -1
        shares[int(s)] = share
    return shares


def plant_variant_missingness(g: np.ndarray, variants: list[int], rng: np.random.Generator, low: float = 0.05,
                              high: float = 0.15, exact: bool = False) -> dict[int, float]:
    """Set a share (uniform in [low, high]) of each listed variant's genotypes missing."""
    shares = {}
    for v in variants:
        share = float(rng.uniform(low, high))
        if exact:
            g[v, rng.choice(g.shape[1], size=int(round(share * g.shape[1])), replace=False)] = -1
        else:
            g[v, rng.random(g.shape[1]) < share] = -1
        shares[int(v)] = share
    return shares


def plant_differential_missingness(g: np.ndarray, variant: int, cases: np.ndarray, controls: np.ndarray,
                                   rng: np.random.Generator, case_rate: float = 0.032,
                                   control_rate: float = 0.002, het_weight: float = 3.0) -> tuple[int, int]:
    """Missing calls at an exact rate in cases and in controls; heterozygotes are `het_weight` times more
    likely to be lost. Returns the numbers set missing (cases, controls)."""
    row = g[variant]
    done = []
    for group, rate in ((cases, case_rate), (controls, control_rate)):
        idx = np.flatnonzero(group & (row >= 0))
        k = min(len(idx), int(round(rate * int(group.sum()))))
        w = np.where(row[idx] == 1, het_weight, 1.0)
        chosen = rng.choice(idx, size=k, replace=False, p=w / w.sum()) if k else np.array([], dtype=int)
        row[chosen] = -1
        done.append(int(k))
    return done[0], done[1]


def plant_hwe_failure(g: np.ndarray, variant: int, samples: np.ndarray, rng: np.random.Generator,
                      share: float = 0.25) -> int:
    """Heterozygote deficit: a share of the heterozygotes among `samples` become homozygous (either way)."""
    row = g[variant]
    hets = np.flatnonzero((row == 1) & samples)
    chosen = hets[rng.random(len(hets)) < share]
    row[chosen] = np.where(rng.random(len(chosen)) < 0.5, 0, 2)
    return int(len(chosen))


def plant_het_loss(g: np.ndarray, samples: np.ndarray, rng: np.random.Generator, share: float) -> float:
    """A faulty plate: in the listed sample columns, each heterozygous call becomes homozygous with
    probability `share`. Returns the share of all their called genotypes that changed."""
    block = g[:, samples]
    lost = (block == 1) & (rng.random(block.shape) < share)
    block[lost] = np.where(rng.random(int(lost.sum())) < 0.5, 0, 2)
    g[:, samples] = block
    return float(lost.sum() / max(1, (block >= 0).sum()))


def contaminate(own: np.ndarray, other: np.ndarray, alpha: float, rng: np.random.Generator,
                no_call: float = 0.01) -> np.ndarray:
    """Genotype calls of a DNA sample that holds a share `alpha` of another person's DNA.

    The B-allele fraction moves from the own cluster (0, 0.5, 1) by alpha x (other - own) / 2. A homozygous
    call becomes heterozygous with probability min(1, shift / 0.2); a shifted call is lost with probability
    `no_call`. The result is excess heterozygosity that grows with alpha."""
    out = own.copy()
    valid = (own >= 0) & (other >= 0)
    shift = np.where(valid, alpha * np.abs(other.astype(float) - own) / 2.0, 0.0)
    to_het = valid & (own != 1) & (rng.random(own.shape) < np.minimum(1.0, shift / 0.2))
    out[to_het] = 1
    out[valid & (shift > 0) & (rng.random(own.shape) < no_call)] = -1
    return out


# --- plates ---------------------------------------------------------------------------------------------------

def well_label(position: int) -> str:
    """Position 0..95 on a 96-well plate, filled by row: A01 ... A12, B01 ... H12."""
    return "ABCDEFGH"[position // 12] + f"{position % 12 + 1:02d}"


def assign_plates(n_wells: int, special: np.ndarray, replicate_of: np.ndarray, rng: np.random.Generator,
                  per_plate: int = 96, bad_plate: int = 14) -> tuple[np.ndarray, np.ndarray]:
    """Random plate (1-based) and position (0-based) of every well. The bad plate holds only wells that are not
    `special`. A replicate (replicate_of >= 0) is never on the plate of its original."""
    n_plates = n_wells // per_plate
    if n_plates * per_plate != n_wells:
        raise ValueError("the wells do not fill whole plates")
    plain = np.flatnonzero(~special)
    on_bad = rng.choice(plain, size=per_plate, replace=False)
    rest = rng.permutation(np.setdiff1d(np.arange(n_wells), on_bad))
    plate = np.zeros(n_wells, dtype=int)
    plate[on_bad] = bad_plate
    other_plates = [p for p in range(1, n_plates + 1) if p != bad_plate]
    plate[rest] = np.repeat(other_plates, per_plate)
    for r in np.flatnonzero(replicate_of >= 0):
        while plate[r] == plate[replicate_of[r]]:
            swap = int(rng.choice(np.flatnonzero((plate != plate[r]) & (plate != bad_plate) & ~special)))
            plate[r], plate[swap] = plate[swap], plate[r]
    position = np.zeros(n_wells, dtype=int)
    for p in range(1, n_plates + 1):
        members = np.flatnonzero(plate == p)
        position[members] = rng.permutation(per_plate)
    return plate, position


# --- reading and writing ----------------------------------------------------------------------------------------

def read_haps(prefix: str) -> tuple[list[tuple[str, str, int, str, str]], list[str], np.ndarray]:
    """A PLINK 2 `--export haps` file: per variant (chromosome, ID, position, allele coded 0, allele coded 1),
    the sample IDs, and the haplotypes [haplotype, variant], two per sample in sample order. The absent second
    haplotype of a man on chrX ('-') is stored as NO_HAP."""
    rows, haps = [], []
    with open(f"{prefix}.haps", "rb") as fh:
        for line in fh:
            head = line.split(b" ", 5)
            rows.append((head[0].decode(), head[1].decode(), int(head[2]), head[3].decode(), head[4].decode()))
            values = np.frombuffer(head[5].rstrip(b"\r\n")[::2], dtype=np.uint8) - 48
            haps.append(np.where(values > 1, NO_HAP, values).astype(np.uint8))
    with open(f"{prefix}.sample", encoding="utf-8") as fh:
        samples = [line.split()[1] for line in fh][2:]
    matrix = np.array(haps, dtype=np.uint8).T.copy() if haps else np.zeros((2 * len(samples), 0), dtype=np.uint8)
    return rows, samples, matrix


def pack_bed_rows(genotypes: np.ndarray) -> bytes:
    """PLINK 1 .bed body (variant-major) for genotypes [variant, sample] as A1 counts (0/1/2, -1 missing);
    A1 is the first allele of the .bim line."""
    code = np.full(genotypes.shape, 0b01, dtype=np.uint8)           # missing
    code[genotypes == 2] = 0b00
    code[genotypes == 1] = 0b10
    code[genotypes == 0] = 0b11
    n_var, n = code.shape
    pad = (-n) % 4
    if pad:
        code = np.concatenate([code, np.zeros((n_var, pad), dtype=np.uint8)], axis=1)
    code = code.reshape(n_var, -1, 4)
    packed = code[:, :, 0] | (code[:, :, 1] << 2) | (code[:, :, 2] << 4) | (code[:, :, 3] << 6)
    return packed.astype(np.uint8).tobytes()


def unpack_bed_rows(body: bytes, n_samples: int) -> np.ndarray:
    """The inverse of pack_bed_rows: genotypes [variant, sample] as A1 counts, -1 missing."""
    raw = np.frombuffer(body, dtype=np.uint8).reshape(-1, (n_samples + 3) // 4)
    codes = np.stack([(raw >> shift) & 3 for shift in (0, 2, 4, 6)], axis=2).reshape(raw.shape[0], -1)[:, :n_samples]
    return np.array([2, -1, 1, 0], dtype=np.int8)[codes]


def write_bed(path: str, genotypes: np.ndarray, chunk: int = 20_000) -> None:
    with open(path, "wb") as fh:
        fh.write(bytes([0x6C, 0x1B, 0x01]))
        for start in range(0, genotypes.shape[0], chunk):
            fh.write(pack_bed_rows(genotypes[start:start + chunk]))


def genotype_letters(g: np.ndarray, a1: str, a2: str, missing: str = "0") -> list[tuple[str, str]]:
    """Allele letters of genotypes given as counts of `a1`: 2 -> a1 a1, 1 -> a1 a2 (sorted), 0 -> a2 a2."""
    het = tuple(sorted((a1, a2)))
    table = {2: (a1, a1), 1: het, 0: (a2, a2), -1: (missing, missing)}
    return [table[int(x)] for x in g]


def final_report(sample_id: str, names: list[str], ref: list[str], alt: list[str], g: np.ndarray,
                 gc: np.ndarray, content: str, total_samples: int, file_index: int,
                 processing_date: str = "11/11/2026 10:30 AM") -> bytes:
    """One sample's Illumina Final Report in the GenomeStudio layout agreed for the course: semicolons,
    decimal points, CRLF line ends, plus-strand alleles, '-' and 0.0000 for a missing call."""
    n = len(names)
    lines = ["[Header]", "GSGT Version;2.0.4", f"Processing Date;{processing_date}", f"Content;;{content}",
             f"Num SNPs;{n}", f"Total SNPs;{n}", f"Num Samples;{total_samples}", f"Total Samples;{total_samples}",
             f"File ;{file_index} of {total_samples}", "[Data]",
             "SNP Name;Sample ID;GC Score;Allele1 - Plus;Allele2 - Plus"]
    for name, r, a, x, score in zip(names, ref, alt, g, gc):
        if x < 0:
            lines.append(f"{name};{sample_id};0.0000;-;-")
        else:
            one, two = ((r, r), tuple(sorted((r, a))), (a, a))[int(x)]
            lines.append(f"{name};{sample_id};{score:.4f};{one};{two}")
    return ("\r\n".join(lines) + "\r\n").encode("ascii")


def gc_scores(g: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """GenCall-like scores: high for called genotypes, 0 for missing calls."""
    scores = 0.15 + 0.84 * rng.beta(9.0, 1.6, size=g.shape)
    return np.where(g >= 0, np.round(scores, 4), 0.0)


# --- imputation-like dosages ---------------------------------------------------------------------------------

def simulate_hap_dosages(haps: np.ndarray, target_r2: np.ndarray, rng: np.random.Generator,
                         concentration: float = 60.0) -> np.ndarray:
    """Imputed haplotype dosages [haplotype, variant] for true alleles `haps`.

    Each haplotype follows a copied allele: the true allele with probability c, otherwise an allele drawn from
    the frequency f (so it is sometimes wrong). The dosage is the calibrated probability that the true allele
    is 1 given the copied allele: (1 - c) f + c x copied. With c = sqrt(target r^2), both the Minimac R-square
    (dosage variance over f(1 - f)) and the true r^2 between dosage and truth are close to c^2. c varies a
    little between haplotypes (beta with the given concentration), so dosages are not just two values."""
    freq = haps.mean(axis=0)
    q = np.clip(np.sqrt(target_r2), 0.02, 0.995)
    c = rng.beta(q * concentration, (1 - q) * concentration, size=haps.shape)
    follows_truth = rng.random(haps.shape) < c
    copied = np.where(follows_truth, haps, rng.random(haps.shape) < freq).astype(np.float32)
    return ((1 - c) * freq + c * copied).astype(np.float32)


def minimac_r2(hap_dosages: np.ndarray) -> np.ndarray:
    """The imputation quality reported by Minimac: variance of the haplotype dosages over p(1 - p)."""
    p = hap_dosages.mean(axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.nan_to_num(hap_dosages.var(axis=0) / (p * (1 - p)), nan=0.0, posinf=0.0)


def dosage_fields(d1: np.ndarray, d2: np.ndarray) -> list[str]:
    """VCF sample fields GT:DS:GP for one variant from the two haplotype dosages of every sample."""
    ds = d1 + d2
    p2, p0 = d1 * d2, (1 - d1) * (1 - d2)
    p1 = 1 - p0 - p2
    gt1, gt2 = (d1 > 0.5).astype(int), (d2 > 0.5).astype(int)
    return [f"{a}|{b}:{x:.3f}:{u:.3f},{v:.3f},{w:.3f}" for a, b, x, u, v, w in zip(gt1, gt2, ds, p0, p1, p2)]


# --- chain lift-over --------------------------------------------------------------------------------------------

class Chain:
    """A UCSC chain file as ungapped blocks: (source start, source end, target contig, target start, sign,
    chain score), 0-based, grouped by source contig. `lift` uses the best-scoring chain that covers a position,
    as liftOver does."""

    def __init__(self, blocks: dict[str, list[tuple[int, int, str, int, int, float, int]]]):
        self.blocks = blocks

    @classmethod
    def from_file(cls, path: str) -> "Chain":
        opener = gzip.open if str(path).endswith(".gz") else open
        with opener(path, "rt") as fh:
            return cls.from_lines(fh)

    @classmethod
    def from_lines(cls, lines) -> "Chain":
        blocks: dict[str, list] = {}
        chain_id = 0
        for line in lines:
            f = line.split()
            if not f:
                continue
            if f[0] == "chain":
                score, t_name, t = float(f[1]), f[2], int(f[5])
                q_name, q_size, q_strand, q = f[7], int(f[8]), f[9], int(f[10])
                chain_id += 1
                continue
            size = int(f[0])
            start, sign = (q, 1) if q_strand == "+" else (q_size - 1 - q, -1)
            blocks.setdefault(t_name, []).append((t, t + size, q_name, start, sign, score, chain_id))
            if len(f) == 3:
                t += size + int(f[1])
                q += size + int(f[2])
        return cls(blocks)

    def inverted(self) -> "Chain":
        """The same alignment read from target to source."""
        out: dict[str, list] = {}
        for src, items in self.blocks.items():
            for s0, s1, dst, d0, sign, score, cid in items:
                size = s1 - s0
                if sign == 1:
                    out.setdefault(dst, []).append((d0, d0 + size, src, s0, 1, score, cid))
                else:
                    out.setdefault(dst, []).append((d0 - size + 1, d0 + 1, src, s1 - 1, -1, score, cid))
        return Chain(out)

    def lift(self, contig: str, positions: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """1-based positions on `contig` -> (target contig names, 1-based target positions); '' and -1 where
        no chain covers the position."""
        p0 = np.asarray(positions, dtype=np.int64) - 1
        names = np.full(len(p0), "", dtype=object)
        out = np.full(len(p0), -1, dtype=np.int64)
        by_chain: dict[int, list] = {}
        for b in self.blocks.get(contig, []):
            by_chain.setdefault(b[6], []).append(b)
        for items in sorted(by_chain.values(), key=lambda it: -it[0][5]):
            todo = np.flatnonzero(out < 0)
            if len(todo) == 0:
                break
            items = sorted(items)
            starts = np.array([b[0] for b in items])
            ends = np.array([b[1] for b in items])
            k = np.searchsorted(starts, p0[todo], side="right") - 1
            hit = (k >= 0) & (p0[todo] < ends[np.maximum(k, 0)])
            d0 = np.array([b[3] for b in items])
            sign = items[0][4]
            sel, kk = todo[hit], k[hit]
            out[sel] = d0[kk] + sign * (p0[sel] - starts[kk]) + 1
            names[sel] = items[0][2]
        return names, out


# --- statistics -------------------------------------------------------------------------------------------------

def lambda_gc(p_values: np.ndarray) -> float:
    """Genomic inflation factor: the chi-square (1 df) of the median p-value over 0.4549."""
    p = np.asarray(p_values, dtype=float)
    p = p[np.isfinite(p) & (p > 0) & (p <= 1)]
    if len(p) == 0:
        return float("nan")
    z = NormalDist().inv_cdf(1 - float(np.median(p)) / 2)
    return z * z / 0.4549364
