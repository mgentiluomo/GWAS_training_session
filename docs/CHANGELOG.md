# Changelog

## 2026.4 (project release, 17 November 2026)

- New optional boxes "Try other thresholds" in steps 3.1, 3.2, 3.5, 3.6, 4.1, 4.3 and 4.4. Each box repeats the count with other thresholds and shows a table. The course value is marked. The boxes do not change your results.
- Step 5.5 draws PC1 with PC2, PC1 with PC3 and PC2 with PC3, with the key outside the plot. An optional box shows a 3D plot with ellipses (package `rgl`, not installed by step 0.5).
- Step 7.3 can add a dotted line for suggestive results at 5e-5 and labels the lead variant of each region with its rs number. Step 7.6 draws all three regions with a continuous colour scale. Step 7.7 compares the QQ and Manhattan plots from the least to the most adjusted analysis.
- Step 2.3 prints "no ID problems found" when the check passes. The terminal command of step 2.6 now includes `--flip`. Step 3.5 prints its counts as whole numbers. Step 1.9 says that ONT and PacBio produce an unaligned BAM file. Acronyms are spelled out at first use. "Strong" is kept for effects and "linked" is replaced where it meant "associated with".
- The notebooks have `chunk_output_type: console` in their header.
- All course numbers are unchanged: 1,811 samples, 238,513 variants, lambda 1.016, eight hits and three clumps. The data release is unchanged (`data-2026.1`). The PLINK programs are unchanged.

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
