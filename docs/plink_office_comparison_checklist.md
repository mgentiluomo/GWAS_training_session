# PLINK comparison (status)

Status: **the office confirmation and the Apple Silicon check are done and passed.** The three corrections found on the Mac are made in release `project-2026.3.2`. Two things are still open: the repeat on the Mac, and then macOS Intel and Linux.

The current release is `project-2026.3.2`. See `docs/review/plink_office_confirmation.md`, `docs/review/plink_apple_silicon_check.md` and `docs/review/student_fields_review.md`.

## Repeat on the Apple Silicon Mac (next)

1. Download `GWAS_course-2026.3.2.zip` and extract it. Run step 0.6. `prepare_course_plink()` must now finish without an error and print `PLINK v2.0.0-b.1.4 M1 (7 Nov 2026)` as the version line. The preflight must not warn about a different build.
2. Run `restore_checkpoint("3.1")` in an empty output folder, then modules 3 to 7. Repeat for `"4.1"`, `"5.1"`, `"6.1"` and `"7.1"` (the restart ids of the checkpoints 3.8, 4.6, 5.7 and 6.8). Each must run to the end. On Windows the author test `scripts/author/test_checkpoint_restarts.R` did this for all five and passed.
3. Run `where_am_i()` on the finished main path. The checkpoints must be "complete". The `beta` column may show "matches within rounding". Figures and software records are "not compared".
4. If a count, lambda, hit or clump differs, stop and do not change an expected result.

## Then macOS Intel and Linux

- Test the provisioning and the preflight on Intel macOS and on Linux before you announce four-platform support.
- On Linux, run `plink2 --version` and compare it with the pinned line `PLINK v2.0.0-b.1.4LM 64-bit Intel (7 Nov 2026)` in `third_party/plink2/releases.tsv`. The pinned line was read from the program, not run. The check ignores spaces, so a space before `LM` is accepted.
- A ZIP downloaded with a browser on a Mac may carry the quarantine flag. If `bin/plink2` is blocked, run `xattr -d com.apple.quarantine bin/plink2` and note it.

If a count, lambda, hit or clump differs on a platform, stop and do not change an expected result. PLINK must then leave the package and a new project release is needed.
