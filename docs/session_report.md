# Main-path authoring session, 12 November 2026

## Scope and decisions

Modules 0 to 7 only. Modules A and B and post-GWAS work are excluded.
Student code and notebooks are committed; data, instructor keys, passwords and
generated analytical outputs remain outside the repository. The authorised
working area is `C:/WEB_site/data_sources/codex_work/`.

- PLINK runs from the project root with relative paths. Windows short paths
  provide an ASCII fallback for non-ASCII directory components. No system
  locale settings are changed.
- Full genotype checkpoints belong at module boundaries. Intermediate restart
  states are reconstructed from stored removal lists and checked against counts.
- The local stage 1 ZIP remains a test archive. It will not be silently replaced;
  the classroom release needs new configured URLs and checksums.
- Expected QC values distinguish observed reference-run counts from planted
  expectations. The observed extra HWE and missingness failures are retained.

## Windows verification

- Unicode regression: PLINK completed its frequency probe in `café_α_中文`.
  Only ASCII relative paths reached PLINK. The caller's working directory was restored.
- Module 0: all executable preparation chunks and fixed block order passed on
  Windows with R 4.5.2 and PLINK 2 b.1.4. The original input was checked as
  2,016 wells and 299,523 variants. Password prompts and installer clicks remain
  manual checks; no real URL download was attempted.

## Work in progress

Module authoring and boundary checkpoint validation are continuing. Completed
modules and unresolved checks will be recorded below before the final push.

- Module 1: seven steps executed on Windows; annotation rows, 21 plates,
  2,016 wells and the three supplied report excerpts were checked. No genotype
  changes are made in this module. Laboratory steps have no PLINK equivalent;
  they are explicitly labelled rather than given a misleading command.

- Module 2: executed on Windows and compared with the instructor reference.
  Strand correction flipped 400 sites and excluded 3,013; boundary 2.8 has
  2,016 wells and 296,510 variants. R lift-over mapped 9,970/10,000 exercise sites
  on the same chromosome, including eight reverse-strand mappings. All 9,965
  shared annotation IDs were checked where mapped. The author-only chain path
  was supplied through COURSE_CHAIN_FILE; stage the official chain in the
  classroom package before publication. The isolated exercise is not position-sorted.

- Module 3: Windows execution matched all reference sample counts, ending at
  1,844 samples and 296,360 variants. Pruning retained 69,539 sites; 13 low-F
  samples, 30 duplicate/related records and 76 remaining P14 wells were removed.
  Eight high-F samples were flagged and retained. One failed first attempt
  exposed scientific notation in interval coordinates; explicit integer formatting
  fixed it, and the full module passed on the next attempt.

- Module 4: Windows execution matched the reference counts, ending at
  1,844 samples and 238,513 variants. HWE removed 167 sites, including the
  three named ancestry markers; chromosome review removed 33 sites and
  duplicate review another 306 entries. The sample-size-aware HWE policy is
  calibrated at 1,000 controls with a 10^(-6) mid-p cutoff and tightens for
  larger samples; at this dataset size it reproduces the reference rule.
  This teaching policy must not be presented as a universal research threshold.

- Module 5: Windows reference PCA/projection passed with 48,614 shared sites.
  After removing 33 projected outliers, the retained cohort has 1,811 samples
  and 238,513 variants. Ten within-cohort PCs and a scree plot were generated.
  A first attempt found a long PVAR metadata header; streaming over all header
  lines fixed the reader. The PCA figure was visually inspected and its legend
  was corrected to use the four groups actually present in the supplied subset.

- Module 6: Windows main scan produced 236,815 finite tests and eight genome-wide
  hits, with autosomal lambda 1.016465. The model includes age, sex and ten PCs.
  All main-scan FIRTH flags were N; a separate low-frequency retained autosomal
  site was deliberately analysed with forced Firth for teaching. A manifest
  protects the 6.7 analysis checkpoint.

- Module 7: Windows execution produced Manhattan, QQ, common-scale QQ comparison
  and L2 regional plots, three LD clumps, effect-allele lead tables and a final
  Markdown summary. Final cohort: 900 cases and 911 controls. The no-PC and
  no-sample/variant-QC contrasts reproduced 15 and 19 significant variants and
  lambda approximately 1.546 and 1.655. All main plots were visually inspected;
  the regional legend was changed to ASCII ranges for Windows font portability,
  and the comparison plots now share a vertical scale.

- Full main-path rerun: all eight notebooks executed in order in a fresh external
  folder and passed instructor key/reference comparisons, including sample
  removal identities (except the intentionally interchangeable relative-pair
  choice), leading association p-values and main-scan test counts.
- Recovery: seven restart targets (2.6, 3.2, 3.5, 4.5, 5.6, 6.4, 7.7) passed
  metadata identity, expected counts and zero PLINK genotype differences with
  missing calls included. Early source conversion and required diagnostic files
  are now replayed too; full genotype copies remain at the four boundaries only.
- Local release staging: 105 files, 634,410,035 bytes, under codex_work/classroom-stage-2026.1,
  with a separate SHA-256 manifest. It includes the official chain and excludes
  imputation material and instructor keys. The old 55-file test ZIP is unchanged.
