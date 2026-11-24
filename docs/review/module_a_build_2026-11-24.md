# Module A build, 24 November 2026

Goal: module A (imputation) ready to publish, in preview only. Code, notebook, export and website.
Rules: one branch per repository, no merge, no release, no encryption, no push to `main`.

Course branch: `course/module-a-data`. Website branch: `course/module-a` (from an up-to-date `main`).

## Before phase 1: a conflict with the identity proof of phase 2

`course/module-a-data` descends from `course/2026.5`. Its lessons have 63 main-path steps: step 6.2 was removed
in 2026.5. The website holds the 2026.4 export: 64 steps, from commit `1e05565` of
`course/2026-guided-training` (`src/content/gwas/index.json`). A normal export from this branch therefore
writes the 2026.5 JSON for modules 0 to 7, which differ from the website JSON (checked: `step-3-2.json` and
`module-3.json` already differ in the committed `site_content/`). The required proof (JSON of modules 0 to 7
byte-identical to the 2026.4 JSON of the website) fails by construction, whatever module A does.

The rule for this case is: stop and document. Phase 1 does not depend on the export, so it goes ahead. Phase 2
prepares the lesson and the exporter, runs the proof, and stops there if the proof fails.

## Phase 1. Course code

### R helpers (`R/imputation.R`) and tests (`scripts/tests/test_imputation.R`)

New file `R/imputation.R`, sourced after `R/guided.R`. All PLINK calls go through `run_plink`.

- `prepare_imputation_input(cfg)`: one VCF per region from the state at 5.7. PLINK writes VCF 4.2 with bgzip,
  the `chr` prefix and IID as the sample name. The REF list (one file per region) holds the GRCh38 `Ref_Plus`
  of the array annotation. R checks that every REF equals that allele, removes the PR flag and its header
  line, and writes the file again as BGZF with plain line ends. Base R has no BGZF writer:
  `imputation_write_bgzf` compresses each block with R's gzip writer and replaces the gzip header with the
  BGZF header. `bgzip -t`, `tabix -p vcf` and `bcftools view` (htslib 1.25, WSL) accept the files.
- `read_imputation_info(path)`: R2, ER2, AF, MAF, TYPED and IMPUTED from the dosage VCF, as a data.frame.
- `compare_with_truth(dose, truth, panel)` and `imputation_quality_table()`: R2 against true r2 by frequency
  class, array sites left out (INFO flag `ARRAY`, also when bcftools has added AC and AN).
- `imputation_association(cfg, dose)` (the command of A.9 through `run_plink`) and `imputation_l4()`.

Checks on the real data (Windows 11, R 4.5.2, PLINK 2.0 b.1.4):

- **The data release matters.** The imputed output in `stage-module-a-2026.1` was made from the cohort of
  `data-2026.1` (course 2026.4). The cohort of `data-2026.2` (course 2026.5) has 4 different samples
  (relatives rule at 3.6): SIM26_0017, 0423, 0678, 1088 against 1264, 1291, 1329, 1636. So the checks
  below use `release-data-2026.1/payload` (checkpoint 5.7 as `s5-7_state`, `s6-3_covariates.tsv` as
  `s6-2_covariates.tsv`) in the new work folder `codex_work/module-a-build-20261124`. **Open:** module A
  with the 2026.5 course needs its imputed output made again from the 2026.2 cohort.
- `prepare_imputation_input`: 161 sites on chr18 and 277 on chr22, 1,811 samples; PLINK wrote 168 and 284
  CRLF lines and 161 and 277 PR flags, all removed. Against the target of the night
  (`module_a_work/target/full`): samples, sites, REF and ALT, INFO and every genotype identical. Only the
  `##fileDate` line differs (23 and 24 November).
- `read_imputation_info` (chr22, 60,224 variants, 10 seconds): 277 typed sites, median ER2 0.586.
- `compare_with_truth` (chr22, about 75 seconds): the table of draft section A.8, row by row (19,832
  variants; for example at least 5%: 7,826, median R2 0.79, median true r2 0.70; all: 0.62 and 0.35). Against
  `per_variant_chr22.tsv` of the night: same 19,832 variants, same R2, true r2 within 5e-7.
- `imputation_association` (chr18): 8,334 variants tested. L4 `chr18:38042715:G:A`: MACH r2 0.946, OR 1.47,
  p 1.65e-6. Best of the region `chr18:38106879:G:C`: OR 1.54, p 4.19e-8. Same as the night.

`scripts/tests/test_imputation.R` (synthetic data, PLINK in `bin/`): BGZF blocks and EOF, REF check and swap,
PR and CRLF removal, the error for a REF that matches neither allele, INFO reading, true r2 and classes, the
`ARRAY` flag with AC and AN, a missing sample, association with the R2 filter, and the L4 table. Passed.
