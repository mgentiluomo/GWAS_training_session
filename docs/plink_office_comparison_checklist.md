# PLINK comparison at the office (confirmation against the reference results)

Status: to do. Updated on 15 November 2026 for the author.

Release 2026.3 is published **with PLINK 2** (four non-AVX2 builds, Beta 1.4, 7 November 2026). On 15 November the Windows non-AVX2 build and the AVX2 validation build gave identical results on one PC (`docs/review/plink_home_comparison.md`). The office run is now a **confirmation against the reference files** `instructor/answer_key.json` and `instructor/build_report.md`, which are not on the PC used before. It runs the same build on another PC with the instructor files. Rules and pins are in `docs/plink_packaging_plan.md` and `third_party/plink2/`.

If the confirmation fails, do not republish silently. Write the difference in the review file and decide on a new project release (2026.3.1 or 2026.4) with a fix or without PLINK.

## What you need on the office PC

- The course data (the extracted `data-2026.1` payload) and the instructor files: `instructor/answer_key.json`, `instructor/build_report.md`, `checkpoints/index.tsv`.
- The project release 2026.3 ZIP (it contains the non-AVX2 builds). The AVX2 build is needed only if you also want to repeat the two-build comparison.
- R 4.5 or newer, the course packages, and the branch `plink/bundle`.

## Acceptance rules

| Quantity | Rule |
| --- | --- |
| Counts (samples, variants, removals, tests, hits, clumps) at every step | Exact match |
| Lambda | Equal to three decimals (1.016) |
| Top hits and clumps | Same variants, same clump membership |
| P-values, PCs, plot inputs | Report every difference and review it |

The run must fail if a reference file is missing. It must never skip silently.

## Commands (PowerShell, from the project root of a fresh clone of `plink/bundle`)

1. Download `GWAS_course-2026.3.zip` from the release `project-2026.3`, check the SHA-256 value (`9b0e9a7d8160d1c15fee52f4860f39c6669088a0a49866a1c274c4c8dcb264cd`) and extract it to `C:\GWAS_office`.
2. In R from `C:\GWAS_office\GWAS_course`: `source("R/plink_setup.R"); prepare_course_plink()`. It must use the build from the package and not download.
3. Check the answer: `bin\plink2.exe --version` must print `PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)`. Compare the executable hash with `third_party/plink2/releases.tsv` (row `windows-x86_64`).
4. Download and verify the data: `source("R/course.R"); download_course_data()` (the password is asked at the prompt).
5. `Rscript scripts/preflight.R`, then `Rscript scripts/check_course.R`.
6. `Rscript scripts/run_main_path.R` in an empty output folder.
7. Compare `step_counts.tsv`, every `guided_register` and `stopifnot` number, the lambda, the hits and the clumps with `instructor/answer_key.json` and `instructor/build_report.md` and with the table above. Save the comparison as a table in `docs/review/`.
8. Optional: repeat steps 2 to 6 with the AVX2 build in a second folder and compare the two runs, as in `docs/review/plink_home_comparison.md`.

## If something differs

1. Stop. Do not change an expected result.
2. Note the step, the quantity, both values and the build.
3. Check the PLINK Beta 1.4 changelog for `--glm`, `--pca`, `--het`, `--make-king-table`, `--split-par` and `--mind`.
4. A difference in counts, lambda, hits or clumps means: PLINK must leave the package. Prepare a new project release without it.
5. A difference only in p-values, PC signs or plot inputs needs your review before any text changes.

## If it all passes

Record the result in `docs/review/student_fields_review.md`. Nothing else changes: release 2026.3 already contains PLINK and the PLINK source of tag `v2.0.0-b.1.4` (commit `760ee7329e8914de52f75a4e470cecabccbde0d9`).

## Apple Silicon check (your Mac)

1. Extract the release ZIP `GWAS_course-2026.3.zip`. Run step 0.6 (`prepare_course_plink()` must choose `macos-arm64` from the package) and the preflight. Record the hardware, macOS, R, PLINK version and executable hash.
2. Restore the verified 2.8 baseline into a fresh output folder with `restore_checkpoint`.
3. Run modules 3 and 5 to 7. Module 3 alone cannot test PCA, logistic regression or clumping.
4. Compare with the Windows run under the rules above.
5. If `bin/plink2` is blocked, run `xattr -d com.apple.quarantine bin/plink2`. Note that you needed it.

Test the provisioning and the preflight on Intel macOS and on Linux before you announce four-platform support.
