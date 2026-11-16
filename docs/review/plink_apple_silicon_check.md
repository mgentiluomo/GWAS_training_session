# PLINK 2 check on Apple Silicon

Written for the author. Date: 16 November 2026. Result: **passes**, with two problems in the release that are not about the numbers (see "Problems found").

The Apple Silicon run gives the same counts, lambda, hits and clumps as the Windows runs. The release was not changed.

## Set-up

| Item | Value |
| --- | --- |
| Machine | Mac14,2, Apple M2 (`uname -m`: arm64) |
| macOS | 27.0.1 (build 26A434) |
| R | 4.4.0, native arm64 (`R.version$arch` is `aarch64`, no Rosetta) |
| RStudio | 2024.09.1+394, with its own Quarto 1.5.57. `quarto` is not on the PATH. |
| Package | `GWAS_course-2026.3.1.zip` from release `project-2026.3.1`. SHA-256 `d99ae77694cb74c82a1279c692e5a7ed415a5a7dbff2a7e88c8fed2c0c969ecf` (matches). |
| Download | `curl`, so the ZIP has only `com.apple.provenance`. It has no `com.apple.quarantine`. |
| Extraction | `unzip` into a new folder. |
| R packages | `install_course_packages()` used CRAN binaries only. Nothing was compiled. |
| Data | 108 files from `download_course_data()`. All sizes and SHA-256 values match `course.MANIFEST.tsv`. No extra file. |
| Threads and memory | `config.R`: `--threads 2`, `--memory 2048` |

## PLINK 2

| Item | Value |
| --- | --- |
| Program chosen | `macos-arm64`, from the package, no download |
| `--version` | `PLINK v2.0.0-b.1.4 M1 (7 Nov 2026)` |
| `bin/plink2` SHA-256 | `e6d321565e2a4fd20874a7c21ac6c2cfe3e0802549bdffdfbe9623438cd6bf4a`, equal to `releases.tsv` |
| File type | Mach-O 64-bit executable arm64 |
| Permissions in the ZIP | `-rwxr-xr-x` for all three `plink2` programs (macos-arm64, macos-x86_64, linux-x86_64) |
| Quarantine | None on `bin/plink2`. `xattr -d com.apple.quarantine` was **not needed**. No Gatekeeper message appeared. |
| Not tested | A ZIP downloaded with a browser, which may carry `com.apple.quarantine`. |

## Times

| Run | Time | Exit code |
| --- | --- | --- |
| `check_course.R` | a few seconds | 0 |
| `preflight.R` without data | 1 s | 0, ends with "course data are missing" |
| `preflight.R` with data | 1 s | 0, all PASS |
| `run_main_path.R` (new empty folder) | 117 s | 0 |
| Restore 2.8, then modules 3 to 7 (new empty folder) | 112 s | 0 |

## Problems found

1. **`prepare_course_plink()` fails on Apple Silicon.** It expects `PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)`. The macOS arm64 build prints `PLINK v2.0.0-b.1.4 M1 (7 Nov 2026)`. The hash is right and the program runs. The error message blames macOS and tells the student to run `xattr -d com.apple.quarantine`. That advice is wrong here. `bin/plink2` is copied before the check fails. A second run fails again. The later check in `R/course.R` only looks for `v2.0.0-b.1.4`, so the preflight and the course work. The macOS Intel build and the Linux build may print other banners too.
2. **The checklist path "restore 2.8, then modules 3, 5, 6, 7" does not run.** `restore_checkpoint("5.1")` copies the 4.6 state but does not write `checkpoints/index.tsv`. Module 5 then stops at step 5.2 with "The artifact checkpoint parent is unavailable" (or with "cannot open file .../checkpoints/index.tsv" in an empty folder). Module 4 writes the index rows. The run above therefore used modules 3, 4, 5, 6, 7 from the restored 2.8. The failed attempt is kept in `out_ckpt_failed_no_module4`.

## Comparison with the Windows runs

Rules: counts exact, lambda equal to three decimals, same hits and clumps. References: `plink_office_confirmation.md`, `plink_home_comparison.md`, and the checkpoint files shipped in the data (`checkpoints/6.8`).

