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
