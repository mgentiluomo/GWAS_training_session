"""Tests of the simulated 2026 dataset generator on a synthetic donor panel.

The full build needs the local 1000 Genomes files and runs on the author's machine only. These tests check
the parts that decide whether the data are right: the haplotype mosaic (alleles copied from donors, segment
lengths, the cap, forced segments at causal loci), meiosis, chromosome X, the KING kinship of the copy check,
the planting of problems, the plate layout, the file writers, the chain lift-over and the study roster.

Run with pytest, or without it:  python -I scripts/author/tests/test_sim2026.py
"""

import math
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import make_sim2026 as gen  # noqa: E402
import sim2026_core as m  # noqa: E402
from sim2026_core import Person  # noqa: E402


def panel(n_donors=40, m_variants=600, seed=1):
    """Synthetic donor haplotypes with some LD: blocks of 20 variants share a few founder patterns."""
    rng = np.random.default_rng(seed)
    founders = rng.integers(0, 2, size=(6, m_variants), dtype=np.uint8)
    blocks = np.repeat(np.arange(m_variants // 20), 20)
    donors = np.empty((n_donors, m_variants), dtype=np.uint8)
    for d in range(n_donors):
        pick = rng.integers(0, 6, size=blocks.max() + 1)
        donors[d] = founders[pick[blocks], np.arange(m_variants)]
    return donors, np.linspace(0.0, 60.0, m_variants)                 # a 60 cM chromosome


def hwe_population(n, m_variants, rng):
    freqs = rng.uniform(0.1, 0.5, m_variants)
    return (rng.random((2 * n, m_variants)) < freqs).astype(np.uint8)


def genotypes(haps):
    return haps[0::2].astype(np.int8) + haps[1::2]


def close(a, b, tol):
    return abs(a - b) <= tol


# --- mosaic and meiosis ------------------------------------------------------------------------------------

def test_every_mosaic_allele_comes_from_a_donor_at_the_same_variant():
    donors, cm = panel()
    haps, _ = m.mosaic(donors, cm, 20, 3.0, np.random.default_rng(2))
    for h in haps:
        assert all(h[v] in donors[:, v] for v in range(donors.shape[1]))


def test_the_mosaic_switches_donors_at_about_the_mean_segment_length():
    """Each donor carries its own label at every variant, so the mosaic shows where every variant came from."""
    n_donors, m_variants = 50, 2000
    cm = np.linspace(0.0, 100.0, m_variants)
    rng = np.random.default_rng(3)
    labels = np.arange(n_donors)[:, None].repeat(m_variants, axis=1).astype(np.uint8)
    switches = []
    for _ in range(30):
        haps, longest = m.mosaic(labels, cm, 1, 5.0, rng)
        switches.append(int((np.diff(haps[0].astype(int)) != 0).sum()))
        assert longest[0] <= 100.0 + 1e-9
    assert 15 < np.mean(switches) < 25                                # 100 cM at a mean of 5 cM


def test_longest_copied_stretch_is_the_whole_chromosome_without_breakpoints():
    donors, cm = panel()
    haps, longest = m.mosaic(donors, cm, 4, 1e9, np.random.default_rng(4))
    for h, length in zip(haps, longest):
        assert any((h == d).all() for d in donors)
        assert close(length, 60.0, 1e-9)


def test_capped_segments_never_copy_more_than_the_limit_from_one_donor():
    rng = np.random.default_rng(14)
    donors = hwe_population(500, 3000, rng)
    cm = np.linspace(0, 300, 3000)
    _, uncapped = m.mosaic(donors, cm, 50, 3.0, rng)
    _, capped = m.mosaic(donors, cm, 50, 3.0, rng, max_cm=10.0)
    assert uncapped.max() > 10.0
    assert capped.max() <= 10.0 + 1e-9
    assert m.donor_sequence(1000, 2, rng).tolist()[:3] in ([0, 1, 0], [1, 0, 1])


def test_a_forced_segment_carries_the_requested_allele_and_the_local_ld_of_the_donors():
    """Columns 300 and 301 are identical in every donor (perfect LD). Forcing an allele at 300 gives the same
    allele at 301 whenever no breakpoint falls between them, because the segment comes from one donor."""
    donors, cm = panel(n_donors=60)
    donors[:, 301] = donors[:, 300]
    rng = np.random.default_rng(15)
    want = rng.integers(0, 2, size=(200, 1)).astype(np.int8)
    want[:20] = -1                                                    # no constraint for the first 20
    haps, _ = m.mosaic(donors, cm, 200, 3.0, rng, 10.0, np.array([300]), want)
    assert (haps[20:, 300] == want[20:, 0]).all()
    assert (haps[:, 301] == haps[:, 300]).mean() > 0.95
    for h in haps[:50]:
        assert all(h[v] in donors[:, v] for v in range(donors.shape[1]))


def test_a_forced_allele_absent_from_the_pool_is_left_alone():
    donors, cm = panel()
    donors[:, 100] = 0
    haps, _ = m.mosaic(donors, cm, 10, 3.0, np.random.default_rng(16), None, np.array([100]),
                       np.ones((10, 1), dtype=np.int8))
    assert (haps[:, 100] == 0).all()


def test_meiosis_takes_each_allele_from_one_of_the_two_parental_haplotypes():
    donors, cm = panel()
    rng = np.random.default_rng(5)
    a, b = donors[0], donors[1]
    for _ in range(20):
        g = m.meiosis(a, b, cm, rng)
        assert all(g[v] in (a[v], b[v]) for v in range(len(g)))
    assert m.meiosis(a[:1], b[:1], cm[:1], rng)[0] in (a[0], b[0])


def test_allele_errors_flip_about_the_requested_share():
    haps = np.zeros((100, 10_000), dtype=np.uint8)
    flipped = m.add_allele_errors(haps, 0.001, np.random.default_rng(6))
    assert flipped == int(haps.sum()) and 700 < flipped < 1300


# --- people ------------------------------------------------------------------------------------------------

def test_cases_carry_the_risk_allele_at_the_tilted_frequency_and_controls_at_the_pool_frequency():
    rng = np.random.default_rng(20)
    donors = hwe_population(150, 400, rng)
    donors[:, 200] = rng.random(300) < 0.30
    cm = np.linspace(0, 40, 400)
    people = [Person("N", 1, status=2) for _ in range(1500)] + [Person("N", 2, status=1) for _ in range(1500)]
    locus = {"col": 200, "risk": 1, "or": 1.8}
    h1, h2, _ = m.simulate_autosome(people, {"N": donors}, cm, rng, 3.0, 10.0, locus)
    f0 = donors[:, 200].mean()
    cases = (h1[:1500, 200].mean() + h2[:1500, 200].mean()) / 2
    controls = (h1[1500:, 200].mean() + h2[1500:, 200].mean()) / 2
    assert close(cases, m.tilted_frequency(f0, 1.8), 0.03) and close(controls, f0, 0.03)
    odds = (cases / (1 - cases)) / (controls / (1 - controls))
    assert 1.5 < odds < 2.15
    assert close(m.tilted_frequency(0.3, 1.0), 0.3, 1e-12)


def test_relatives_made_by_meiosis_have_the_expected_kinship():
    rng = np.random.default_rng(21)
    donors = hwe_population(300, 6000, rng)
    cm = np.linspace(0, 600, 6000)
    people = [Person("N", 2), Person("N", 1), Person("N", 1, mother=0, father=1), Person("N", 2, mother=0, father=1),
              Person("N", 1), Person("ADM", 2)]
    pools = {"N": donors[:300], "AFR": donors[300:450], "EUR": donors[:300]}
    h1, h2, longest = m.simulate_autosome(people, pools, cm, rng, 3.0, 10.0)
    g = (h1 + h2).astype(np.int8)
    kin = m.king_kinship(g, g)
    assert close(kin[2, 0], 0.25, 0.04) and close(kin[2, 1], 0.25, 0.04)          # parent and child
    assert close(kin[2, 3], 0.25, 0.10)                                          # full siblings (wide spread)
    assert abs(kin[0, 1]) < m.THIRD_DEGREE and abs(kin[4, 0]) < m.THIRD_DEGREE   # unrelated founders
    assert longest[:2].max() <= 10.0 + 1e-9 and longest[2] == 0                  # only founders are mosaics


def test_the_share_copied_from_one_donor_is_about_2_over_h_and_below_the_cap():
    """H donor haplotypes (H/2 donor individuals) over a 3,000 cM genome: the share of a person's genome copied
    from one donor individual averages 2/H, and no share reaches the 3% cap. The labels follow meiosis, so a
    child's shares come from its parents' segments."""
    rng = np.random.default_rng(29)
    h, mv = 200, 6000
    donors = (rng.random((h, mv)) < 0.3).astype(np.uint8)
    cm = np.linspace(0, 3000, mv)
    people = [Person("N", 2) for _ in range(60)] + [Person("N", 1) for _ in range(60)] + [Person("N", 1, mother=0, father=60)]
    track = {"offset": {"N": 0}}
    m.simulate_autosome(people, {"N": donors}, cm, rng, 3.0, 10.0, None, track)
    weights = m.column_weights(cm)
    assert close(weights.sum(), 3000.0, 1e-6)
    copied = m.copied_cm(track["l1"], weights, h) + m.copied_cm(track["l2"], weights, h)
    assert np.allclose(copied.sum(axis=1), 6000.0)                      # two haplotypes x 3,000 cM
    share = m.donor_shares(copied, 3000.0, 2)                           # [person, donor individual]
    assert share.shape == (121, h // 2)
    assert close(share.mean(), 2 / h, 1e-9)                             # every cM comes from some donor
    assert close(float(np.median(share[:120])), 2 / h, 0.004) and share.max() < 0.03
    child = track["l1"][120]
    assert set(np.unique(child)) <= set(np.unique(np.concatenate([track["l1"][0], track["l2"][0]])))


def test_men_have_one_x_haplotype_and_a_daughter_carries_her_fathers_x():
    rng = np.random.default_rng(22)
    donors = hwe_population(100, 500, rng)
    cm = np.linspace(0, 50, 500)
    people = [Person("N", 2), Person("N", 1), Person("N", 2, mother=0, father=1), Person("N", 1, mother=0, father=1),
              Person("N", 1, two_x=True)]
    h1, h2, one = m.simulate_x(people, {"N": donors}, cm, rng)
    assert one.tolist() == [False, True, False, True, False]
    assert (h1[1] == h2[1]).all() and (h1[3] == h2[3]).all()                     # men: written as homozygous
    assert (h2[2] == h1[1]).all()                                                # daughter: the father's X
    assert all(h1[3][v] in (h1[0][v], h2[0][v]) for v in range(500))             # son: from the mother only
    assert (h1[4] != h2[4]).any()                                                # the XXY profile has two
    wells = m.well_genotypes(h1, h2, np.array([1, 0]), 0.0, rng, one)
    assert set(np.unique(wells[:, 0])) <= {0, 2} and 1 in wells[:, 1]


def test_two_wells_of_one_person_differ_only_by_the_allele_errors():
    rng = np.random.default_rng(23)
    haps = hwe_population(3, 20_000, rng)
    w = m.well_genotypes(haps[0::2], haps[1::2], np.array([0, 0, 1]), 0.0005, rng)
    assert w.shape == (20_000, 3)
    discordance = (w[:, 0] != w[:, 1]).mean()
    assert 0.0005 < discordance < 0.004 and (w[:, 0] != w[:, 2]).mean() > 0.3


# --- KING kinship: the copy check -------------------------------------------------------------------------

def test_king_kinship_of_unrelated_identical_and_parent_offspring():
    rng = np.random.default_rng(7)
    haps = hwe_population(40, 5000, rng)
    cm = np.linspace(0, 200, 5000)
    g = genotypes(haps)
    kin = m.king_kinship(g, g)
    off_diagonal = kin[~np.eye(len(g), dtype=bool)]
    assert abs(np.median(off_diagonal)) < 0.02 and off_diagonal.max() < m.THIRD_DEGREE
    assert np.allclose(np.diag(kin), 0.5)
    child = m.meiosis(haps[0], haps[1], cm, rng).astype(np.int8) + m.meiosis(haps[2], haps[3], cm, rng)
    with_parent = m.king_kinship(child[None, :], g[:2])[0]
    assert close(with_parent[0], 0.25, 0.03) and close(with_parent[1], 0.25, 0.03)


def test_a_mosaic_is_not_a_copy_of_any_donor():
    """The copy check of the build, with a donor pool of the real size (about 210 haplotypes per group)."""
    rng = np.random.default_rng(8)
    donors = hwe_population(105, 8000, rng)
    cm = np.linspace(0, 600, 8000)
    haps, longest = m.mosaic(donors, cm, 80, 3.0, rng, 10.0)
    kin = m.king_kinship(genotypes(haps), genotypes(donors))
    assert kin.max() < m.THIRD_DEGREE and longest.max() <= 10.0 + 1e-9
    among = m.king_kinship(genotypes(haps), genotypes(haps))
    np.fill_diagonal(among, 0)
    assert among.max() < m.THIRD_DEGREE


def test_missing_genotypes_are_left_out_of_kinship():
    rng = np.random.default_rng(9)
    g = genotypes(hwe_population(10, 3000, rng))
    damaged = g.copy()
    damaged[0, :1500] = -1
    assert close(m.king_kinship(damaged[:1], g[:1])[0, 0], 0.5, 1e-6)


# --- planting ----------------------------------------------------------------------------------------------

def test_sample_and_variant_missingness_hit_the_planted_shares():
    rng = np.random.default_rng(10)
    g = np.ones((20_000, 50), dtype=np.int8)
    shares = m.plant_sample_missingness(g, [3, 7], rng)
    for s, share in shares.items():
        assert close((g[:, s] == -1).mean(), share, 0.01) and 0.04 <= share <= 0.08
    assert (g[:, 0] == -1).sum() == 0
    weights = np.ones(20_000)
    weights[:5000] = 0
    exact = m.plant_sample_missingness(g, [9], rng, 0.02, 0.02, weights, exact=True)
    assert (g[:5000, 9] == -1).sum() == 0 and (g[:, 9] == -1).sum() == round(0.02 * 15_000) and exact[9] == 0.02
    g = np.ones((10, 20_000), dtype=np.int8)
    shares = m.plant_variant_missingness(g, [2], rng)
    assert close((g[2] == -1).mean(), shares[2], 0.01)
    shares = m.plant_variant_missingness(g, [4], rng, 0.05, 0.05, exact=True)
    assert (g[4] == -1).sum() == 1000


def test_differential_missingness_is_exact_in_cases_and_controls():
    rng = np.random.default_rng(17)
    g = genotypes(hwe_population(2000, 3, rng)).T.copy()
    cases = np.arange(2000) < 1000
    done = m.plant_differential_missingness(g, 1, cases, ~cases, rng)
    assert done == (32, 2)
    assert (g[1, cases] == -1).sum() == 32 and (g[1, ~cases] == -1).sum() == 2 and (g[0] == -1).sum() == 0


def test_hwe_failure_lowers_heterozygosity_and_fails_the_test():
    rng = np.random.default_rng(11)
    g = genotypes(hwe_population(2000, 1, rng)).T.copy()
    half = np.arange(2000) % 2 == 0
    before = g[0, ~half].copy()
    changed = m.plant_hwe_failure(g, 0, half, rng, 0.6)
    assert changed > 0 and (g[0, ~half] == before).all()
    assert m.hwe_chi2_p(g[0, half]) < 1e-6 and m.hwe_chi2_p(g[0, ~half]) > 1e-4


def test_a_faulty_plate_loses_heterozygotes_only_in_its_wells():
    rng = np.random.default_rng(18)
    g = genotypes(hwe_population(200, 5000, rng)).T.copy()
    before = g.copy()
    plate = np.arange(96)
    share = m.plant_het_loss(g, plate, rng, 0.07)
    assert (g[:, 96:] == before[:, 96:]).all()
    lost = ((before[:, :96] == 1) & (g[:, :96] != 1)).sum() / (before[:, :96] == 1).sum()
    assert close(lost, 0.07, 0.01) and 0.01 < share < 0.05
    assert ((before[:, :96] != 1) == (g[:, :96] != 1))[before[:, :96] != 1].all()   # homozygotes untouched


def test_contamination_adds_heterozygous_calls_in_proportion_to_the_share():
    rng = np.random.default_rng(19)
    g = genotypes(hwe_population(2, 50_000, rng))
    light = m.contaminate(g[0], g[1], 0.10, rng)
    heavy = m.contaminate(g[0], g[1], 0.25, rng)
    het = lambda x: (x == 1).sum() / (x >= 0).sum()                    # noqa: E731
    assert het(g[0]) < het(light) < het(heavy)
    assert (light == -1).mean() < 0.02 and (heavy[g[0] == g[1]] == g[0][g[0] == g[1]]).all()


def test_allele_checks_tell_same_flip_mismatch_and_palindromic_apart():
    assert m.allele_check("A", "G", "G", "A") == "same"
    assert m.allele_check("T", "C", "A", "G") == "flip"
    assert m.allele_check("A", "T", "A", "T") == "palindromic" and m.is_palindromic("C", "G")
    for ref, alt in (("A", "G"), ("A", "C"), ("G", "T"), ("C", "T"), ("T", "G")):
        bad = m.incompatible_alleles(ref, alt)
        assert m.allele_check(bad[0], bad[1], ref, alt) == "mismatch" and not m.is_palindromic(*bad)
        assert m.allele_check(*m.complement_alleles(ref, alt), ref, alt) == "flip"


# --- plates ------------------------------------------------------------------------------------------------

def test_plates_are_full_the_bad_plate_is_plain_and_replicates_sit_on_another_plate():
    rng = np.random.default_rng(24)
    n = 21 * 96
    special = np.zeros(n, dtype=bool)
    special[rng.choice(n, 300, replace=False)] = True
    replicate_of = np.full(n, -1)
    replicates = np.flatnonzero(special)[:16]
    replicate_of[replicates] = np.flatnonzero(special)[16:32]
    plate, position = m.assign_plates(n, special, replicate_of, rng)
    assert all((plate == p).sum() == 96 for p in range(1, 22))
    assert not special[plate == 14].any()
    assert all(plate[r] != plate[replicate_of[r]] for r in replicates)
    assert all(sorted(position[plate == p]) == list(range(96)) for p in range(1, 22))
    assert m.well_label(0) == "A01" and m.well_label(11) == "A12" and m.well_label(12) == "B01" and m.well_label(95) == "H12"


# --- reading and writing ---------------------------------------------------------------------------------

def test_bed_rows_survive_a_round_trip_and_follow_the_plink_coding():
    rng = np.random.default_rng(13)
    g = rng.integers(-1, 3, size=(7, 11)).astype(np.int8)              # 11 samples: the last byte is padded
    body = m.pack_bed_rows(g)
    assert len(body) == 7 * 3 and (m.unpack_bed_rows(body, 11) == g).all()
    one = m.pack_bed_rows(np.array([[2, 1, 0, -1]], dtype=np.int8))    # 00, 10, 11, 01 from the low bits
    assert one == bytes([0b01111000])
    with tempfile.TemporaryDirectory() as d:
        m.write_bed(str(Path(d) / "t.bed"), g)
        raw = (Path(d) / "t.bed").read_bytes()
        assert raw[:3] == bytes([0x6C, 0x1B, 0x01]) and raw[3:] == body


def test_haps_files_are_read_with_the_missing_second_haplotype_of_men_on_chrx():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "x.haps").write_text("X X:10:A:G 10 A G 1 - 0 1\nX X:20:C:T 20 T C 0 - 1 1\n", encoding="ascii")
        (Path(d) / "x.sample").write_text("ID_1 ID_2 missing sex\n0 0 0 D\n0 MAN 0 1\n0 WOMAN 0 2\n", encoding="ascii")
        rows, samples, haps = m.read_haps(str(Path(d) / "x"))
    assert samples == ["MAN", "WOMAN"] and rows[1] == ("X", "X:20:C:T", 20, "T", "C")
    assert haps.tolist() == [[1, 0], [m.NO_HAP, m.NO_HAP], [0, 1], [1, 1]]


def test_the_final_report_has_the_agreed_layout():
    g = np.array([0, 1, 2, -1], dtype=np.int8)
    text = m.final_report("SIM26_0001", ["rs1", "1:500", "rs3_ilmndup1", "rs4"], list("AGCT"), list("GATC"), g,
                          np.array([0.91234, 0.8, 0.7561, 0.0]), "SimArray_simulated.bpm", 96, 7)
    lines = text.decode("ascii").split("\r\n")
    assert lines[:10] == ["[Header]", "GSGT Version;2.0.4", "Processing Date;11/11/2026 10:30 AM",
                          "Content;;SimArray_simulated.bpm", "Num SNPs;4", "Total SNPs;4", "Num Samples;96",
                          "Total Samples;96", "File ;7 of 96", "[Data]"]
    assert lines[10] == "SNP Name;Sample ID;GC Score;Allele1 - Plus;Allele2 - Plus"
    assert lines[11:15] == ["rs1;SIM26_0001;0.9123;A;A", "1:500;SIM26_0001;0.8000;A;G",
                            "rs3_ilmndup1;SIM26_0001;0.7561;T;T", "rs4;SIM26_0001;0.0000;-;-"]
    assert lines[15] == "" and b"\n" not in text.replace(b"\r\n", b"")
    scores = m.gc_scores(g, np.random.default_rng(1))
    assert scores[3] == 0 and (scores[:3] > 0.15).all() and (scores <= 0.99).all()
    assert m.genotype_letters(g, "G", "A") == [("A", "A"), ("A", "G"), ("G", "G"), ("0", "0")]


def test_imputed_dosages_are_close_to_the_truth_when_quality_is_high():
    rng = np.random.default_rng(25)
    haps = hwe_population(1500, 2, rng)
    dose = m.simulate_hap_dosages(haps, np.array([0.95, 0.20]), rng)
    r2 = m.minimac_r2(dose)
    truth = [np.corrcoef(dose[:, j], haps[:, j])[0, 1] ** 2 for j in (0, 1)]
    assert r2[0] > 0.85 > 0.5 > r2[1] and truth[0] > truth[1] and (dose >= 0).all() and (dose <= 1).all()
    fields = m.dosage_fields(np.array([1.0, 0.2]), np.array([0.0, 0.1]))
    assert fields[0] == "1|0:1.000:0.000,1.000,0.000" and fields[1].startswith("0|0:0.300:0.720,0.260,0.020")


def test_the_reported_rsq_matches_the_true_r2_with_the_real_genotypes():
    """Minimac R-square of the simulated dosages against the squared correlation between the dosage (DS) and
    the true genotype, over variants of different frequency and quality: median difference below 0.05."""
    rng = np.random.default_rng(28)
    n, mv = 1500, 300
    freq = rng.uniform(0.02, 0.5, mv)
    haps = (rng.random((2 * n, mv)) < freq).astype(np.uint8)
    target = rng.uniform(0.2, 0.99, mv)
    dose = m.simulate_hap_dosages(haps, target, rng)
    rsq = m.minimac_r2(dose)
    ds = dose[:n] + dose[n:]
    truth = (haps[:n] + haps[n:]).astype(float)
    true_r2 = np.array([np.corrcoef(ds[:, j], truth[:, j])[0, 1] ** 2 for j in range(mv)])
    assert np.median(np.abs(rsq - true_r2)) < 0.05
    assert np.median(np.abs(rsq - target)) < 0.05 and len(np.unique(dose[:, 0])) > 10


def test_the_chain_lifts_forward_and_back_and_reports_gaps():
    """Two chains: a forward one with a 10-base gap in the source, and one on the reverse strand of another
    contig."""
    text = ["chain 1000 chrA 1000 + 100 400 chrA 1200 + 150 460 1", "100 10 20", "190", "",
            "chain 500 chrA 1000 + 500 600 chrB 300 - 50 150 2", "100", ""]
    chain = m.Chain.from_lines(text)
    names, pos = chain.lift("chrA", np.array([101, 200, 205, 211, 400, 401, 501, 600, 900]))
    assert pos.tolist() == [151, 250, -1, 271, 460, -1, 250, 151, -1]
    assert names.tolist() == ["chrA", "chrA", "", "chrA", "chrA", "", "chrB", "chrB", ""]
    back = chain.inverted()
    names, pos = back.lift("chrA", np.array([151, 250, 271, 460, 251]))
    assert pos.tolist() == [101, 200, 211, 400, -1] and names[0] == "chrA"
    names, pos = back.lift("chrB", np.array([250, 151, 149]))
    assert pos.tolist() == [501, 600, -1] and names.tolist() == ["chrA", "chrA", ""]
    assert chain.lift("chrZ", np.array([5]))[1].tolist() == [-1]


# --- loci and statistics -----------------------------------------------------------------------------------

def test_the_locus_search_picks_the_variant_with_most_array_neighbours_and_a_tag_for_an_off_array_one():
    rng = np.random.default_rng(26)
    n, mv = 400, 300
    haps = (rng.random((n, mv)) < 0.5).astype(np.uint8)
    pos = np.arange(mv) * 1000
    core = (rng.random(n) < 0.30).astype(np.uint8)
    noisy = lambda rate: np.where(rng.random(n) < rate, 1 - core, core)      # noqa: E731
    for v in range(100, 130):
        haps[:, v] = noisy(0.03)                                        # an LD block around variant 100
    haps[:, 200] = core
    haps[:, 201] = noisy(0.03)                                          # a second candidate with one neighbour
    on_array = np.zeros(mv, dtype=bool)
    on_array[100:130:2] = True
    on_array[[200, 201]] = True
    allowed = np.ones(mv, dtype=bool)
    half = np.arange(n) < n // 2
    hit = m.find_locus(haps, pos, on_array, allowed, np.flatnonzero(half), np.flatnonzero(~half), 0.30, True,
                       freq_tol=0.05, ns_max=0.1, min_dense=5)
    assert hit is not None and 100 <= hit["col"] < 130 and on_array[hit["col"]] and hit["array_neighbours"] >= 10
    assert close(hit["risk_freq"], 0.30, 0.05) and hit["risk"] == 1
    haps[:, 121] = noisy(0.055)                                         # off-array, r2 about 0.8 with the block
    on_array[:] = False
    on_array[100] = True
    for v in range(101, 130):
        if v != 121:
            haps[:, v] = haps[:, 100]
    off = m.find_locus(haps, pos, on_array, allowed, np.flatnonzero(half), np.flatnonzero(~half), 0.30, False,
                       freq_tol=0.06, ns_max=0.15, min_dense=5)
    assert off is not None and not on_array[off["col"]] and off["tag"][0] == 100 and 0.75 <= off["tag"][1] <= 0.85


def test_lambda_is_one_for_uniform_p_values_and_larger_for_inflated_ones():
    rng = np.random.default_rng(27)
    z = rng.standard_normal(200_000)
    p = np.array([math.erfc(abs(x) / math.sqrt(2)) for x in z])
    assert close(m.lambda_gc(p), 1.0, 0.02)
    p_inflated = np.array([math.erfc(abs(x) * math.sqrt(1.6) / math.sqrt(2)) for x in z])
    assert close(m.lambda_gc(p_inflated), 1.6, 0.04)


# --- the study roster --------------------------------------------------------------------------------------

def test_the_roster_has_the_planned_numbers_and_every_problem_on_its_own_subjects():
    r = gen.make_roster(np.random.default_rng([20261111, 2]))
    assert len(r.subjects) == 2000 and len(r.wells) == 2016 and len(r.grch37_people) == 120
    assert sum(s.status == 2 for s in r.subjects) == 1000
    european = [(s.status, r.people[s.person].pool) for s in r.subjects if r.people[s.person].pool in ("N", "S")]
    assert {k: european.count(k) for k in gen.QUOTA} == gen.QUOTA
    outliers = [s for s in r.subjects if "outlier" in s.tags]
    assert len(outliers) == 40 and sum(s.status == 2 for s in outliers) == 30
    count = lambda tag: sum(tag in s.tags for s in r.subjects)          # noqa: E731
    assert [count(t) for t in ("failed", "low_call_rate", "plate14", "plate14_low", "contaminated", "consanguineous",
                               "replicate_original", "sex_xxy")] == [3, 22, 96, 20, 6, 5, 16, 1]
    problems = ("failed", "low_call_rate", "plate14", "contaminated", "consanguineous", "replicate_original",
                "outlier", "relative", "duplicate_coherent", "duplicate_discordant", "sex_xxy",
                "sex_declared_female_genetic_male", "sex_declared_male_genetic_female")
    assert all(sum(t in s.tags for t in problems) <= 1 for s in r.subjects)
    for i, p in enumerate(r.people):                                    # parents come first, one of each sex
        if not p.founder:
            assert p.mother < i and p.father < i and r.people[p.mother].sex == 2 and r.people[p.father].sex == 1
    ids = [w["sample_id"] for w in r.wells]
    assert len(set(ids)) == 2016 and sum(i.endswith("_R2") for i in ids) == 16
    by_id = {w["sample_id"]: w for w in r.wells}
    assert all(w["plate"] != by_id[w["replicate_of"]]["plate"] for w in r.wells if w["replicate_of"])
    assert all(not (set(r.subjects[w["subject"]].tags) - {"plate14", "plate14_low"}) for w in r.wells if w["plate"] == 14)
    kinds = [k for k, _, _ in r.pairs]
    assert kinds.count("parent-offspring") == 6 and kinds.count("full-siblings") == 4
    assert kinds.count("duplicate-coherent") == 2 and kinds.count("duplicate-discordant") == 1
    for kind, a, b in r.pairs:
        if kind.startswith("duplicate"):
            assert r.subjects[a].person == r.subjects[b].person and r.subjects[a].sex == r.subjects[b].sex
            assert (r.subjects[a].status == r.subjects[b].status) == (kind == "duplicate-coherent")
    males = np.mean([s.sex == 1 for s in r.subjects])
    assert 0.49 < males < 0.55


def test_the_expected_sample_flow_ends_at_1811():
    flow = gen.expected_flow(gen.make_roster(np.random.default_rng([20261111, 2])))
    assert [flow["counts"][s]["removed"] for s in ("3.1", "3.2", "3.3", "3.5", "3.6", "3.7", "5.6")] == [3, 42, 8, 13, 30, 76, 33]
    assert flow["start"] == 2016 and flow["final"] == 1811
    everything = [i for ids in flow["removed"].values() for i in ids]
    assert len(everything) == len(set(everything))


def test_the_roster_is_the_same_for_the_same_seed():
    a = gen.make_roster(np.random.default_rng([1, 2]))
    b = gen.make_roster(np.random.default_rng([1, 2]))
    assert [w["sample_id"] for w in a.wells] == [w["sample_id"] for w in b.wells]
    assert [(s.status, s.sex, s.age, s.tags) for s in a.subjects] == [(s.status, s.sex, s.age, s.tags) for s in b.subjects]


# --- safety ------------------------------------------------------------------------------------------------

def test_no_student_folder_can_hold_the_answer_key():
    for name in gen.STUDENT_DIRS:
        assert not any(word in name.lower() for word in ("answer", "instructor", "build_record", "seed", "truth"))


def test_the_generator_refuses_an_output_folder_inside_the_repository():
    argv = sys.argv
    sys.argv = ["make_sim2026.py", "--out", str(gen.REPO / "sim_out")]
    try:
        gen.main()
    except SystemExit as stop:
        assert "outside the repository" in str(stop)
    else:
        raise AssertionError("the generator accepted an output folder inside the repository")
    finally:
        sys.argv = argv
    assert not (gen.REPO / "sim_out").exists()


if __name__ == "__main__":
    tests = [(name, fn) for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"ok    {name}")
        except Exception as error:                                      # noqa: BLE001
            failed += 1
            print(f"FAIL  {name}: {type(error).__name__}: {error}")
    print(f"{len(tests) - failed} of {len(tests)} tests passed")
    sys.exit(1 if failed else 0)