| Quantity | Windows | Apple Silicon main path | Apple Silicon restore 2.8 | Result |
| --- | --- | --- | --- | --- |
| Counts at every step (22 steps, 2.2 to 5.7) | see office table | same | same from 3.1 | same |
| Final cohort | 1,811 (900 cases, 911 controls) | same | same | same |
| Variants after QC | 238,513 | 238,513 | 238,513 | same |
| Association tests | 236,815 | 236,815 | 236,815 | same |
| Lambda | 1.016 (1.016465) | 1.016465 | 1.016465 | same |
| Without PCs, lambda | 1.546 | 1.546 | 1.546 | same |
| Without QC and PCs, lambda | 1.655 | 1.655 | 1.655 | same |
| Hits below 5e-8 | 8 | 8 | 8 | same |
| Clumps | 3 | 3 | 3 | same |
| Lead variants | `3:163224115:T:C`, `9:96426973:A:G`, `12:120965921:G:A` | same | same | same |
| Lead p-values | 3.23e-13, 1.23e-16, 6.53e-11 | 3.22962e-13, 1.2299e-16, 6.53157e-11 | same | same |
| Figures of module 7 | | 4 PNG files created | 4 PNG files created | ok |

### Files

The Windows files are written with CRLF line endings, the Mac files with LF. I compared the SHA-256 after changing the Mac files to CRLF (`sed 's/$/\r/'`). The first 16 characters are those in `plink_office_confirmation.md`.

| File | Result |
| --- | --- |
| `s6-4_association.Disease.glm.logistic.hybrid` (all p-values) | identical (`4c71a3b17f8d3029`) |
| `s5-7_pca.eigenvec` (PCs, signs included) | identical (`3ea5517ad4c1c24e`) |
| `s5-7_pca.eigenval` | identical |
| `s7-5_clump.clumps` | identical |
| `s7-2_lambda.tsv`, `s7-4_thresholds.tsv`, `s7-7_comparison.tsv`, `s7-8_leads.tsv` | identical |
| `s3-6_king.kin0` | identical |
| `s6-8_gwas_summary_statistics.tsv` | **differs, see below** |

### The one difference

`s6-8_gwas_summary_statistics.tsv` (236,815 rows) differs from the Windows file shipped in `data/course/checkpoints/6.8`. Only the `beta` column differs. It differs in 1,484 rows, by at most 1.1e-15 in absolute value. This is the last printed digit of `log(odds_ratio)` and comes from the maths library of the platform. The other 10 columns are identical, including `odds_ratio`, `standard_error`, `p_value` and `n`. Example: `0.0379121650698609` on Windows and `0.037912165069861` on the Mac. No result is affected. A byte-for-byte check of this file will fail on a Mac.

### Other differences

- Principal components: no difference, including signs.
- The two Mac output folders agree byte for byte in all 204 compared result files. They differ in 6 files: the restored folder has no rows for steps 2.2 to 2.7 in `step_counts.tsv` and `checkpoints/index.tsv` (and so in the 7.8 copies). The restored 2.8 `.pvar` and `.psam` keep the CRLF endings of the shipped checkpoint.
- Logs, `*.command.txt`, `*.console.txt`, `preflight.txt` and `software_versions.txt` differ in time stamps, folder names and the version banner (`M1` against `64-bit`). They were not compared.

## Outcome

**Passes.** Counts, lambda, hits and clumps are the same as on Windows. P-values and PCs are the same file by file, except the last digit of `beta` in 1,484 rows of the summary statistics.

## What is left

- macOS Intel and Linux, as before.
- A ZIP downloaded with a browser on a Mac (quarantine flag).
- Rosetta: not needed, R was native.

## Suggested changes (not made)

1. In `course_plink_version_text()` (`R/plink_setup.R`), compare only `v2.0.0-b.1.4` and the date, or store the banner of each platform in `releases.tsv` (column `version_run_here` already exists for this). Say "M1" for macos-arm64.
2. In `course_plink_run_help()`, mention `xattr` only if the program did not start. Print the real banner first.
3. Make `restore_checkpoint()` (the index path) write the restored step into `checkpoints/index.tsv` and `step_counts.tsv` of the work folder. Or change the checklist and the module 5 text to say that module 4 must be run, or that a student restoring 4.6 needs this index.
4. In the checklist, say that `s6-8_gwas_summary_statistics.tsv` can differ in the last digit of `beta` across platforms. Compare the other columns, or compare `beta` with a tolerance of 1e-12.
5. In `docs/plink_office_comparison_checklist.md`, record the Apple Silicon check as done. Intel macOS and Linux remain.

## Findings for the fix

Read-only checks on 16 November 2026, to prepare the fix. The course code was not changed. The checks used the package `GWAS_course-2026.3.1` and the clone at `notebooks/all-modules` (commit `cb9f95d`). `R/plink_setup.R` is the same in both, apart from line endings.

