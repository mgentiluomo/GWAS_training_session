# Proposals for future content

Written for the course author. These two items are not built. Each one needs new data or a change of the generator, so each needs your decision first.

## 1. Survival analysis (Kaplan-Meier curves and Cox regression)

Proposal. Add an optional module that follows the cases over time. Students would draw Kaplan-Meier curves for carriers and non-carriers of a lead variant. They would then fit a Cox proportional hazards model and compare its hazard ratio with the odds ratio of module 6. The module would explain censoring (people who have not yet had the event), the hazard, the proportional hazards assumption and why a time-to-event outcome needs a different model from a case-control outcome.

Data needed. The current simulated dataset has a binary disease status only. It has no event time and no follow-up time. The generator (`scripts/author/make_sim2026.py` and `scripts/author/sim2026_core.py`) would need a new phenotype: an event time for the cases (for example age at diagnosis or time from enrolment to progression), a follow-up time with censoring for everyone, and a planted genetic effect on the hazard at one of the three known loci. The new file would be a new column set in `phenotypes/sim2026_phenotypes.tsv` or a separate file. The genotypes, the QC problems and every number of the main path would stay the same, so the main path is not affected. A new data release is needed, because the phenotype file changes.

Estimate of work. About 3 to 4 working days. About 1 day for the generator and its tests (event times from a Weibull model with a hazard ratio for the lead variant, independent censoring, a check that the Cox estimate recovers the planted hazard ratio). About 2 days for the lessons (four to five steps, the glossary entries, the quick checks and the expected results). About 1 day for the notebooks, the site pages and the checks. The R survival package (`survival`) is a recommended package that ships with R, so no new installation is needed.

Risks. (1) A time-to-event outcome in a cohort that was designed as case-control is artificial, because cases and controls are sampled by status. The text must say so. (2) Students may read a hazard ratio as an odds ratio. The module must compare them in a table. (3) The data release must be rebuilt and encrypted again. (4) The extra material makes the course longer, so it should stay optional (module C), like the imputation and REGENIE modules.

## 2. A second dataset to repeat the path without checkpoints

Request. Daniele asked for a second dataset so that students can run the whole path again by themselves, without the restart checkpoints and without the expected numbers.

Proposal. Generate a second simulated study with another seed, a different set of planted problems and a different number of samples. Give students only the raw files (array export, sample sheet and phenotypes). The instructor key stays private. Students then repeat the path from module 2 to module 7 on their own and write the report of step 7.8 for the new data. Their numbers are checked against the key by the instructor, or by an optional `check_report()` function that compares a few counts without revealing the others.

What to change in the generator. The seed and the sample size (for example 1,200 people and 120,000 variants, to keep run time and the download small). The planted problems: move them (different plates, different samples, a different set of strand errors), change their sizes, and add one problem that the first dataset does not have (for example a sample swap, a batch with a different call rate pattern, or a different pair of relatives). Use different locations for the true loci so that answers cannot be copied. The scripts that write the keys and the build report must write a second file set (`answer_key_second.json`, `build_report_second.md`). The staging script would write a second folder. No checkpoint is needed.

Estimate of work. About 4 to 5 working days. About 1 day to parameterise the generator and its checks, so that a second build does not copy the first. About 1 day to run the full path on the new data, as the instructor, and to write the key. About 1 day for a short guide (what to do, how to report, how to check). About 1 day for the packaging (a second encrypted archive, a second SHA-256, the release and the access form). About 1 day for tests by a student who has not seen the first dataset.

Risks. (1) A second password and a second release to maintain each year. (2) The first dataset has fixed counts in the lessons. The second one must not appear in the lesson text, or students could look up the answers. (3) If a planted problem is too hard to find without the lessons, students get stuck, so the problems should be findable with the checks that the course teaches. (4) The generator could drift between the two builds, so a test must check that the first dataset still builds byte for byte.
