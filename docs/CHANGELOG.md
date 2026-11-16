# Changelog

## 2026.3.3 (project release, 16 November 2026)

- Step 0.6 explains the macOS quarantine mark in short steps. Run only `prepare_course_plink()`. Do not open the programs inside `third_party/` by hand, because macOS can block them and move them to the Bin. If macOS shows a warning about `bin/plink2`, choose "Done", not "Move to Bin". Then remove the mark with `xattr -d com.apple.quarantine bin/plink2` and run the step again. If `bin/plink2` has disappeared, run step 0.6 again. The link to Apple's instructions stays.
- The author test for restarts now compares files with the same function as `check_step()`. It can pass on macOS and Linux. It is not part of the student package.
- Nothing else changes for students. The PLINK programs are unchanged. The data release is unchanged (`data-2026.1`).

## 2026.3.2 (project release, 16 November 2026)

- The PLINK version line is checked for each build. The pin list has a new column, `version_banner`, with the exact line that each program prints: `64-bit` on Windows and Intel macOS, `M1` on Apple Silicon and `LM 64-bit Intel` on Linux. `prepare_course_plink()` no longer fails on Apple Silicon. If the program runs but prints another version line, the message says that the version is not the one of the course. It gives the `xattr` advice only when macOS blocked the program. The Linux line was read from the program and has not been run on Linux yet.
- You can restart from all five checkpoints (2.8, 3.8, 4.6, 5.7 and 6.8). `restore_checkpoint()` now writes `checkpoints/index.tsv` and `step_counts.tsv`, so the next module runs to the end. The restart id is the first step that you will run: `"3.1"`, `"4.1"`, `"5.1"`, `"6.1"` or `"7.1"`. Module 7 now says `"7.1"`. If you give the id of a checkpoint itself, for example `"2.8"`, R stops and names the id to use.
- `check_step()` and `where_am_i()` compare file contents, not hashes. Line endings are ignored (Windows CRLF against Mac and Linux LF). Numbers may differ by a relative 1e-9. The message says "matches", "matches within rounding" or "different contents". Binary files must be identical. Figures and software records are not compared.
- The data release is unchanged (`data-2026.1`). The PLINK programs are unchanged.

## 2026.3.1 (project release, 16 November 2026)

- The office confirmation passed. The Windows package build gives the same counts, lambda (1.016), hits, clumps, p-values and principal components as the reference files `answer_key.json`, `build_report.md` and `checkpoints/index.tsv`. See `docs/review/plink_office_confirmation.md`.
- Step 0.6 is corrected. The command `prepare_course_plink()` is now the main action. It is no longer marked "Optional". The official PLINK page is only the fallback, named in the text. Steps 0.5 and 0.7 had the same label on their commands. It is removed there too.
- Step 0.3 now names release `project-2026.3.1`.
- The data release is unchanged (`data-2026.1`).

## 2026.3 (project release, 15 November 2026)

- The package now contains PLINK 2 Beta 1.4 (build 7 November 2026) for Windows, macOS (Apple Silicon and Intel) and Linux. They are the non-AVX2 builds. Step 0.6 now runs `prepare_course_plink()`, which copies the right build into `bin/` and checks its SHA-256 value.
- The licence text of PLINK 2 (GPL 3), the notices of its parts and the link to its source are in `third_party/plink2/`. The source of the tag `v2.0.0-b.1.4` is attached to the release.
- The Windows non-AVX2 build and the AVX2 build used for the validation gave identical results on the complete main path (counts, lambda 1.016, hits, clumps, p-values and principal components). See `docs/review/plink_home_comparison.md`. The macOS and Linux builds were checked only by their hashes.
- Step 0.3 now names release `project-2026.3`.
- `download_course_data()` waits up to an hour for the download and gives a plain message if it stops. A slow connection no longer ends the download after 60 seconds.
- The setup check (step 0.8) no longer stops on the files of the old demo. Without course data it prints a warning and ends.
- The data release is unchanged (`data-2026.1`).

## 2026.2 (project release, 15 November 2026)

- Student notebooks are Quarto files (`notebooks/*.qmd`), one per module and one for the whole course.
- Each notebook has a contents list, an "In this module" box, code notes, option tables, a "What you do" box for steps without code, and a glossary appendix.
- Each step has a short student summary. Many texts were reviewed and corrected, for example the definition of odds, the Firth correction, the p-value and the thresholds.
- Module 0 sends students to `notebooks/module_00_preparation.qmd`. The folder list at step 0.3 includes `notebooks`.
- Long code lines wrap in the rendered notebooks.
- PLINK 2 is not in the package. The four non-AVX2 builds are pinned in the `plink/bundle` branch. They wait for the comparison at the office.
- The data release is unchanged (`data-2026.1`).

## 2026.1 (project release)

- First guided course, modules 0 to 7, with the project ZIP and the encrypted classroom data.
