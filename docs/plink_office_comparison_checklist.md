# PLINK comparison (status)

Status: **the office confirmation and the Apple Silicon check (releases 2026.3.1, 2026.3.2 and 2026.3.3) are done and passed.** The corrections found on the Mac are made in release `project-2026.3.3`. Still open: only macOS Intel and Linux.

The current release is `project-2026.3.3`. See `docs/review/plink_office_confirmation.md`, `docs/review/plink_apple_silicon_check.md` and `docs/review/student_fields_review.md`.

## Apple Silicon Mac: repeat done (16 November 2026)

Release `project-2026.3.2` was tested on an Apple M2 with a ZIP downloaded by Chrome and opened in the Finder. `prepare_course_plink()` finished without an error and printed `PLINK v2.0.0-b.1.4 M1 (7 Nov 2026)`. The preflight did not warn about a different build. The main path matched Windows (22 step counts, lambda 1.016465, 8 hits, 3 clumps), `where_am_i()` showed 30 "complete" and `check_step()` never showed "different contents". Restarts from 2.8, 3.8 and 4.6 pass with the author test. 5.7 and 6.8 stop only because the script compares raw bytes (Windows line endings, last digit of `beta`). The Safari case was seen on a folder that was changed afterwards. See `docs/review/plink_apple_silicon_check.md`.

**Apple Silicon is closed.** The two corrections proposed after this repeat are made in release `project-2026.3.3`: the text of step 0.6 on quarantine, and `test_checkpoint_restarts.R` using `course_compare_files()`. The restart test passes for all five checkpoints on Windows. Run it once on macOS Intel and on Linux too.

## Then macOS Intel and Linux

- Test the provisioning and the preflight on Intel macOS and on Linux before you announce four-platform support.
- On Linux, run `plink2 --version` and compare it with the pinned line `PLINK v2.0.0-b.1.4LM 64-bit Intel (7 Nov 2026)` in `third_party/plink2/releases.tsv`. The pinned line was read from the program, not run. The check ignores spaces, so a space before `LM` is accepted.
- Download the ZIP with a browser on the Intel Mac. A ZIP downloaded with a browser on a Mac carries the quarantine flag. On Apple Silicon `bin/plink2` was not blocked, because `prepare_course_plink()` copies without the flag. Running the packaged file by hand is blocked and macOS moves it to the Bin. If `bin/plink2` is blocked, run `xattr -d com.apple.quarantine bin/plink2` and note it.

If a count, lambda, hit or clump differs on a platform, stop and do not change an expected result. PLINK must then leave the package and a new project release is needed.