### 1. Version line of the four builds

| Build | How checked | Line printed | Word after the version |
| --- | --- | --- | --- |
| macos-arm64 | run on this Mac | `PLINK v2.0.0-b.1.4 M1 (7 Nov 2026)` | `M1` |
| macos-x86_64 | `strings` only, not run | `PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)` | `64-bit` |
| windows-x86_64 | `strings` only here. The office and home runs printed the same line. | `PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)` | `64-bit` |
| linux-x86_64 | `strings` only, not run | `PLINK v2.0.0-b.1.4LM 64-bit Intel (7 Nov 2026)` | `LM 64-bit Intel`, and `LM` is glued to the version |

So the current check would also fail on Linux. The Linux line comes from `strings`. Run it on Linux before you pin it.

### 2. Where "64-bit" is checked and the smallest fix

Where:

- `R/plink_setup.R` lines 77 to 83: `course_plink_version_text(row)` builds the expected text. It writes `64-bit` from the pointer size of R. This is the cause.
- Lines 133 to 140: `verify()` stops if the printed text does not contain that text.
- Lines 90 to 100: `course_plink_run_help()` gives the `xattr` advice for every macOS platform, whatever the output was.
- `scripts/tests/test_plink_setup.R` line 144 tests the old text. Lines 131 to 139 test the `xattr` text with the output `zsh: killed`.
- `R/course.R` line 524 only looks for `2.0.0-b.1.4`. It works on all four builds.

Smallest fix:

1. Add a column `version_banner` to `third_party/plink2/releases.tsv` with the exact line of each build. Do not use `version_run_here`, because three rows hold "not run" and the pin test lists it.

   | platform | `version_banner` |
   | --- | --- |
   | windows-x86_64 | `PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)` |
   | macos-arm64 | `PLINK v2.0.0-b.1.4 M1 (7 Nov 2026)` |
   | macos-x86_64 | `PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)` |
   | linux-x86_64 | `PLINK v2.0.0-b.1.4LM 64-bit Intel (7 Nov 2026)` (to confirm on Linux) |

2. Make `course_plink_version_text(row)` return `row$version_banner`. Keep the `grepl(..., fixed = TRUE)` check. Add the new column to the `needed` list in `course_plink_manifest()` and to `test_plink_pins.py`.
3. Change `course_plink_run_help(platform, output, expected)`:
   - If the output has a line that starts with `PLINK v2`, the program runs. Say: "The program runs, but its version line differs from the pin list. Expected: ... Printed: ... This is a problem of the course, not of macOS. Do not run xattr. Ask the instructor and show this message."
   - Give the `xattr` advice only if the output looks like a block: it contains `killed`, `cannot be opened`, `not permitted`, `damaged` or `Could not run`, or it is empty.
   - Keep the glibc message for Linux.
4. Update the tests: the `zsh: killed` case still shows `xattr`. Add a case with the `M1` line that must not show `xattr`. Replace the test of line 144 by the banner of each row.

The SHA-256 of the program is already checked against the pin before the version is run. The version check is a second check, so a mismatch of the middle word is not a security problem.

### 3. Restore of each checkpoint

Each case used a new output folder. "First step" is the setup chunk and the first step chunk of the module. "Whole module" runs every chunk of the module after the restore.

| Checkpoint | Call (restart id) | `guided_check_module()` | First step | Whole module | Why |
| --- | --- | --- | --- | --- | --- |
| 2.8 | `restore_checkpoint("3.1")` | works (module 3) | works (3.1) | works | Module 3 and 4 use `guided_register()`, which creates `checkpoints/index.tsv` and `step_counts.tsv` if they are missing. |
| 2.8 | `restore_checkpoint("2.8")` | **fails** (module 3) | not reached | not reached | The call means "restart at 2.8". It restores the state after 2.7, so `s2-8_state.*` does not exist. |
| 3.8 | `restore_checkpoint("4.1")` | works (module 4) | works (4.1) | works | Same as 2.8. |
| 4.6 | `restore_checkpoint("5.1")` | works (module 5) | works (5.1) | **fails at 5.2** | `guided_artifact_checkpoint()` reads `checkpoints/index.tsv` and needs the row of 4.6. The restore does not write it. The error is "cannot open file .../checkpoints/index.tsv". |
| 5.7 | `restore_checkpoint("6.1")` | works (module 6) | **fails at 6.1** | not reached | Same cause: no `index.tsv` with the row of 5.7. |
| 6.8 | `restore_checkpoint("6.1")` (the id in the module 7 metadata) | **fails** (module 7) | not reached | not reached | This restores only the 5.7 state. The 6.8 files are not restored. The message then tells the student to restore 6.1 and run module 6, and module 6 fails at 6.1 (row above). |
| 6.8 | `restore_checkpoint("7.1")` | **fails** (module 7) | not reached | not reached | This restores the 6.8 files and the 5.7 state. `step_counts.tsv` and `checkpoints/index.tsv` are missing, and the module 7 check needs both. |

