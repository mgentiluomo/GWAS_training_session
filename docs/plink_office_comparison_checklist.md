# PLINK comparison at the office (release 2026.3 decision)

Status: to do. Written on 15 November 2026 for the author.

Release 2026.2 is published **without PLINK 2**. This comparison decides whether release 2026.3 can include the four pinned non-AVX2 builds (Beta 1.4, 7 November 2026). Rules and pins are in `docs/plink_packaging_plan.md` and `third_party/plink2/` (branch `plink/bundle`, which already contains the 2026.2 work).

If PLINK is later added to the 2026.2 line, the same run is a second confirmation on another PC. Use the same criteria.

## What you need on the office PC

- The course data (the extracted `data-2026.1` payload) and the instructor files: `instructor/answer_key.json`, `instructor/build_report.md`, `checkpoints/index.tsv`.
- The AVX2 Windows build that produced the reference results.
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

1. `git clone --branch plink/bundle https://github.com/mgentiluomo/GWAS_training_session.git C:\GWAS_cmp`
2. Put the four archives in `C:\PLINK_downloads`, then in R from `C:\GWAS_cmp`: `source("R/plink_setup.R"); prepare_course_plink()`
3. Check the answer: `bin\plink2.exe --version` must print `PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)`. Compare the executable hash with `third_party/plink2/releases.tsv` (row `windows-x86_64`).
4. Download and verify the data: `source("R/course.R"); download_course_data()` (the password is asked at the prompt).
5. `Rscript scripts/preflight.R`, then `Rscript scripts/check_course.R`.
6. `Rscript scripts/run_main_path.R` in an empty output folder.
7. Repeat steps 2 to 6 with the AVX2 build in a second folder (`C:\GWAS_ref`). Keep R, packages, threads and memory the same.
8. Compare the two runs and the reference files with the table above. Save the comparison as a table.

## If something differs

1. Stop. Do not change an expected result.
2. Note the step, the quantity, both values and the build.
3. Check the PLINK Beta 1.4 changelog for `--glm`, `--pca`, `--het`, `--make-king-table`, `--split-par` and `--mind`.
4. A difference in counts, lambda, hits or clumps means: no PLINK in the package. Release 2026.3 stays without it.
5. A difference only in p-values, PC signs or plot inputs needs your review before any text changes.

## If it all passes

1. Record the result in `docs/review/student_fields_review.md`.
2. Merge `plink/bundle` into `notebooks/all-modules`, run the tests, then follow the normal flow to `course/2026-guided-training`.
3. Update the module 0 step on PLINK: the package contains PLINK 2 Beta 1.4, R prepares it, and the official download page stays as a source. Mention `xattr -d com.apple.quarantine` on macOS and glibc 2.31 or newer on Linux.
4. Build the package with `scripts/package_project.py --plink-cache C:\PLINK_downloads`, publish `project-2026.3` and attach the PLINK source of tag `v2.0.0-b.1.4` (commit `760ee7329e8914de52f75a4e470cecabccbde0d9`).

## Apple Silicon check (your Mac)

1. Extract the release ZIP. Run step 0.6 and the preflight. Record the hardware, macOS, R, PLINK version and executable hash.
2. Restore the verified 2.8 baseline into a fresh output folder with `restore_checkpoint`.
3. Run modules 3 and 5 to 7. Module 3 alone cannot test PCA, logistic regression or clumping.
4. Compare with the Windows run under the rules above.
5. If `bin/plink2` is blocked, run `xattr -d com.apple.quarantine bin/plink2`. Note that you needed it.

Test the provisioning and the preflight on Intel macOS and on Linux before you announce four-platform support.
