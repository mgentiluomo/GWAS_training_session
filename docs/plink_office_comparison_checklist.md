# PLINK comparison (status)

Status: **the office confirmation and the Apple Silicon check are done and passed.** The numbers on the Apple Silicon Mac are the same as on Windows. Two things in the course must be corrected. macOS Intel and Linux are still open.

The current release is `project-2026.3.1`. See `docs/review/plink_office_confirmation.md`, `docs/review/plink_apple_silicon_check.md` and `docs/review/student_fields_review.md`.

## Apple Silicon check: done

| Item | Value |
| --- | --- |
| Date | 16 November 2026 |
| Hardware | Mac14,2, Apple M2, macOS 27.0.1 |
| Software | R 4.4.0 (native arm64), RStudio 2024.09.1, PLINK `v2.0.0-b.1.4 M1 (7 Nov 2026)` from the package |
| `bin/plink2` SHA-256 | `e6d321565e2a4fd20874a7c21ac6c2cfe3e0802549bdffdfbe9623438cd6bf4a`, equal to `releases.tsv` |
| Result | **Passes.** Counts at all 22 steps, the final cohort (1,811 samples, 238,513 variants, 236,815 tests), lambda 1.016 (1.016465), 8 hits and 3 clumps are the same as on Windows. P-values and PCs are the same, except the last digit of `beta` in 1,484 rows of `s6-8_gwas_summary_statistics.tsv` (at most 1.1e-15). |
| Runs | `run_main_path.R` in 117 s. Restore 2.8, then modules 3 to 7, in 112 s. Both exit code 0. |
| Quarantine | `xattr` was not needed. The ZIP was downloaded with `curl` and had no quarantine flag. A ZIP downloaded with a browser was not tested. |

## To correct (not done yet)

1. **Version line in `prepare_course_plink()`.** It expects `64-bit` and fails on the macOS arm64 build, which prints `M1`. The Linux build prints `LM 64-bit Intel`. Keep the exact line of each build in `releases.tsv`. The error message must not advise `xattr` when the program runs. Details in `docs/review/plink_apple_silicon_check.md`.
2. **Restart from checkpoints.** `restore_checkpoint()` does not write `checkpoints/index.tsv` and `step_counts.tsv`. Restarts at modules 5, 6 and 7 fail. Restarts at modules 3 and 4 work. The right id for the 2.8 baseline is `restore_checkpoint("3.1")`, not `"2.8"`. The checklist step "modules 3 and 5 to 7" needs module 4 too until the restore is fixed.
3. **Hash checks against the shipped files.** `check_step()` and `where_am_i()` with the default `data_dir` compare SHA-256 and report "different contents" on Mac and Linux, because the shipped files have CRLF line endings. `s6-8_gwas_summary_statistics.tsv` also differs in the last digit of `beta`.

## Still open

- Test the provisioning and the preflight on Intel macOS and on Linux before you announce four-platform support.
- Run the same restart test (2.8, 3.8, 4.6, 5.7, 6.8) after the correction.

If a count, lambda, hit or clump differs on a platform, stop and do not change an expected result. PLINK must then leave the package and a new project release is needed.