Result: a student can restart at modules 3 and 4 only. Restarts at modules 5, 6 and 7 do not work, for one reason. `restore_checkpoint()` (the index path, `course_index_restore()` in `R/course.R`) copies the files but does not write the restored steps into `checkpoints/index.tsv` and `step_counts.tsv` of the work folder.

Smallest fix: at the end of `course_index_restore()`, write the index rows of the restored checkpoint and of its parents (copy them from `data/course/checkpoints/index.tsv`) and the matching rows of `step_counts.tsv`. Then add a test that restores 4.6, 5.7 and 6.8 and runs the first step of module 5, 6 and 7.

What the lessons say about the ids:

- `docs/troubleshooting.md` (section "Rejoining the class"): `restore_checkpoint("3.2")` means restart at step 3.2. The restored state is the one before it.
- The module metadata give the restart ids 3.1, 4.1, 5.1 and 6.1 for modules 3 to 6. For module 7 it gives 6.1 with checkpoint 6.8, which restores 5.7. The right id for module 7 would be 7.1, and it needs the index fix.
- The checklist did not name an id. It said "restore the verified 2.8 baseline with `restore_checkpoint`". Typed as `restore_checkpoint("2.8")`, this gives the 2.7 state and fails (row 2 above). The right call is `restore_checkpoint("3.1")`. The id 5.1 is correct for module 5. It was not a wrong id. The checklist step "modules 3 and 5 to 7" skips module 4, and module 4 is what writes the index rows that module 5 needs.

### 4. Checks that compare files of the students

- `guided_check_module()` only checks that files exist. No hash.
- The lessons call `check_step("X", data_dir = cfg$out, work_dir = cfg$out)`. This compares the output folder with itself. It always matches and it tests nothing.
- `check_step("X")` and `where_am_i()` with the default `data_dir = "data/course"` compare the student files with the files shipped in `data/course/checkpoints`. They use SHA-256 for the full checkpoints (2.8, 3.8, 4.6, 5.7) and for every file of an artifacts checkpoint. The troubleshooting page tells students to use `check_step`. Module 0 calls `where_am_i(data_dir = cfg$data_dir, ...)`, but only before any output exists.
- The answer key is used only by author scripts (`scripts/author`, `scripts/package_release.py`), not by student code.

**Yes, these checks fail on this Mac.** I ran `where_am_i("data/course", out_main)` after the main path. All replay steps are `complete`. Every full and artifacts checkpoint is `not verified`: 2.8, 3.4, 3.8, 4.6, 5.2, 5.4, 5.7, 6.1, 6.3, 6.4, 6.5, 6.7, 6.8, 7.6 and 7.8. I compared the bytes of the shipped files with the Mac files:

| Difference | Files |
| --- | --- |
| Line endings only (the shipped files have CRLF, the Mac files LF). The text is the same. | `.pvar` and `.psam` of 2.8, 3.8, 4.6 and 5.7, and almost every table of the artifacts checkpoints, including the association file and the PCs |
| Real content difference, last digit of `beta` | `s6-8_gwas_summary_statistics.tsv` (1,484 rows, at most 1.1e-15) |
| Content difference that is expected | `s7-8_summary.md` and `software_versions.txt` (software line), the PNG figures of 7.6 and 7.8 (not inspected), and in the restored run `step_counts.tsv` |

So the `beta` difference of 1e-15 matters, but the line endings are the bigger problem. Any Mac or Linux student who runs `check_step("3.8")` or `where_am_i()` against the shipped reference gets "different contents", even when the run is correct. A Windows student gets "matches". The main path and the lessons do not show this, because they compare the folder with itself.

Smallest fix: in `course_index_check()` (lines 383 and 398 to 399 of `R/course.R`), compare the files after removing carriage returns. For `s6-8_gwas_summary_statistics.tsv`, compare the table with a tolerance of 1e-12 on `beta` instead of a hash. Say in the output that PNG, software line files are not compared.
