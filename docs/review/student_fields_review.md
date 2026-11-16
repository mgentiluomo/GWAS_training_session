# Review of the student fields for modules 0 to 7

## Session of 16 November, office confirmation and release 2026.3.1

Written for the author, Manuel Gentiluomo. Status: release published, website not updated. History was not rewritten.

### Result in one table

| Item | Value |
| --- | --- |
| Office confirmation | **Passes.** Details and tables in `docs/review/plink_office_confirmation.md`. |
| Project release | `project-2026.3.1`, not a pre-release: https://github.com/mgentiluomo/GWAS_training_session/releases/tag/project-2026.3.1 |
| Tag | annotated `project-2026.3.1` on `003e024` (merge commit of `course/2026-guided-training`) |
| Asset | `GWAS_course-2026.3.1.zip`, 21,519,256 bytes, 75 files |
| SHA-256 | `d99ae77694cb74c82a1279c692e5a7ed415a5a7dbff2a7e88c8fed2c0c969ecf` |
| Download check | The public URL gave the same SHA-256 and size. |
| Other assets | `GWAS_course-2026.3.1.zip.sha256`, `plink-ng-v2.0.0-b.1.4-source.zip` (the same archive as in 2026.3, SHA-256 `012cf4f54285b31b75a6cf3ab695770a2f93d8864f7f237570c7d3ec0e44da6d`) |
| Data | `data-2026.1`, unchanged |
| Website | **Not updated** (see "Skipped") |

### Phase 0. This PC

- `C:\GWAS_course` was clean. `fetch` and `pull --ff-only` aligned `course/2026-guided-training`. The branches `notebooks/all-modules` and `plink/bundle` existed only on the remote. I created them locally at the remote commits.
- `C:\WEB_site\sito` has uncommitted changes (`src/app/notes/page.tsx`, `src/components/notes/ArticleRenderer.tsx`, `content/notes/jurassic-park.md`, `public/images/notes/jurassic-park/`). I did not touch them. The website phase was not done.

### Phase 1. Confirmation

- Reference files found: `C:\WEB_site\data_sources\sim2026\instructor\answer_key.json` (`56dc070f...3fac`), `build_report.md` (`f966e0ef...768e`) and `checkpoints/index.tsv` in the staging folder `classroom-stage-2026.1-final` (`f5d95011...18fe`). Full hashes are in the confirmation file.
- Package `GWAS_course-2026.3.zip`: SHA-256 matched. Extracted to `C:\GWAS_office`. `prepare_course_plink()` used the package build, with no download. `PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)`. `plink2.exe` SHA-256 `b57537f1...42b9`, equal to the pin.
- Data: the 108 staging files match `course.MANIFEST.tsv` of `data-2026.1` (sizes and SHA-256).
- Preflight, `check_course.R` and `run_main_path.R` (new output folder): all passed, exit code 0.
- Comparison: all counts at every step, the lists of removed samples, lambda 1.016, 8 hits, 3 clumps and lead p-values equal the reference files. P-values, PCs and plot inputs are byte for byte equal to an earlier run on this PC and agree with the home comparison. No difference.

### Phase 2. Step 0.6 (branch `notebooks/all-modules`)

- **Cause.** The exporter sets `run_by_default` to false for every chunk with `eval=FALSE`. The site shows "Optional" for such a chunk, in the "Do this" box and under the code. Steps 0.5, 0.6 and 0.7 each have a necessary command with `eval=FALSE`, because the whole-path script must not run them.
- **Fix at the source (course).** New step metadata `required_commands` (a list of chunk labels). Those commands are exported with `run_by_default: true`. `eval=FALSE`, the whole-path script and the `manual_required` verification do not change. Used in 0.5, 0.6 and 0.7. Step 0.6 no longer has the "Official PLINK 2 download page" button, so the R command is the main action. The page stays as the written fallback in the step text. A test was added in `test_course_exports.py`.
- **Audit of the 64 steps.** Only 0.5, 0.6 and 0.7 had a command marked "Optional". All three are fixed. Steps with both a button and a command: 0.6 (fixed) and 0.7. Step 0.7 has two buttons ("Request the course password", "Course data release"). They are real prerequisites, not a replacement for the command, so I left them. The other 61 steps have no external action next to a command. The label "Optional: you do not need it for the course" on the PLINK terminal equivalent is intended.
- **Regenerated:** export, 64 step JSON, 8 module JSON, `run_main_path.R` (only the hash line changed) and the 9 notebooks. Tests that passed: `test_plink_pins` 3, `test_course_exports` 22, `test_student_notebooks` 35, `test_project_package` 17, `test_prove_comment_only`, `test_package_release` (1 skipped), `test_plink_setup.R`, `test_course_setup.R`, `test_preflight_no_data.R`, `test_preflight_output.R`, `test_summary_stats.R`, `test_guided_module_check.R`, `check_course.R`, `check_text.py` and `--check-notebooks`.
- **Version.** Step 0.3, README, `release_checklist.md` and the default of `package_project.py` name 2026.3.1. Changelog entry 2026.3.1 added. `grep` finds no `2026.3.zip` or `project-2026.3/` in student texts.
- **Merges** (no squash, no rewrite): `notebooks/all-modules` into `course/2026-guided-training` (`003e024`), then `course/2026-guided-training` into `plink/bundle` (`a2effd9`). All pushed.

### Phase 3. Package

- `scripts/package_project.py --version 2026.3.1 --plink-cache C:\PLINK_downloads --output C:\GWAS_release_2026.3.1`. The four PLINK archives were downloaded by the project mechanism and checked against the pins.
- Student test in `C:\GWAS_student_test`: `check_course.R`, the first chunk of module 0, `prepare_course_plink()` (package build, hash equal to the pin), preflight with the data (passed) and `run_main_path.R` (exit 0). Counts, association file, eigenvectors, clumps, lambda and the summary statistics are byte for byte equal to the phase 1 run.
- The nine `.qmd` rendered with the Quarto of RStudio (all exit 0). Each render prints one knitr message, "You changed the working directory ... It will be restored". The unchanged 2026.3 package prints the same message, so it is not new. I did not remove it.

### Skipped, and open

- **Phase 4, the website.** Not done, because the repository `C:\WEB_site\sito` has uncommitted changes that are not mine. Still to do on `course/notebook-style`: `npm run sync:gwas`, `tsc`, lint, both builds, axe on steps 0.3 and 0.6, merge into `main`, check the live pages. Until then the site step 0.3 links the 2026.3 ZIP (still published) and step 0.6 still shows "Optional". After the sync, step 0.6 will show the R command alone in the "Do this" box.
- The empty folder `C:\GWAS_pkg` stayed from a failed first call. The removal was blocked, so it can be deleted by hand. The folders `C:\GWAS_office`, `C:\GWAS_student_test`, `C:\GWAS_release_2026.3.1`, `C:\GWAS_release_assets`, `C:\GWAS_release_verify` and `C:\PLINK_downloads` are outside the repository.
- No AVX2 run at the office. No run on macOS, Linux or Apple Silicon.

## Session of 15 November, home PLINK comparison and release 2026.3

Written for the author, Manuel Gentiluomo. Status: published. History was not rewritten.

### Result in one table

| Item | Value |
| --- | --- |
| Comparison | Passes. Details in `docs/review/plink_home_comparison.md`. |
| Project release | `project-2026.3`, not a pre-release: https://github.com/mgentiluomo/GWAS_training_session/releases/tag/project-2026.3 |
| Tag | annotated `project-2026.3` on `8302da1` (merge commit of `course/2026-guided-training`) |
| Asset | `GWAS_course-2026.3.zip`, 21,519,234 bytes, 75 files |
| SHA-256 | `9b0e9a7d8160d1c15fee52f4860f39c6669088a0a49866a1c274c4c8dcb264cd` |
| Download check | The public URL gave the same SHA-256 and size. |
| Other assets | `GWAS_course-2026.3.zip.sha256`, `plink-ng-v2.0.0-b.1.4-source.zip` (SHA-256 `012cf4f54285b31b75a6cf3ab695770a2f93d8864f7f237570c7d3ec0e44da6d`) |
| PLINK 2 in the package | Yes: four non-AVX2 builds (Windows x86_64, macOS arm64, macOS x86_64, Linux x86_64), mode 0755, with GPL 3 text and notices |
| Data | `data-2026.1`, unchanged |
| Website | `main` at `9ee3088`, published |

### Phase 1. Comparison (non-AVX2 against AVX2)

- Data in `C:\GWAS_cmp\noavx2`: 108 files, sizes and SHA-256 all match `course.MANIFEST.tsv`. The second clone `C:\GWAS_cmp\avx2` is at the same commit (`9ea6070`) with a copy of the data.
- Non-AVX2 `plink2.exe`: `PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)`, SHA-256 `b57537f1...bd9` equal to `releases.tsv`. AVX2 `plink2.exe` from `plink2_win_avx2_20261107.zip`: `PLINK v2.0.0-b.1.4 AVX2 (7 Nov 2026)`, SHA-256 `05255a19...fa00`. `VALIDATION.md` has no hash of the validation build.
- `check_course.R` and `run_main_path.R` ran one after the other in new output folders, with the same R 4.5.0, packages, threads and memory. Both builds finished with exit code 0.
- **Result: identical.** All 22 step counts, the final cohort (1,811 samples, 238,513 variants, 236,815 tests), lambda 1.016, the three clumps with their eight hits, every p-value, the principal components and the plot inputs. 235 of 318 files are byte for byte equal. The other 83 differ only in time stamps, folder names and the version banner. See the comparison file.
- About the preflight: it passed in the non-AVX2 clone once the data were there. The stop on `data/demo/DB_demo.*` appears only when the course data are missing (item 2f below).

### Phase 2. Version 2026.3

| Item | Before | After |
| --- | --- | --- |
| Step 0.3 | "from release `project-2026.1`" | "from release `project-2026.3`". All links point to `GWAS_course-2026.3.zip`. |
| Step 0.6 | A manual download from the official page, with a table of builds. No R command. | Short steps: the package already holds PLINK 2 Beta 1.4 for Windows, macOS (Apple Silicon and Intel) and Linux. R copies the right build with `prepare_course_plink()` and checks it. The official page, <https://www.cog-genomics.org/plink/2.0/>, stays as the manual route. Notes: `xattr -d com.apple.quarantine bin/plink2` on macOS, glibc 2.31 or newer on Linux. New student summary, a code chunk with `eval=FALSE` (like step 0.5, so the main-path script is unchanged) and an expected result. |
| `docs/setup.md`, `bin/README.md` | Download PLINK yourself | R prepares PLINK in step 0.6 |
| Licences | Course licence only | `LICENSE-CONTENT.md` says PLINK stays under GPL 3 and the course licence does not apply. `third_party/plink2/README.md` links the source tag and states the comparison result. |
| `download_course_data()` | R stopped each download after 60 seconds | The limit is 3,600 seconds for the download only and is restored. A stopped download says: "The download stopped before the end. This can happen on a slow or unstable connection. Run the same command again. If it keeps failing, ask the instructor." A partial file is removed. Test added in `test_course_setup.R`. |
| `scripts/preflight.R` | Stopped when the old demo files were missing | Without course data it prints a warning, skips the genotype check and the probe, and ends with "Preflight passed with a warning: course data are missing." The PLINK check still runs. Test added (`test_preflight_no_data.R`). The step 0.8 text mentions it. |
| Changelog | | Entry 2026.3 in `docs/CHANGELOG.md` |

- The comment-only proof **cannot pass for module 0 on purpose**: step 0.6 has a new code chunk. It reports only `lessons/module_00_preparation.Rmd` and `site_content/steps/step-0-6.json`. Nothing else changed in the R code. The only change in `run_main_path.R` is the source hash line.
- The export test and `docs/screenshot_list.md` were updated for step 0.6.
- Tests: `test_student_notebooks` 35, `test_project_package` 17, `test_plink_pins` 3, `test_course_exports` 22, `test_prove_comment_only` 3, `--check-notebooks`, `test_guided_module_check.R`, `check_course.R`, `test_plink_setup.R`, `test_course_setup.R` all passed. The nine `.qmd` rendered without warnings.
- Merges: `course/2026-guided-training` `8302da1`; `plink/bundle` `92c470e` (aligned, pushed).

### Phase 3. Package and student test

Built with `scripts/package_project.py --version 2026.3 --plink-cache C:\PLINK_downloads`, outside the repository. It holds the four builds with mode 0755, the GPL 3 text and the notices, the nine `.qmd` notebooks and no data, no HTML, no `.Rmd` notebook and no render folder. Extracted to `C:\Temp\gwas_release_test_3\GWAS_course`:

- Folders and files as expected. `check_course.R` passed. The first chunk of module 0 ran.
- `prepare_course_plink()` chose `windows-x86_64`, took the program **from the package** without downloading, and `plink2.exe --version` printed `PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)`.
- Preflight without data: warning and end. Preflight with the data copied in: `Preflight passed.`
- The complete main path ran from the extracted project (2 min 54 s). `step_counts.tsv`, the association file, the clumps, the eigenvectors and the lambda file are byte for byte equal to the phase 1 results. `guided_check_module(3)` and `(4)` passed.

### Phase 4. Website

- Branch `course/notebook-style` synced to `8302da1`. Step 0.3 links `GWAS_course-2026.3.zip`.
- axe on steps 0.3, 0.6, 0.7 and 3.3 at 390 px and 1280 px, light and dark, showed one new finding on step 0.6: `target-size`. The code note markers on two adjacent lines were 20 px. I made them 24 px (no overlap). After the fix only the old logo finding remains. No page scroll on any of the 64 steps.
- `tsc` clean, `lint` 0 errors, normal build and `GWAS_REVIEW_BUILD=1` build passed. Merged into `main` (`9ee3088`) with `--no-ff`, build and lint on `main` passed, pushed.
- On https://www.manuelgentiluomo.it: steps 0.3 and 0.6 answer 200. Step 0.3 has three links to the 2026.3 ZIP and none to 2026.2. Step 0.6 shows `prepare_course_plink`, the macOS `xattr` note and the glibc note. The ZIP link answers 200.

### Skipped, and open

- macOS and Linux builds: checked only by their SHA-256 values. Not run.
- Analysis in R on the Mac, notebook execution, the comparison against `instructor/answer_key.json` (see `docs/plink_office_comparison_checklist.md`).

## Session of 15 November, release 2026.2

Written for the author, Manuel Gentiluomo. Status: published. History was not rewritten.

### Result in one table

| Item | Value |
| --- | --- |
| Project release | `project-2026.2`, not a pre-release, on `https://github.com/mgentiluomo/GWAS_training_session/releases/tag/project-2026.2` |
| Tag | annotated `project-2026.2` on `ef74130` (merge commit of `course/2026-guided-training`) |
| Asset | `GWAS_course-2026.2.zip`, 269,423 bytes, 61 files |
| SHA-256 | `c1a3c9381ba9cd319945c82782d3f20620597ba03886404de31ad7c372509ba9` |
| Download check | The public URL gave the same SHA-256 and size. |
| PLINK 2 in the package | No |
| Data | `data-2026.1`, unchanged |
| Website | `main` at `71c56f9`, published |

### Phase 0. PLINK comparison: not run

The plan needs the course data, `instructor/answer_key.json`, `instructor/build_report.md` and the AVX2 reference results. None of them is on this PC. There is no `C:\WEB_site\data_sources` folder, and a search found no answer key or data archive. The comparison would have been empty, and the plan says it must fail when a reference is missing. I followed rule 0b: **no PLINK in the package**. `plink/bundle` stays separate and now holds the 2026.2 work too. I did not prepare the licence notes again, because nothing ships.

| Quantity | Result on this PC |
| --- | --- |
| Counts at every step | not run (no data) |
| Lambda | not run |
| Top hits and clumps | not run |
| Archive hashes (earlier, browser download) | 4 of 4 match the pins |

### Phase 1. Website changes

- The label "Course bookkeeping, do not change" is removed. The lighter colour stays. axe found no colour contrast problem.
- The cells of the option tables wrap. No option table scrolls sideways at 390 px on any of the 64 steps.
- Two bugs found and fixed while checking all 64 steps. First, a screen-reader-only span inside a scroll region widened the whole page on steps 0.7, 1.8 and 6.8. Second, the "In short" box showed Markdown links as raw text. Both are fixed. The box also wraps long words.
- Still scrolling inside a contained, keyboard-reachable box at 390 px: Markdown tables on steps 1.8, 1.9 and 6.8, and fenced code blocks on steps 0.7 and 1.10. Not changed.

### Phase 2. Version 2026.2 in the course

- References to `project-2026.1` and `GWAS_course-2026.1.zip` changed in module 0 (step 0.3), `README.md` and `docs/release_checklist.md`. Data references (`data-2026.1`) are unchanged. `docs/project_zip_report.md` and `docs/project_zip_proposal.md` stay as history of the first release.
- `scripts/package_project.py`: the default version is 2026.2. The version rule was fixed to 2026.1 and now accepts 2026.N and 2026.N.M.
- `docs/CHANGELOG.md` is new. `docs/session_report.md` and `docs/setup.md` have a short 2026.2 note. Step 0.6 was not changed, because PLINK is not in the package.
- Tests: `test_student_notebooks` 35, `test_project_package` 6, `test_course_exports` 22, `test_prove_comment_only` 3, `--check-notebooks`, the comment-only proof, `test_guided_module_check.R` and `check_course.R` all passed. The nine `.qmd` rendered without warnings.
- Merges: `course/2026-guided-training` `ef74130`. `plink/bundle` `9ea6070` (one conflict in `package_project.py`, solved by keeping both the PLINK arguments and the new version rule). On `plink/bundle`: `test_student_notebooks` 35, `test_project_package` 17, `test_plink_pins` 3, `test_course_exports` 22 and `test_plink_setup.R` passed.

### Phase 3. Package and student test

Built from `course/2026-guided-training` outside the repository. The nine `.qmd` are in. No generated `.Rmd`, no data, no render folder, no HTML. Extracted to `C:\Temp\gwas_release_test\GWAS_course`: the folders `R`, `lessons`, `notebooks`, `scripts` and the files `config.R` and `GWAS_course.Rproj` are there. `check_course.R` passed. The first chunk of `module_00_preparation.qmd` ran with `Rscript`. A notebook rendered from the extracted copy. `guided_check_module(3)` stops with "Complete step 0.7 before module 3", the right answer without data.

### Phase 4. GitHub release

`gh` was installed with winget. You logged in. I created the annotated tag, pushed it, and created the release with the ZIP and the `.sha256` file. The notes say what is new, that PLINK is not included, that Mac and Linux builds are pinned but not run, and that the data stay `data-2026.1`.

### Phase 5. Public website

- Synced to course commit `ef74130`. Step 0.3 links `GWAS_course-2026.2.zip`.
- `tsc` clean, `lint` 0 errors (10 old warnings), normal build and `GWAS_REVIEW_BUILD=1` build passed.
- **The production build shows all 8 modules and all 64 steps** (`PUBLISHED_MODULES` is 0 to 7). I did not change this.
- axe (WCAG 2.0 to 2.2 A and AA, best practice) on module 3 and steps 0.3, 0.6, 3.3, 6.4 and 7.7, at 390 px and 1280 px, light and dark: only the old `label-content-name-mismatch` on the header logo. No page scroll.
- Merged into `main` with `--no-ff` (`71c56f9`), build and lint on `main` passed, pushed.
- After 3 minutes, `https://www.manuelgentiluomo.it`: `/teaching/gwas`, `/teaching/gwas/module-0/step-0-3`, `/teaching/gwas/module-3`, `/teaching/gwas/module-3/step-3-3` and `/teaching/gwas/module-6/step-6-2` answer 200 with the new texts. Step 0.3 has three links to the 2026.2 ZIP. Step 6.2 has the new odds text. The ZIP link answers 200. `/gwas/notebooks/module_03_sample_quality_control.qmd` and `gwas_course_complete.qmd` answer 200. **The text is identical to the files in the release.** Only the line endings differ: the files in the ZIP have Windows line endings, the site copies have Unix ones. This is harmless for RStudio and Quarto.

### Skipped, and open

- The PLINK comparison and PLINK in the package (see phase 0).
- Analysis on the course data, notebook execution, macOS and Linux, the other PLINK builds.
- The GitHub release has no source archive of the PLINK tag, because PLINK is not shipped.

## Session of 15 November, preview review

Written for the author, Manuel Gentiluomo. Status: finished. No release. Nothing was pushed to the website `main` branch. History was not rewritten.

### A1. Odds in the other steps

The phrase ", the ratio of cases to controls." was in the `--glm` explanations of steps 6.4, 6.6 and two commands of 7.7.

- Before: "... changes the odds of disease, the ratio of cases to controls."
- After: "... changes the odds of disease. The odds of disease are the chance of having the disease divided by the chance of not having it."

This matches step 6.2 and the glossary. Commits on `notebooks/all-modules`: `e7f113e` (odds), `5b7f030` (folder list), `5d290fd` (wrapped code). The final `grep` finds the old phrase in no lesson, notebook or site JSON. It still appears in `docs/review/student_fields_review.md`, in the quoted "before" text and in the older drafts. I left those, because they record what the text said at the time. It also appears in the untracked rendered HTML under `notebooks/render_check/` of earlier renders. I rebuilt the renders from the new notebooks.

### A2. Folder list in module 0

"`R`, `lessons` and `scripts`" became "`R`, `lessons`, `notebooks` and `scripts`" in the step 0.3 success line, in the action text of step 0.3, in the "You should see" line and in the expected result. Step 0.4 does not repeat the list. The project ZIP built from the course branch holds nine files under `notebooks/`.

### A3. Wrapped code in the notebooks

`code-overflow: wrap` is now in the generated header of every `.qmd`. A test checks it. The R code is unchanged. The comment-only proof passes.

### Course checks

`test_student_notebooks` 35, `test_project_package` 6, `test_course_exports` 22, `test_prove_comment_only` 3, all OK. `--check-notebooks` passes. `test_guided_module_check.R` and `check_course.R` passed. The nine `.qmd` rendered with the RStudio Quarto (`--no-execute`) with no warnings. `notebooks/render_check/compare.html` is rebuilt with no problem in any row.

Merges: `course/2026-guided-training` `325f1f4` (no squash), `plink/bundle` `2bc6040`. `test_plink_pins` 3 OK and `test_plink_setup.R` passed. `plink/bundle` was not merged into the course branch. Both were pushed.

### B. Website, branch `course/notebook-style`

Content synced to course commit `325f1f4` (commit `dc489ea`).

- **B1, long lines (`fcc9519`).** Code lines wrap inside the box, with a hanging indent of 1.5 rem for the continuation. The note markers stay in the gutter on the first visual line. The "Module setup" panel now uses the same component. The PLINK terminal box already wrapped its command with a flex layout, so I did not change it. At 390 px, no code box has a horizontal scrollbar on steps 3.3, 6.4 and 7.7. "Copy R code" copies the exported code. I compared the clipboard with the step JSON for steps 3.3, 4.5, 6.4, 7.7 and 7.8: all equal. Chrome on Windows returns the clipboard text with CRLF, so I compared after changing CRLF to LF. No line break is added.
- **B2, bookkeeping (`0c98007`).** The marker is the comment line `# Course bookkeeping`. I looked at all 29 code blocks that have it. The block runs from that line to the end of the code, or to the next numbered comment. Two steps differ: 4.5 and 7.8 have a numbered comment after the bookkeeping lines (`# 8.` and `# 6.`), so the lighter block ends before it. The lines are in `--muted` colour with the label "Course bookkeeping, do not change". The text stays in the copied code. axe reports no colour contrast problem in light or dark.
- **B3, time (`3705d06`).** All eight "At a glance" overviews contain "How long it takes", so "In this module" no longer shows the time. The page text has one mention per module (checked for modules 0 to 7). Other overlaps, not changed: the "Steps" list in "In this module" repeats the step cards further down. The overviews of modules 1 to 4 also name a slow step, and the checkpoint is named in module 2.

**Checks.** `tsc --noEmit` clean. `npm run lint` 0 errors, 10 old warnings. `next build` with `GWAS_REVIEW_BUILD=1` passed. axe-core (WCAG 2.0 to 2.2 A and AA, plus best practice) on module 3 and steps 3.3, 6.4 and 7.7, at 390 px and 1280 px, light and dark, with the closed blocks opened: the only finding is the old `label-content-name-mismatch` on the header logo link. No horizontal page scroll. The Tab walk of 59 stops found no hidden stop and the markers work with Enter.

One scroll remains: the option tables of steps 6.4 and 7.7 scroll sideways by a few pixels at 390 px (358 px content in 350 px). They are tables, not code boxes. The scroll region is keyboard reachable. I did not change it.

**Screenshots** (scratchpad, `C:\Users\manue\AppData\Local\Temp\claude\c4b1ded9365bb562\712313de-0104-40a4-a15c-0d2a722ccdb6\scratchpad\axe\`): `step33_before_390.png`, `step33_before_1280.png`, `step33_after_390.png`, `step33_after_1280.png`. Before, the code scrolled sideways. After, it wraps and shows the label.

### C1. Preview

The address `https://personal-site-git-course-notebook-style-mgentiluomos-projects.vercel.app` answers 302 to a Vercel sign-in page (`vercel.com/sso-api`). The preview is protected, so curl could not read the four pages. I only note it. Open it while you are signed in to Vercel.

### Skipped

Not run: analysis on the course data, execution of the notebooks, macOS and Linux, the other PLINK builds, the office comparison run.

## Session of 15 November, evening

Written for the author, Manuel Gentiluomo. Status: finished. No release. Nothing was pushed to the website `main` branch. History was not rewritten. The experimental files that ended up in `cf82dbf` are left as they are.

### Point 1. Missing commits

- `b36a55c` (ZIP with the `.qmd` only) was already in `course/2026-guided-training` and in `plink/bundle`.
- `168da50` (the afternoon report) was in neither. The merge at the end of this session brought it in.
- Project ZIP built outside the repository from the course branch: 61 files, nine `.qmd` notebooks, no generated `.Rmd` notebook. Not published.

### Point 2. Step 0.4 and the references to `lessons/`

Step 0.4 had no `student_action`, because it is a code step. I changed the step text and the module introduction instead.

| Place | Before | After |
| --- | --- | --- |
| Module 0 introduction | "This notebook is the source of the guided preparation module. A notebook is a file that mixes text and R commands." | "The student notebook for this module is `notebooks/module_00_preparation.qmd`. A notebook is a file that mixes text and R commands. The folder `lessons/` holds the source files that the author edits. You do not open them." |
| Step 0.4, action 2 | "In the Files pane, click the folder `lessons`. Then click this notebook. It opens in the editor." | "In the Files pane, click the folder `notebooks`. Then click `module_00_preparation.qmd`. It opens in the editor. The file `gwas_course_complete.qmd` holds all modules in one notebook, if you prefer one file. The folder `lessons` holds the source files for the author. You do not need it." |
| `README.md` table | "Canonical notebook", links to `lessons/*.Rmd` | "Student notebook", links to `notebooks/*.qmd` |
| `docs/setup.md` | link to `lessons/module_00_preparation.Rmd` | link to `notebooks/module_00_preparation.qmd` |

I searched `docs/`, `R/`, `config.R` and the other lessons for `lessons/` and `.Rmd`. I found no other student-facing reference. The list of folders in steps 0.3 (`R`, `lessons`, `scripts`) is still true and I left it. Commit `30b9e64`.

### Point 3. Step 3.5, command 2 title

The code removes only one end.

- `lessons/module_03_sample_quality_control.Rmd` line 501: `low <- het$IID[f < mean_f - 3 * sd_f]`.
- Line 502: `high <- het$IID[f > mean_f + 3 * sd_f]`.
- Line 504: `high` goes only to `flag_high.txt`, for review.
- Lines 505 and 507: `remove_file` is built from `low`, and `--remove` uses it.

A low F means too many heterozygous sites. So the removal is for unusually high heterozygosity only. The title stays "remove samples with unusually high heterozygosity". The summary, the option tables and the expected result ("13 wells with low F are removed") already agree with the code. No change, no commit.

### Point 4. Step 6.2 and the glossary

| Place | Before | After |
| --- | --- | --- |
| 6.2 summary | "... the odds of disease, the ratio of cases to controls. This multiplier is the odds ratio." | "The model estimates how many times each extra copy of the allele multiplies the odds of disease, the chance of having the disease divided by the chance of not having it. This multiplier is the odds ratio." |
| Glossary, Odds | "... the number of people with the outcome divided by the number without it." | "The odds of an outcome are the chance of having the outcome divided by the chance of not having it. In a group, this equals the number of people with the outcome divided by the number without it. ..." |
| Glossary, OR | "Odds ratio per additional copy of the tested allele in an additive model." | "Odds ratio. It shows how many times the odds of disease are multiplied by each extra copy of the tested allele in an additive model. A value of 1 means no effect." |

Commit `9c6a5b5`. **Not changed, for your decision:** the same phrase "the ratio of cases to controls" is still in the `--glm` explanations of steps 6.4 and 6.6 and in two commands of step 7.7. I did not extend the change, because you asked for 6.2 only.

### Checks after points 2 to 4

Comment-only proof passed. `test_student_notebooks` 35, `test_project_package` 6, `test_course_exports` 22, `test_prove_comment_only` 3, all OK. `--check-notebooks` passes. `test_guided_module_check.R` and `check_course.R` passed. The nine `.qmd` rendered with the RStudio Quarto (`--no-execute`) with no warnings. `notebooks/render_check/compare.html` is rebuilt: no problem in any row, 979 ids and no duplicate in the complete notebook.

### Merges

- `course/2026-guided-training`: merge commit `f63f2a2` (no squash), pushed.
- `plink/bundle`: merge commit `1ab5610`, pushed. Tests: `test_student_notebooks` 35, `test_project_package` 17, `test_plink_pins` 3, `test_course_exports` 22, `test_plink_setup.R`, all OK. It is not merged into the course branch.
- This report commit lives on `notebooks/all-modules` only.

### Point 5. Website, branch `course/notebook-style`

- Synced to course commit `f63f2a2`. The sync copied the nine `.qmd` files to `public/gwas/notebooks/`. Commit `7878fc4`, pushed. `main` untouched.
- `tsc --noEmit` clean. `npm run lint`: 0 errors, 10 old warnings. `next build` with `GWAS_REVIEW_BUILD=1` passed.
- Local production server: step 0.4 shows `module_00_preparation.qmd` and the sentence about the source files. Step 3.5 shows "unusually high heterozygosity". Step 6.2 shows "chance of not having it".
- Downloads: `/gwas/notebooks/module_00_preparation.qmd` and `gwas_course_complete.qmd` answer 200, are byte-identical to the files in the course repository, and start with a valid Quarto header. The module 0 page and the course home carry `download="..."` buttons.

### Point 6. Vercel preview

I could not read the preview address without credentials. The GitHub API answers 404 for the private repository, and the guessed address does not exist. The commit page of the branch is opened in your browser. The Vercel check mark is on the latest commit, `7878fc4`.

### Skipped

Not run: analysis on the course data, execution of the notebooks, macOS and Linux, the other PLINK builds, the office comparison run.

## Session of 15 November, afternoon

Written for the author, Manuel Gentiluomo. Status: finished. Nothing was released. The website branch is pushed but not merged into `main`.

### 1. PLINK download comparison (phase 0)

All four archives that you downloaded with a browser match the hashes in `third_party/plink2/releases.tsv`.

| Archive | Result |
| --- | --- |
| `plink2_win64_20261107.zip` | match |
| `plink2_mac_arm64_20261107.zip` | match |
| `plink2_mac_20261107.zip` | match |
| `plink2_linux_x86_64_20261107.zip` | match |

The manifest, `third_party/plink2/README.md` and `docs/plink_packaging_plan.md` now say that the pins were confirmed by a second, independent browser download on 15 November 2026. The wording "to be verified by the author against the official page" stays, because no publisher checksum was compared. The commit is on `plink/bundle`. The folder `PLINK` moved to `C:\PLINK_downloads`. `git status` is clean on all branches.

### 2. Corrections applied (phase 1)

| Step | Before | After |
| --- | --- | --- |
| 3.4 summary | "We pick a set of common variants that are not strongly linked to each other. The sample checks that follow need independent variants, ..." | Your text: "We select common DNA sites that are less strongly correlated with each other. This stops groups of similar sites from weighing too much in the sample checks. The full dataset is kept for the association scan." |
| 3.3 `min-male-xf` | "... F measures how homozygous the X chromosome looks." | Same, plus "Values near 1 are expected when there is only one X chromosome, as in males." |
| 4.5 `--export A` (option table and lesson text) | "Writes a table of allele counts, recorded as 0, 1 or 2 copies ..." | "Writes a table with one row per person and values of 0, 1 or 2 for each variant. For chromosomes present in one copy, such as X in males, PLINK writes 0 or 2, so 2 does not mean two physical copies." Step 6.1 (one autosomal variant) keeps its text. |
| 5.3 summary | "... pair of alleles, the alternative DNA letters, ..." | "... the two DNA letters that can occur at that site ..." |
| 3.5 command 2 title | "remove samples with unusually few matching letters" | "remove samples with unusually high heterozygosity" |
| 5.4 `no-mean-imputation` (both commands) | "Leaves missing genotype calls out of each average instead of replacing them with an average genotype." | "A missing genotype adds nothing to a person's score, instead of being filled in from the allele frequency." |
| 6.2 summary | "We calculate how each extra copy changes the odds of disease, ..." | "The model estimates how many times each extra copy multiplies the odds of disease, the ratio of cases to controls. This multiplier is the odds ratio." |
| 6.4, 6.6, 7.7 `firth-fallback` and `firth`; 6.6 summary | "reduces bias with small groups" | "gives usable estimates when very few people carry the allele" |
| 6.5 summary | "p-value, a measure of evidence against no effect" | "p-value, the chance of a result at least this strong if the variant had no effect" |
| 6.6 table | Already aligned after the `--snp` change | Checked again: no `--extract` row remains. The table matches the R command and the terminal command. |
| 4.2, 6.7, 7.3, 7.4, 7.5 thresholds | "0.00001", "0.00000005", "5e-8 (0.00000005)" | "1 × 10⁻⁵ (0.00001)", "5 × 10⁻⁸ (0.00000005)". Step 6.7 now names the threshold. Step 4.4 keeps its formula, which was not on your list. |
| 7.7 headings | "Command 1: Command 1: ..." | "Command 1: ...". The lesson labels carried the prefix. The generator now removes a repeated "Command N:" prefix, and a test checks it. |

Commits: the text corrections (`cf82dbf`) and the generator fix (`f19a674`).

I made a mistake in `cf82dbf`. `git add notebooks` also added the untracked Quarto experiment (`notebooks/experiment_html/` and your `module_03_sample_quality_control.qmd`). I removed them from the index in `4abaff1`. They stay in the history of `cf82dbf`, so nothing is lost. The generated module 3 `.qmd` has now replaced your experimental file in the working folder.

**Step 0.3, as it reads now (not touched, for you to check).**

- Summary: "We download and extract the complete course project. Keeping its files together lets the commands find the files they need."
- Action: "Download GWAS_course-2026.1.zip (link to the `project-2026.1` release). Extract it under C:/ on Windows or your home folder on macOS or Linux, using your system's extraction tool. Open the supplied GWAS_course folder and check that it contains config.R, GWAS_course.Rproj, R, lessons and scripts."

### 3. Quarto as the student format (phase 2)

- `DEFAULT_FORMAT` is now `"qmd"`. The nine generated `.Rmd` notebooks are removed. The `rmd` renderer stays in the registry (`--notebook-format rmd`). `--check-notebooks` also flags any leftover generated `.Rmd` notebook.
- Each notebook has: a floating contents list on the left (steps, glossary, next links), numbered step headings with anchor links, an "In this module" box (time from the lesson, what you need, linked steps, the checkpoint where the module ends), code annotations from the numbered comments, copy buttons on, code never folded, the expected result as a collapsed tip, the PLINK terminal equivalent as a note, and a "What you do" box for reading and outside-R steps.
- At the end of each module: "Where next" with previous and next `.qmd` links and the module page on the website. The complete notebook starts with a course map and repeats the previous and next logic between modules.
- **Links between notebooks.** Quarto does not rewrite `.qmd` links to `.html` outside a website project. I tested a minimal `_quarto.yml` and it did not help. The notebooks keep the `.qmd` link, which opens the file in RStudio, and a small script in the rendered page changes it to `.html` in the browser. The script is in the YAML header, so no extra file ships.
- **Glossary links.** The course glossary is a separate Markdown file, and `../docs/glossary.md#term` fails in a rendered page. Each notebook now ends with a "Glossary terms used in this notebook" appendix. The links point to it (`#glossary-term`). They work offline, in RStudio Visual mode and in the HTML. Only the terms a notebook uses are copied. A missing term stops the generator. The appendix headings are unlisted, so the contents list stays short.
- **Check on the nine rendered pages.** Rendered with the Quarto in RStudio, `--no-execute`, no warnings. No duplicate ids, no broken links inside a page, and every step is in the contents list. Every code step has its Expected result and PLINK boxes. Every other step has a "What you do" box. The complete notebook has 979 ids, no duplicates, no broken link and 192 course map links.
- **Open them.** `notebooks/render_check/compare.html` (untracked) is the index of the nine pages, with the check table. The pages are in `notebooks/render_check/qmd/`. Each render of a single file with `--output-dir` deletes the other files in that folder, so I rendered next to the source and moved the HTML.
- **ZIP.** Built outside the repository: 61 files, 268,372 bytes. The nine `.qmd` notebooks are inside. No `.Rmd` notebook, render folder, HTML or archive is inside. Not published.
- Commits: `00c4bd4` (the switch and the navigation features together) and `b36a55c` (ZIP allowlist). I could not split the switch and the navigation into two clean commits, because the renderer changes are in the same functions.

### 4. Merge (phase 3)

All checks passed, so I merged.

- `course/2026-guided-training` now holds the merge commit `886fa02` (no squash) and is pushed.
- `plink/bundle` holds `3d326e9`, the merge of `course/2026-guided-training` into it. It is pushed. It is not merged into the course branch. It waits for the office comparison run.

### 5. Website prototype (phase 4)

Branch `course/notebook-style` in `C:\WEB_site\sito`, from `main`. Not merged. Four commits: `a2a9ef9` (content sync to course commit `886fa02`), `fb28599` (the sync script copies the notebooks), `c518450` (the page features), `ae0ab5e` (marker gutter).

- Step pages: "In short" (student summary), a "What you do" box for reading and outside-R steps, R code with numbered markers in a left gutter and the explanations under it (the markers are links, so the keyboard works; the copy button copies the exported code with its comments), a visible "What each option does" table per command with modifiers under their parent and the shared `--threads` and `--memory` line, the expected result collapsed, and the terminal equivalent in a note box with an accent border. The old "All options explained" list is hidden when the new tables exist. Previous and next navigation is unchanged. The format viewer, the "Do this" card, "Report a problem" and the beta label are untouched.
- Module pages: an "In this module" box like the notebook, and a download button for the module notebook. The course home has a button for the complete notebook.
- **Download choice.** The sync script copies the nine `.qmd` files to `public/gwas/notebooks/`. A raw GitHub link would show the file as text and the `download` attribute does not work across origins. The same pattern already holds for the format examples. The files come from the merged commit. No data and no password are involved.
- **Checks.** `tsc --noEmit` passed. `npm run lint` gave 0 errors and 10 warnings that were there before. `next build` passed with `GWAS_REVIEW_BUILD=1`. axe-core (WCAG 2.0 to 2.2 A and AA, plus best practice) ran on module 3, step 3.3 and step 6.4, at 390 px and 1280 px, in light and dark, with the collapsed blocks opened. The only finding is `label-content-name-mismatch` on the header logo link (`.gap-2.5`). It appears on every page and the header is not part of this change. There is no horizontal page scroll at 390 px. A Tab walk of 59 stops on steps 3.3 and 6.4 found no hidden focus stop. The header and some Markdown links use the browser's own focus ring, not the site ring. My new controls use the site ring. Pressing Enter on a note marker moves to its explanation.
- **Preview URL.** I could not read it. This machine has no `gh` or Vercel command, and the repository is private. Open the Vercel dashboard, then Deployments, then the branch `course/notebook-style`. Or open the branch on GitHub and follow the Vercel check on the latest commit (`ae0ab5e`). A preview build shows every module (`NEXT_PUBLIC_REVIEW_BUILD`).

### 6. Tests

- Course, `notebooks/all-modules` and `course/2026-guided-training` (Windows): `test_student_notebooks` 35 OK, `test_project_package` 6 OK, `test_course_exports` 22 OK, `test_prove_comment_only` 3 OK. `--check-notebooks` passes. The comment-only proof passes. R: `test_guided_module_check.R` and `check_course.R` passed.
- `plink/bundle` after the merge: `test_student_notebooks` 35, `test_project_package` 17, `test_plink_pins` 3, `test_course_exports` 22, all OK. `test_plink_setup.R` passed.

### 7. Skipped, open issues, where I stopped

- Not run: any analysis on the course data, the notebooks themselves (they were rendered, not executed), macOS and Linux, the other PLINK builds, the office comparison run.
- **Module 0 still tells students to open the notebook in `lessons/`.** The student notebooks are now `.qmd` files in `notebooks/`. I did not change module 0 text, as instructed. Please decide whether 0.4 should point to `notebooks/module_00_preparation.qmd`.
- I did not update `docs/session_report.md`, `docs/release_checklist.md` or `docs/setup.md`.
- I stopped after pushing the website branch and writing this section. No usage limit stopped me.

## Session of 15 November (earlier)

Written for the author, Manuel Gentiluomo. Status: finished. Everything below was done while you were away. Nothing was merged, nothing was released and the website repository was not touched. Branches `notebooks/all-modules` and `plink/bundle` are pushed as backups. `course/2026-guided-training` was not changed in this session.

### A. Read these first

1. **Phase B proposals that I did not apply** (section D below). Three items change a scientific statement or a teaching choice. They need your decision.
2. **Module 0 text after the review.** Steps 0.1, 0.2, 0.3, 0.6 and 0.7 now carry links and a little more detail. The 0.7 summary has three sentences, one more than the usual limit of two. The 0.6 action is long. Check both, and check that the text still says what you teach.
3. **The Quarto pages.** Open `notebooks/render_check/compare.html` (section G) and look at one module in both versions. The default stays `.Rmd`.
4. **PLINK pins** (section I). They are a first pin and are not verified against any publisher checksum. Compare them with the official page before you rely on them.
5. **The reviewer found nothing in steps 5.4, 6.2, 6.3, 7.1, 7.2 and 7.3.** That run was short. Read those summaries yourself, as you planned.

### B. Decisions taken without asking

1. **Module 7 restart.** `restore_checkpoint("6.1")` is supported, because the indexed restore picks the full checkpoint at 5.7. Module 7 now says: "Finish module 6 first. Or restart with: restore_checkpoint("6.1") and run module 6 again (use an empty folder)." The module 3 message is byte-identical to before. The rule in `R/guided.R`: when the restart step belongs to the module that makes the files, the message says "and run module N again". The R test was updated. Commit `d4b6c2d`.
2. **Step 6.6.** The plain PLINK 2 command now uses `--snp VARIANT_ID`, as the R code does. The text says to replace `VARIANT_ID` with the ID that R saved in `s6-6_variant.txt`. No R chunk changed. The special 6.6 validator rule and its regression test were removed. The 2.6 conditional `--flip` rule stays. Commit `88ac93c`.
3. **Phase B.** Codex reviewed the text without being told who wrote it. I applied only corrections that the lesson text clearly supports (section C). Commit `5113726`, with the comment-only proof.
4. **Phase C.** I found no generator problem, so there was no generator commit.
5. **Phase D.** The `qmd` renderer is behind `--notebook-format qmd`. The `.qmd` files carry no `execute: eval: false`. Students run them. I rendered them with `quarto render --no-execute` instead. Commit `2777593`.
6. **Phase E.** The ZIP allowlist accepts only `notebooks/module_0N_*.Rmd` and `notebooks/gwas_course_complete.Rmd`. Any other tracked file in `notebooks/` stops the build. Commit `7580bfc`.
7. **Phase F.** Followed `docs/plink_packaging_plan.md`, items 2 to 4. Module 0 text, expected numbers and `CLAUDE.md` were not changed.
8. **ZIP metadata (branch `plink/bundle` only).** Every ZIP member now records a Unix creation system (value 3), so the permission bits are honoured on every platform. This changes the bytes of the project ZIP compared with earlier builds. The two builds in one run are still identical.
9. **Pins.** I chose the four URLs listed in your brief. I did not look for publisher checksums.

### C. Phase B: corrections applied

Reviewer findings that I applied (wording, clarity, spelling, unsupported claims). Each correction is supported by a sentence in the lesson of the same step.

| Step | Field | What changed |
| --- | --- | --- |
| 0.1 | action | Added the CRAN link and the macOS choice (arm64 or x86_64). |
| 0.2 | action | Added the official Posit link. |
| 0.3 | action | Added the project ZIP link of release `project-2026.1`. |
| 0.6 | action | Added the official download link, the advice to choose the 64-bit version without AVX2 when unsure, and the note for Windows ARM and Linux ARM. |
| 0.7 | summary | Added how to request the password and who may use the form. |
| 1.7 | summary | The code checks that the files are present and that their sizes agree. It does not prove that the samples belong together. |
| 3.3 | `max-female-xf`, `min-male-xf` | Replaced "X coefficient" with "X chromosome F value" and explained F in the lesson's own words. |
| 3.4 | `--indep-pairwise` | Explained the squared correlation (r²) and that one site of every pair above 0.2 is dropped. |
| 3.5 | summary and `--het` | Plainer words ("two different DNA letters"). `--het` reports the numbers, PLINK calculates F, R calculates the review thresholds. |
| 3.6 | `--king-table-filter` | Added what the kinship score measures. |
| 4.4 | `--hardy` | The expected shares come from the allele frequencies when people mate at random. |
| 5.6 | summary | Explained the principal components in plain words. I kept the original sentence "this rule defines the group for our teaching analysis", which the reviewer had dropped. |
| 5.7 | `--indep-pairwise` | Same r² explanation as 3.4. |
| 6.6 | summary and `--snp` | The variant is chosen among valid tests on chromosomes 1 to 22. |
| 7.4 | summary | Names the three rules. The third rule is the Benjamini-Hochberg adjusted p-value and controls the expected share of false results among those called significant. |

### D. Phase B: proposals not applied

For each item the original text is in the lesson now. The suggested text is the reviewer's, unless I say otherwise.

**1. Step 3.4, student summary.** Not applied, because you fixed this exact text in an earlier session.

- Original: "We pick a set of common variants that are not strongly linked to each other. The sample checks that follow need independent variants, otherwise the same genetic signal is counted many times."
- Reviewer: pruning lowers the correlation inside the chosen windows. It does not guarantee independence, and "need independent variants" overstates what the checks require.
- Suggested: "We select common DNA sites whose genotype patterns are less strongly correlated. This reduces the influence of groups of similar sites on the sample checks, while keeping the full dataset for association testing."
- Supported by the lesson: yes ("less correlated", "It does not delete the other sites from the association data").

**2. Step 3.3, `min-male-xf`, one extra sentence.** I applied the first sentence of the suggestion and left out the second, because the lesson does not state it.

- Applied: "Sets 0.8 as the smallest accepted X chromosome F value for a recorded male. F measures how homozygous the X chromosome looks."
- Not applied: "Values near 1 indicate the pattern expected when there is one X chromosome copy."
- Supported by the lesson: no. PLINK's sex-check documentation supports it. Add it if you agree.

**3. Step 4.5, `--export A`.** Changes a scientific statement.

- Original: "Writes a table of allele counts, recorded as 0, 1 or 2 copies of a DNA version for each person and variant."
- Reviewer: for chromosomes present in one copy, PLINK scales the values, so the numbers are not literal copy counts.
- Suggested: "Writes a table with one row per person and values of 0, 1 or 2 for each variant. For chromosomes present in one copy, PLINK scales the values to 0 or 2, so 2 does not mean two physical copies."
- Supported by the lesson: no. The lesson also calls these values copy counts. I could not confirm the scaling rule from memory, so check the PLINK 2 `--export` page before you decide.

### E. Render check of the nine `.Rmd` notebooks (no code run)

- Tool: `rmarkdown::render` with chunk evaluation off, pandoc from RStudio's Quarto folder. Output in `notebooks/render_check/` (untracked, excluded in `.git/info/exclude`).
- Result: all nine notebooks rendered without errors. The only message is a pandoc deprecation notice (`--no-highlight`) from the installed `rmarkdown`. It does not come from the course.
- Chunk labels: no duplicates (the complete notebook has 65 chunks).
- Tables: every pipe table became an HTML table. The complete notebook has 41 pipe tables and 45 HTML tables, and no raw pipe line was left in the HTML.
- Headings: no level is skipped in any notebook.
- Internal links: every `../docs/glossary.md#...` anchor exists in the glossary (385 anchors, none missing). These links only work when the notebook stays in the project folder.
- Generator problems: none found.
- Not checked: the look of the pages in RStudio's notebook viewer, and the first-chunk behaviour when someone opens a notebook outside the project root (the check chunk handles `..`).

### F. Link check

I requested all 64 step-page URLs of the form `https://www.manuelgentiluomo.it/teaching/gwas/module-N/step-N-M`, following redirects. All 64 returned 200, and a made-up page returned 404, so the 200 values are real. Also 200: the data-access form, the project ZIP of release `project-2026.1`, the Posit download page, CRAN and the PLINK 2 page.

### G. How to open `compare.html`

1. Open the file `C:\GWAS_course\notebooks\render_check\compare.html` in a browser (double-click).
2. Each row links to the `.Rmd` HTML and to the `.qmd` HTML of one notebook. The `.qmd` pages are in `C:\GWAS_course\notebooks_qmd\html\`.
3. To regenerate everything after a change in a lesson:
   - `python -B scripts/build_tutorial.py --export-notebooks notebooks_qmd --notebook-format qmd`
   - in `notebooks_qmd`: `quarto render <file>.qmd --no-execute`, then move the HTML files into `html/`
   - the `.Rmd` pages: the render script in the scratchpad of this session (not versioned): `rmarkdown::render` for each notebook with `knitr::opts_chunk$set(eval = FALSE)`.
4. To make Quarto the default later, change one line: `DEFAULT_FORMAT = "rmd"` in `scripts/student_notebooks.py`. Three other places must follow: the allowlist pattern `NOTEBOOK_NAME` in `scripts/package_project.py` (it accepts only `.Rmd`), the freshness check in the tests (they check the default format), and the notebook paths named in `CLAUDE.md`. I changed none of them.
5. The `.qmd` files differ from the `.Rmd` files in four ways: numbered comments become code annotations with the explanation list under the chunk, "Expected result" is a collapsed tip callout, "PLINK terminal equivalent" is a note callout, and the front matter has `editor: visual`.

### H. Project ZIP

Built twice into temporary folders outside the repository and deleted afterwards. Nothing was published.

| Build | Files | ZIP size | Uncompressed |
| --- | --- | --- | --- |
| `notebooks/all-modules`, no programs | 61 | 258,339 bytes | 881,364 bytes |
| `plink/bundle`, `--plink-cache` with the four pinned archives | 75 | 21,506,382 bytes | 75,437,395 bytes |

Contents of the first build: 8 lessons, 9 notebooks, 4 files in `R/`, 4 in `scripts/`, 5 in `docs/`, 25 invented format examples (one of them is the invented `.pgen`, which is allowed), `config.R`, the project file, the README and the two licence files. The nine notebooks are inside. No `.qmd`, no HTML, no render folder, no archive and no program is inside. The link checker of the packager validated every local link, including the glossary anchors used by the notebooks. On `plink/bundle` the second build adds `R/plink_setup.R`, the pin list, the licence texts and the four programs (mode 0755, Unix creation system).

### I. PLINK groundwork (branch `plink/bundle`)

Status: items 2 to 4 of the plan are done. Item 1 (the comparison run at the office), the Apple Silicon check, the module 0 text, `LICENSE-CONTENT.md`, `bin/README.md`, `docs/troubleshooting.md` and the manual-download rule in `CLAUDE.md` are not done, as you asked.

**Pins to verify.** All four are "first pin, to be verified by the author against the official page". I downloaded each archive once on 15 November 2026 from `https://s3.amazonaws.com/plink2-assets/beta1/`. A hash taken at the first download detects later changes. It does not prove that the first file was genuine.

| Platform | Archive SHA-256 | Executable SHA-256 |
| --- | --- | --- |
| windows-x86_64 | `0a7c1bff1d5a3a7a01a27f789c4fbd92f7631c7ed27fd376b8c36fe2cf6f3f48` | `b57537f14734f15325bf2dd5d2de431308e025a66cabc1b1494249ee1d7142b9` |
| macos-arm64 | `6027138e618e3b4978950c2a3fd5e1015c66349a90b037843129192bcbf87efe` | `e6d321565e2a4fd20874a7c21ac6c2cfe3e0802549bdffdfbe9623438cd6bf4a` |
| macos-x86_64 | `6a16027c51a86bd8efba31f2eb4f7dbdbbe331001006109c79ce303e6870e3ec` | `0564701a0efe3a91bf2b5fac430efc84779e65e92675af4cfcc31e6d034d981b` |
| linux-x86_64 | `16b5cf92faed7e8b8aa1010c6eab9bac17c92b57ccfa69c4d059b1b17b98eb70` | `93ab85dde8743b76e815a84a13bc6e62650148cb6abf785e1909c8d08c589dcc` |

- Only the Windows program was run: `plink2.exe --version` printed `PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)`. The other three were not run (they need their own systems).
- Source tag `v2.0.0-b.1.4` resolves on GitHub to commit `760ee7329e8914de52f75a4e470cecabccbde0d9`, as in the plan.
- Each archive also holds `ldsc`, `mtag` and `vcf_subset`. They are not extracted. The Linux archive holds `intel-simplified-software-license.txt`, which I included in `third_party/plink2/notices/`.
- Licence texts from the source tag (commit above): `COPYING` (GPL 3), `COPYING.LESSER`, `LICENSE.QD`, and the notices of libdeflate, simde and zstd. The plan asks you to check the dependency notices against the four binaries before release. I did not do that.

**Item 2, `R/plink_setup.R`.** `prepare_course_plink()` picks the pin row from the system and the CPU (Apple Silicon under Rosetta uses the arm64 build), checks every SHA-256, copies the program to `bin/`, sets mode 755 on macOS and Linux and runs `--version`. It never replaces a different program in `bin/`. It stops with a clear message on Windows ARM, Linux ARM, 32-bit R, musl, glibc older than 2.31 and unknown systems. Failure help covers macOS quarantine (`xattr -d com.apple.quarantine bin/plink2`, never run for the student) and "Kernel too old". The tests use fake programs and fake archives. They never use the network. I also ran it for real on this Windows PC with the real pin list and download: it prepared the program and the second call reported "already ready".

**Item 3, packager.** `--plink-cache DIR` (outside Git) downloads when missing, checks the archive hash and size before it opens the archive, rejects absolute paths, `..`, backslashes and drive letters, reads only the named member, checks the program hash and size, and adds the program with mode 0755. A cached archive with a wrong hash is never trusted. Without the option no program is added. Tracked programs or archives stop the build, `.gitignore` lists the program names, and `scripts/tests/test_plink_pins.py` fails if any tracked file is a program, an archive or has an executable or ZIP header.

**Not yet connected.** Step 0.6 still tells students to download PLINK by hand. Nothing calls `prepare_course_plink()` yet. The R helper looks for a packaged program in `third_party/plink2/programs/<platform>/` first and downloads the pinned archive otherwise.

### J. Test results (Windows 11, this machine)

- `notebooks/all-modules`: `python -B -m unittest discover -s scripts/tests -p "test_*.py"`: 62 tests, OK, 1 skipped (the encrypted release round trip needs a password and 7-Zip).
- `plink/bundle`: 76 tests, OK, 1 skipped (same test).
- `python -B scripts/build_tutorial.py --export-notebooks notebooks --check-notebooks`: nine notebooks up to date after every commit.
- `scripts/author/prove_comment_only.py --base <previous commit>`: passed after the module 7 restart commit, the 6.6 commit and the Phase B corrections. The 6.6 commit and the Phase B commit change text outside chunks or inside `step_meta` comments only.
- `scripts/tests/test_guided_module_check.R`: passed.
- `scripts/tests/test_plink_setup.R`: passed (on `plink/bundle`).
- `scripts/check_course.R`: passed.
- Quarto: nine `.qmd` files rendered with `--no-execute` without errors (the module 3 page shows 83 code annotation markers).
- Not run: any analysis on course data, PLINK on course data, the R notebooks (no data on this machine), macOS, Linux, the other three PLINK builds, the comparison run against `answer_key.json`.

### K. Commits

`notebooks/all-modules` (pushed), after the earlier review commit `1cb8f9f`:

- `d4b6c2d` Point the module 7 restart advice to restore_checkpoint("6.1") and module 6
- `88ac93c` Align the step 6.6 terminal command with the R code (--snp) and drop the special validator rule
- `2777593` Add an optional Quarto (qmd) renderer behind --notebook-format qmd
- `5113726` Correct student summaries and option explanations after an independent review
- `7580bfc` Ship the nine student notebooks in the project ZIP allowlist
- the commit that adds this section

`plink/bundle` (created from `7580bfc`, pushed):

- `5a228cf` Pin the four PLINK 2 Beta 1.4 builds and add the licence texts
- `335e1bf` Add prepare_course_plink() to select, verify and install the pinned PLINK 2 program
- `32c9912` Packager: add pinned PLINK 2 programs from an outside-Git cache, with hash, path and permission checks

`plink/bundle` does not contain this review section. Merge `notebooks/all-modules` into it, or the other way round, when you decide.

### L. Where I stopped

All phases A to G are done. No usage limit stopped the work. Untracked and left alone: `notebooks/experiment_html/`, `notebooks/module_03_sample_quality_control.qmd` (your earlier Quarto experiment), and the excluded folders `notebooks/render_check/` and `notebooks_qmd/`. Nothing was merged into `course/2026-guided-training`. No release was created and the website repository was not synced.

---

## Earlier review (14 November)

Written for the author, Manuel Gentiluomo. Status: finished. Branch `notebooks/all-modules` (local only, not pushed, not merged). Date of the work: 14 November 2026.

Everything in this file was produced while you were away. Nothing was executed on course data: this machine has no `data/course` folder and no PLINK. The notebooks were generated and checked, not run.

## 1. Read these first

1. **Module 7 restart advice (section 3, item 1).** `restore_checkpoint("7.1")` cannot rebuild the files that module 7 needs. The error message that students see in module 7 names that command anyway. Decide what module 7 should say.
2. **Module 0, steps 0.1, 0.2, 0.3 and 0.6 (outside R).** The "What you do" sentences tell students exactly where to download and extract. Check them against what you teach, for example the extraction folder in 0.3.
3. **Step 2.6 and step 6.6 option tables.** In both steps the R code builds the PLINK command in a way that differs from the terminal example. Step 2.6 adds `--flip` only when sites map to the opposite strand. Step 6.6 selects the variant with `--snp` in R and with `--extract` in the terminal. Codex taught the exporter to accept exactly these two patterns. Read those two tables and the validator change (section 3, item 3).
4. **Steps 3.4, 5.4, 5.6, 5.7, 6.2, 6.3 and 7.1 to 7.4.** These summaries explain statistics (pruning, PCA, standard deviations, logistic model, QQ plot, lambda, thresholds). Check that each plain explanation is correct and not too short.
5. **Prerequisite file lists** (section 2, item 5). They decide when the check chunk stops a student. A missing file in the list blocks a correct run. An extra file blocks it too.
6. **The complete notebook**, `notebooks/gwas_course_complete.Rmd`. Its structure is in section 2, item 7.

## 2. Decisions taken without asking (most conservative option)

1. **Order of work.** Items 0a to 0c were committed on `course/2026-guided-training` and that branch was pushed. The push also sent two earlier local commits (`39d60f4` line endings and `3891a22` release work folder) that you had approved but that were not yet on GitHub. Everything after that is on the local branch only.
2. **Generator before modules.** I generalised the generator first (commit `394e90d`), with the module 3 notebook byte-identical, then added the modules one at a time.
3. **Step kinds.** A step without an R chunk must be `reading` (summary and link) or `outside_r` (summary, link, "No code to run in this step" and a "What you do" sentence). Steps 0.1, 0.2, 0.3 and 0.6 are `outside_r`. Steps 1.8 to 1.11 are `reading`. All other steps are code steps, even when they use no PLINK option (their table says "No PLINK options are used in this step").
4. **Module 0 check.** Module 0 needs only the project root. Its check is an inline base R chunk, because step 0.5 installs the packages that `R/guided.R` could need. It has no `module_meta`.
5. **Prerequisites** (generated into `R/guided.R` from `module_meta`):
   - Modules 1 and 2: data files only, no checkpoint.
   - Module 3: checkpoint 2.8. Module 4: checkpoint 3.8 (state files only). Module 5: checkpoint 4.6 plus the three PCA reference files. Module 6: checkpoint 5.7 plus the PC file and two metadata files. Module 7: the files it reads at the start (association result, summary statistics, covariates, state files, step counts, checkpoint index, and the 2.8 files for the no-QC comparison).
   - Codex listed only files that exist when the module starts and left out files the module creates. `software_versions.txt` is excluded because setup creates it.
6. **Verification paragraphs.** The paragraphs that start "The tested PLINK version ..." are wrapped in `verification_note` markers, so the notebook shows the expected result without them. No text was invented where a step had no such paragraph.
7. **Complete notebook layout.** One header, one introduction, then for each module a level 1 heading, its check chunk, the shared setup chunk once (first needed in module 1) and the step blocks. Module introductions are not repeated.
8. **Comments.** Numbered comments restart at 1 in each chunk. The bookkeeping comment appears once per block of bookkeeping lines. The long teaching comment in step 6.8 is untouched.
9. **Tests I changed because they assumed the old state** (not generator bugs): a test that compared the code of step 0.7 literally now ignores comment lines; a test that expected module 3 to be the first enabled module now looks for it; a test that inserts metadata into step 1.8 now first removes the lesson's own metadata from its temporary copy.
10. **Validator changes by Codex**, kept because each one blocked a real step and has a regression test: the option registry knows the modifiers `midp`, `A`, `exclude-mismatch`, `list`, the PCA and scoring modifiers and the `--glm` modifiers; two narrow rules for step 2.6 (conditional `--flip`) and step 6.6 (`--snp` with `--extract`).
11. **Quarto.** The renderer layer is a registry. Adding `.qmd` later means adding one function. Nothing Quarto-related is in the commits. The untracked `.qmd` experiment and `notebooks/experiment_html/` were left alone.

## 3. Items that need your decision

1. **Module 7 restart.** `restore_checkpoint("7.1")` does not recreate the counts file or the working checkpoint index, and full genotype copies exist only at 2.8, 3.8, 4.6 and 5.7. The generated message for module 7 still tells students to run it. Options: (a) change the message for module 7 to point to the instructor or to step 6.8; (b) extend `restore_checkpoint` for a 6.8 restart. I changed nothing.
2. **Data-only modules.** Modules 1 and 2 have no checkpoint, so a missing data file points to step 0.7 only.
3. **Validator rules for steps 2.6 and 6.6** are regular expressions on the R code. They are narrow, but they are code that only checks documentation. If the lessons change, they may need an update. Alternative: remove the conditional pieces from the tables and mention them in the text.
4. **The notebooks were not rendered or run.** I read the generated text. Open at least modules 3 and 6 in RStudio and render them.

## 4. Steps skipped

None. Every step of modules 0 to 7 has student fields. Nothing was skipped for safety.

## 4b. Test results (Windows, this machine, final state of the branch)

- `python -B scripts/build_tutorial.py --export-notebooks notebooks --check-notebooks`: passed, nine notebooks (eight modules and the complete notebook).
- `python -B scripts/author/prove_comment_only.py --base <previous commit>`: passed after every module. Lesson chunks, `scripts/run_main_path.R` and `r_commands` in the site JSON differ only by comment lines and source hashes.
- Stronger check at the end: for modules 0, 1, 2 and 4 to 7, the R code of every chunk was parsed at commit `394e90d` and now. The parsed expressions are identical in all seven lessons. Module 3 was proved against its pre-comment commit earlier.
- All R chunks of the lessons, the nine notebooks and `scripts/run_main_path.R` parse without error.
- `python -B -m unittest discover -s scripts/tests -p "test_*.py"`: 54 tests, OK, 1 skipped (the encrypted release round trip needs a password and 7-Zip).
- `scripts/tests/test_guided_module_check.R`: passed (data-only, checkpoint, root-only and unknown modules).
- `scripts/check_course.R`: passed with `LC_CTYPE` set to `English_United Kingdom.utf8`. With the inherited locale a UTF-8 fixture fails, as before.
- Not run: any analysis on course data, PLINK, the R notebooks, the rendered HTML, macOS and Linux.

## 5. Drafted summaries and option tables, module by module

Read the summary of each step and its option tables. The R code, comments and expected results are in the notebooks (`notebooks/module_NN_*.Rmd`). Tables list the options in command order, with modifiers under their parent.


### Module 0: Prepare your computer


#### Step 0.1 · Install R

We install R, the program that runs the course commands. We choose the version that matches the computer's system and processor.


Outside R. What you do: Check your system and processor in the computer's settings, then open the official CRAN page and follow the installation instructions for Windows, macOS or your Linux distribution. Open R and check that its window appears.


#### Step 0.2 · Install RStudio

We install RStudio, a program that makes R easier to use. We find the Console area where we will run commands.


Outside R. What you do: Download RStudio Desktop for your system from the official Posit page and follow its installation instructions for Windows, macOS or Linux. Open RStudio and find the Console area with a `>` prompt.


#### Step 0.3 · Download and extract the project

We download and extract the complete course project. Keeping its files together lets the commands find the files they need.


Outside R. What you do: Download GWAS_course-2026.1.zip and extract it under C:/ on Windows or your home folder on macOS or Linux, using your system's extraction tool. Open the supplied GWAS_course folder and check that it contains config.R, GWAS_course.Rproj, R, lessons and scripts.


#### Step 0.4 · Open the project and check R

We open the course project and check that R can find its files. We display the system and R version, then try a small calculation to check that commands run.


No PLINK options in this step.


#### Step 0.5 · Install the R packages

We install the R packages, which add functions needed by the course. These prepare R to ask for a hidden password and check the downloaded files.


No PLINK options in this step.


#### Step 0.6 · Put PLINK 2 in bin/

We download PLINK 2, the program that analyses the DNA data. We put its program file in the course folder so R can find and run it.


Outside R. What you do: Download the latest PLINK 2 build that matches your system and processor from the official page, then extract the ZIP file. Copy only plink2.exe on Windows, or plink2 on macOS or Linux, into the project's bin/ folder.


#### Step 0.7 · Request the password and download the data

We request the password, then download and check the course data. We enter the password only in a prompt that hides the letters; we never type it into a file.


No PLINK options in this step.


#### Step 0.8 · Run the setup check

We run the setup check to test the R packages, data files and PLINK 2. PLINK reads 20 DNA positions and writes a report, including a test in a folder whose name contains spaces and non-English letters.


| Option or modifier | What it does |
| --- | --- |
| `--bfile` | Reads the BED, BIM and FAM input files named sim2026_lab in data/course/lab_export/. |
| `--autosome` | Keeps only DNA positions on chromosomes 1 to 22. |
| `--thin-count` | Selects 20 DNA positions at random for this small test. |
| `--seed` | Uses 20261111 as the starting number for the random selection so it can be repeated. |
| `--freq` | Writes a report showing how common each version of a DNA letter is at the selected positions. |
| `--out` | Starts the report file names with results/guided/s0-8_probe in the standard project layout; the helper also tests a folder name with spaces and non-English letters. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


### Module 1: From DNA to array data


#### Step 1.1 · SNPs and genotypes

We read a table describing the DNA sites measured by the array. We count its rows and look at site names, chromosome positions and possible DNA letters to understand what the array measures.


No PLINK options in this step.


#### Step 1.2 · How an array measures DNA

We find the three laboratory report files and read the first 12 lines of the first report. This shows how the laboratory organises information before we read the recorded DNA results.


No PLINK options in this step.


#### Step 1.3 · The Global Screening Array

We count the array entries on each chromosome. We also check that the table has 299,523 rows and no repeated site names, so we can recognise the expected starting data.


No PLINK options in this step.


#### Step 1.4 · From sample to scanned chip

We read the sample sheet and count measurements on each laboratory plate. We count labelled repeat measurements and check that the sheet has 2,016 rows, because one person can have more than one measurement.


No PLINK options in this step.


#### Step 1.5 · Calling genotypes

We read the data section of a laboratory report and display its first rows. We summarise the GC scores, which describe the quality of recorded DNA results, to see what information the report provides.


No PLINK options in this step.


#### Step 1.6 · Problems born in the laboratory

We check that the sample sheet includes plate, well, sample and repeat-measurement labels, then display its first rows. These labels help us investigate laboratory problems during later checks.


No PLINK options in this step.


#### Step 1.7 · The export

We check that the three genotype files belong together and display their sample and DNA site counts. We confirm that they contain 2,016 sample wells and 299,523 sites before we begin the analysis.


No PLINK options in this step.


#### Step 1.8 · Where genetic data come from

We compare arrays, sequencing and predicted genotypes, which estimate unmeasured DNA results using a reference group. We read what each source measures and misses so we can understand which questions its data can answer.


Reading only. Summary and link.


#### Step 1.9 · A map of genetic file formats

We follow genetic files from laboratory measurements to analysis results. We compare what the formats store and the checks they need so we can choose suitable files and avoid mixing incompatible information.


Reading only. Summary and link.


#### Step 1.10 · The formats you will meet most often

We read small invented examples to learn what common genetic file fields mean. We examine example conversion commands without running them, so we can understand what conversions preserve and what they may lose.


Reading only. Summary and link.


#### Step 1.11 · How large projects share genetic data

We read how large research projects provide genetic data in several formats. We compare the information each format retains and the work it supports to understand why one study may supply several kinds of files.


Reading only. Summary and link.


### Module 2: Files and formats


#### Step 2.1 · The starting files

We check that the three laboratory files are present and have matching sizes. We also look at the sample identifiers so we can recognise the starting data.


No PLINK options in this step.


#### Step 2.2 · Convert to PLINK 2 native format

We convert the laboratory files to the format that PLINK 2 uses for this course. We check that the conversion keeps every sample and variant, a place in the DNA where people can differ.


| Option or modifier | What it does |
| --- | --- |
| `--bfile` | Reads the BED, BIM and FAM laboratory files named sim2026_lab in data/course/lab_export. |
| `--make-pgen` | Writes the data as PGEN, PVAR and PSAM files, the native PLINK 2 format. |
| `--out` | Starts the output file names with results/guided/s2-2_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 2.3 · Sample and variant tables

We read the tables that describe the samples and the DNA sites. We inspect their first rows and check the sample identifiers so we can match information to the right sample.


No PLINK options in this step.


#### Step 2.4 · First overview

We measure the share of missing DNA results for each sample and each site. These reports help us find possible problems before we choose what to remove.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s2-2_state. |
| `--missing` | Writes separate reports of missing DNA results for samples and variants without removing any data. |
| `--out` | Starts the report file names with results/guided/s2-4_missing. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 2.5 · Alleles and strand

We compare the DNA letters at each site with the supplied reference table. We correct 400 sites read from the opposite DNA strand and remove 3,013 sites whose letters cannot establish a clear match.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s2-2_state. |
| `--flip` | Uses s2-5_flip.txt to replace each DNA letter by its partner on the opposite strand at 400 sites: A pairs with T, and C with G. |
| `--exclude` | Removes the 3,013 sites listed in s2-5_exclude.txt because their DNA letter pairs are ambiguous or incompatible with the reference table. |
| `--make-pgen` | Saves the corrected data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the corrected file names with results/guided/s2-5_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 2.6 · Genome builds and lift-over

We convert the DNA positions in a separate exercise from the GRCh37 genome reference to GRCh38. We keep sites that map to the same chromosome, correct opposite-strand letters and check the new positions without changing the main dataset.


| Option or modifier | What it does |
| --- | --- |
| `--bfile` | Reads the BED, BIM and FAM files named data/course/grch37_exercise/legacy_grch37, containing 10,000 exercise sites. |
| `--extract` | Keeps the 9,970 sites listed in s2-6_mapped.txt that map to the same chromosome in GRCh38. |
| `--update-map` | Reads site identifiers and their new GRCh38 positions from the two columns of s2-6_update_map.tsv. |
| `--flip` | R adds this option when sites map to the opposite DNA strand, using s2-6_reverse.txt to correct the DNA letters at eight sites in this exercise. |
| `--make-pgen` | Saves the converted exercise as PGEN, PVAR and PSAM files. |
| `--out` | Starts the converted exercise file names with results/guided/s2-6_grch38. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 2.7 · Add phenotype and covariates

We match disease status, age and recorded sex to each laboratory well by its identifiers. We save the information table and add disease status and sex to the DNA files so later checks use the right person's information.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the corrected PGEN, PVAR and PSAM files named results/guided/s2-5_state. |
| `--update-sex` | Loads recorded sex from s2-7_phenotypes.tsv by matching the sample identifiers. |
| `--pheno` | Reads the table s2-7_phenotypes.tsv containing the sample identifiers and disease status. |
| `--pheno-name` | Selects the Disease column as the outcome: 1 means a control without the disease and 2 means a case with the disease. |
| `--make-pgen` | Saves PGEN, PVAR and PSAM files with recorded sex and disease status in the sample table. |
| `--out` | Starts the joined file names with results/guided/s2-7_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 2.8 · Module 2 checkpoint

We save a complete checked starting point for module 3, with 2,016 samples and 296,510 variants. This saved copy lets us restart the analysis without repeating module 2.


No PLINK options in this step.


### Module 3: Sample quality control


#### Step 3.1 · Rough cleaning

We remove samples and variants with very many missing calls. This first clean prevents the worst failures from distorting the checks that follow.


**Command 1: remove poor samples**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--mind` | Removes samples with more than 10% missing calls. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

**Command 2: remove poor variants**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--geno` | Removes variants with more than 10% missing calls in the input dataset. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.2 · Sample call rate

We remove samples with more than 2% of their genotype calls missing. This keeps samples with enough information for the later analysis.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--mind` | Removes samples with more than 2% missing calls, keeping a call rate of at least 98%. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.3 · Recorded and genetic sex

We compare recorded sex with patterns in the X and Y chromosome calls. We remove flagged wells from this teaching analysis because a mismatch needs review before the sample is used.


**Command 1: label the shared X and Y regions**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--split-par` | Uses GRCh38 boundaries (b38) to label the shared regions of X and Y separately. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

**Command 2: compare recorded sex with DNA**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--check-sex` | Compares recorded sex with X chromosome patterns and the number of observed Y calls. |
| &nbsp;&nbsp;&rarr; `max-female-xf` | Sets 0.2 as the largest X coefficient accepted for a recorded female. |
| &nbsp;&nbsp;&rarr; `min-male-xf` | Sets 0.8 as the smallest X coefficient accepted for a recorded male. |
| &nbsp;&nbsp;&rarr; `max-female-ycount` | Accepts at most 100 observed Y calls for a recorded female. |
| &nbsp;&nbsp;&rarr; `min-male-ycount` | Requires at least 1000 observed Y calls for a recorded male. |
| `--out` | Sets the shared beginning of the output file names. |

**Command 3: remove samples flagged by the sex check**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--remove` | Removes the samples named in the supplied sample list. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.4 · LD pruning

We pick a set of common variants that are not strongly linked to each other. The sample checks that follow need independent variants, otherwise the same genetic signal is counted many times.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--chr` | Uses only chromosomes 1 to 22, the autosomes. |
| `--maf` | Keeps variants whose less common allele has a frequency of at least 5%. |
| `--geno` | Keeps variants with no more than 2% missing calls. |
| `--exclude` | Leaves out variants within the listed DNA regions. |
| &nbsp;&nbsp;&rarr; `bed1` | Reads DNA regions with positions counted from 1 and includes both ends of each region. |
| `--indep-pairwise` | Selects a less strongly linked set within windows of 200 kb (200,000 DNA bases), using a squared correlation limit of 0.2. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.5 · Heterozygosity

We check whether each sample has unusually many or few genotypes with two different alleles. We remove the unusually high-heterozygosity samples and keep the low-heterozygosity samples flagged for review, because an unusual value alone does not prove an error.


**Command 1: measure matching DNA letters**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--extract` | Uses only the variants named in the supplied variant list. |
| `--het` | Reports how often each sample has two matching alleles, compared with what the allele frequencies predict. R uses this report to calculate F and the review thresholds. |
| `--out` | Sets the shared beginning of the output file names. |

**Command 2: remove samples with unusually few matching letters**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--remove` | Removes the samples named in the supplied sample list. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.6 · Relatedness and duplicates

We compare pairs of samples to find repeated measurements and close relatives. We apply the stated removal rules so that repeated or closely related people do not distort the later association analysis.


**Command 1: compare pairs of samples**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--extract` | Uses only the variants named in the supplied variant list. |
| `--make-king-table` | Estimates how closely related each pair of samples is and writes a table. |
| `--king-table-filter` | Writes only pairs with estimated kinship above 0.0442, an approximate screening boundary for third-degree relatives such as first cousins. |
| `--out` | Sets the shared beginning of the output file names. |

**Command 2: remove repeated or closely related samples**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--remove` | Removes the samples named in the supplied sample list. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.7 · Batch effects

We compare the fraction of successful genotype calls across laboratory plates. We remove the faulty plate in these simulated data because samples processed together can share technical problems.


**Command 1: measure missing calls by sample**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--missing` | Writes a report of missing genotype calls. |
| &nbsp;&nbsp;&rarr; `sample-only` | Writes one row per sample and skips the report for variants. |
| `--out` | Sets the shared beginning of the output file names. |

**Command 2: remove samples from the faulty plate**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--remove` | Removes the samples named in the supplied sample list. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.8 · Sample QC summary and checkpoint

We save the complete dataset after sample quality control and review the recorded counts. This gives us a checked starting point for variant quality control in module 4.


No PLINK options in this step.


### Module 4: Variant quality control


#### Step 4.1 · Variant call rate

We remove variants with more than 2% of their results missing. This keeps sites in the DNA with results for at least 98% of the remaining people.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s3-8_state. |
| `--geno` | Removes variants with more than 2% of their genotype calls missing. |
| `--make-pgen` | Saves the remaining data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the output file names with results/guided/s4-1_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 4.2 · Differential missingness

We compare missing results in people with and without the disease to reduce false links with disease. We remove variants with p-values below 0.00001, which indicate differences that are very unlikely if missing results occur equally in both groups.


**Command 1: compare missing results**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-1_state. |
| `--test-missing` | Tests whether missing genotype calls differ between people with and without the disease. |
| `--out` | Starts the test report file names with results/guided/s4-2_missing. |

**Command 2: remove variants with unequal missing results**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-1_state. |
| `--exclude` | Removes variants listed in results/guided/s4-2_exclude.txt because their missingness test p-value is below 0.00001. |
| `--make-pgen` | Saves the remaining data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the output file names with results/guided/s4-2_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 4.3 · Allele frequency

We keep variants whose less common DNA version appears in at least 1% of the chromosome copies. This removes variants with too little information for the main disease analysis.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-2_state. |
| `--maf` | Removes variants whose less common allele, or DNA version, appears in fewer than 1% of chromosome copies. |
| `--make-pgen` | Saves the remaining data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the output file names with results/guided/s4-3_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 4.4 · Hardy-Weinberg and sample size

We test whether DNA letter combinations on chromosomes 1 to 22 follow expected proportions in people without the disease. We remove variants that fail a rule based on the number of people tested, to reduce possible measurement errors.


**Command 1: test expected DNA letter combinations**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-3_state. |
| `--keep` | Uses only people without the disease, listed in results/guided/s4-4_controls.txt, for this test. |
| `--chr` | Limits the test to chromosomes 1 to 22. |
| `--hardy` | Tests whether genotype proportions, the shares of each DNA letter combination, match Hardy-Weinberg expectations. |
| &nbsp;&nbsp;&rarr; `midp` | Uses the mid-p version of the exact test, which adjusts for the limited possible outcomes of whole-number counts. |
| `--out` | Starts the test report file names with results/guided/s4-4_hardy. |

**Command 2: remove variants that fail the test**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-3_state, including people with and without the disease. |
| `--exclude` | Removes variants listed in results/guided/s4-4_exclude.txt after R applies the cutoff 10^(-6 - 0.001 * max(0, n_control - 1000)), where n_control counts people without the disease who have a result at that variant. |
| `--make-pgen` | Saves the remaining data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the output file names with results/guided/s4-4_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 4.5 · Sex chromosomes, MT and duplicated sites

We remove variants on X, Y and mitochondrial DNA with unexpected results in more than 1% of people checked. We then rename variants by their DNA location and letters, keep one copy of matching duplicates and remove copies that disagree.


**Command 1: export chromosome results for checking**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-4_state. |
| `--chr` | Selects only X, Y and MT, the mitochondrial chromosome. |
| `--export` | Writes genotype data in a text format for R to read. |
| &nbsp;&nbsp;&rarr; `A` | Writes a table of allele counts, recorded as 0, 1 or 2 copies of a DNA version for each person and variant. |
| `--out` | Starts the export file names with results/guided/s4-5_sexchr. |

**Command 2: remove variants with unexpected chromosome results**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-4_state. |
| `--exclude` | Removes variants listed in results/guided/s4-5_exclude.txt because more than 1% of the people checked have unexpected results on X, Y or MT. |
| `--make-pgen` | Saves the remaining data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the output file names with results/guided/s4-5_sex_state. |

**Command 3: rename variants and remove duplicate entries**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-5_sex_state. |
| `--set-all-var-ids` | Names each variant with @:#:$r:$a: chromosome, position, reference DNA version and alternative DNA version, separated by colons. |
| `--rm-dup` | Finds entries with the same variant name and keeps one copy when they match. |
| &nbsp;&nbsp;&rarr; `exclude-mismatch` | Removes all copies of a duplicated variant when their records disagree. |
| &nbsp;&nbsp;&rarr; `list` | Writes a list of the duplicated variant names. |
| `--make-pgen` | Saves the remaining data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the output file names with results/guided/s4-5_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 4.6 · Variant QC summary and checkpoint

We save a complete checked starting point for module 5. We check the saved files and counts so we can restart from the same data later.


No PLINK options in this step.


### Module 5: Population structure


#### Step 5.1 · Why ancestry matters

We count the reference samples in each labelled group. These groups help us compare inherited genetic backgrounds and understand how differences between cases and controls can create false disease associations.


No PLINK options in this step.


#### Step 5.2 · Prepare variants for reference PCA

We find and save the 48,614 sites present in both the cleaned study and the reference. We need the same sites to compare genetic patterns in the two groups.


No PLINK options in this step.


#### Step 5.3 · Match build, position and alleles

We check that each shared site has the same chromosome, DNA position and pair of alleles, the alternative DNA letters, in both files. This prevents us from comparing different sites that happen to share a name.


No PLINK options in this step.


#### Step 5.4 · Reference PCA and study projection

We calculate ten principal components in the reference, each a number summarising one pattern of genetic variation. We then project both groups onto these fixed reference axes, meaning we place them on the same scale so we can compare them.


**Command 1: calculate reference components and allele weights**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the reference genotype files pca_reference/ref1000g_grch38.pgen, .pvar and .psam from the course data folder. |
| `--extract` | Uses only the 48,614 shared sites listed in s5-2_common.txt. |
| `--freq` | Saves how common each allele is in the reference to s5-4_reference.afreq. |
| `--pca` | Calculates ten principal components, each a number per person summarising one pattern of genetic variation. |
| &nbsp;&nbsp;&rarr; `allele-wts` | Saves how much each allele contributes to each component in s5-4_reference.eigenvec.allele. |
| `--out` | Starts the reference output file names with s5-4_reference. |

**Command 2: place reference samples on the fixed axes**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the reference genotype files pca_reference/ref1000g_grch38.pgen, .pvar and .psam from the course data folder. |
| `--extract` | Uses only the 48,614 shared sites listed in s5-2_common.txt. |
| `--read-freq` | Reads the reference allele frequencies from s5-4_reference.afreq so both groups use the same scale. |
| `--score` | Uses s5-4_reference.eigenvec.allele to calculate reference scores, matching variant names in column 2 and counted alleles in column 5. |
| &nbsp;&nbsp;&rarr; `header-read` | Reads the first row of the allele weight file as column names. |
| &nbsp;&nbsp;&rarr; `no-mean-imputation` | Leaves missing genotype calls out of each average instead of replacing them with an average genotype. |
| &nbsp;&nbsp;&rarr; `variance-standardize` | Rescales genotypes using the reference allele frequencies so common and rare alleles contribute on a comparable scale. |
| `--score-col-nums` | Uses columns 6 to 15 of the allele weight file to calculate scores for PC1 to PC10. |
| `--out` | Starts the reference score output file names with s5-4_ref_scores. |

**Command 3: place study samples on the fixed axes**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the cleaned study genotype files s4-6_state.pgen, .pvar and .psam from the results folder. |
| `--extract` | Uses only the 48,614 shared sites listed in s5-2_common.txt. |
| `--read-freq` | Reads the reference allele frequencies from s5-4_reference.afreq so both groups use the same scale. |
| `--score` | Uses s5-4_reference.eigenvec.allele to calculate study scores, matching variant names in column 2 and counted alleles in column 5. |
| &nbsp;&nbsp;&rarr; `header-read` | Reads the first row of the allele weight file as column names. |
| &nbsp;&nbsp;&rarr; `no-mean-imputation` | Leaves missing genotype calls out of each average instead of replacing them with an average genotype. |
| &nbsp;&nbsp;&rarr; `variance-standardize` | Rescales genotypes using the reference allele frequencies so common and rare alleles contribute on a comparable scale. |
| `--score-col-nums` | Uses columns 6 to 15 of the allele weight file to calculate scores for PC1 to PC10. |
| `--out` | Starts the study score output file names with s5-4_study_scores. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 5.5 · Plot the reference and projected study

We plot the first two principal components, each a number summarising one pattern of genetic variation. We show reference groups with labels and symbols and add the study samples to see how their genetic backgrounds compare.


No PLINK options in this step.


#### Step 5.6 · Define an ancestry-matched cohort

We remove study samples more than six standard deviations from the European reference mean on any of the first four components. Standard deviations measure the spread of the reference scores; this rule defines the group for our teaching analysis.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the cleaned study genotype files s4-6_state.pgen, .pvar and .psam from the results folder. |
| `--remove` | Removes the samples listed in s5-6_remove.txt because at least one of their first four component scores is more than six standard deviations from the European reference mean. |
| `--make-pgen` | Saves the retained 1,811 samples and 238,513 variants as PGEN, PVAR and PSAM files. |
| `--out` | Starts the retained study output file names with s5-6_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 5.7 · Cohort PCs and how many to include

We select common sites with weaker links and calculate ten principal components, each a number summarising one pattern of genetic variation within the retained study group. We plot the variation each explains and save a complete checked starting point for module 6.


**Command 1: select common sites with weaker links**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the retained study genotype files s5-6_state.pgen, .pvar and .psam from the results folder. |
| `--chr` | Uses only chromosomes 1 to 22, the autosomes. |
| `--maf` | Keeps sites whose less common allele has a frequency of at least 5%. |
| `--exclude` | Leaves out sites within the regions listed in s3-4_high_ld.bed1, where distant sites can carry similar genetic information. |
| &nbsp;&nbsp;&rarr; `bed1` | Reads region positions counted from 1 and includes both ends of each region. |
| `--indep-pairwise` | Selects sites with weaker links within windows of 200 kb (200,000 DNA bases), using a squared correlation limit of 0.2. |
| `--out` | Starts the site selection output file names with s5-7_prune. |

**Command 2: calculate components within the retained study group**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the retained study genotype files s5-6_state.pgen, .pvar and .psam from the results folder. |
| `--extract` | Uses only the sites listed in s5-7_prune.prune.in, selected to have weaker links to each other. |
| `--pca` | Calculates ten principal components, each a number per person summarising one pattern of genetic variation in the retained study group. |
| `--out` | Starts the component output file names with s5-7_pca. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


### Module 6: Association


#### Step 6.1 · One variant by hand

We count cases and controls who carry at least one copy of a chosen DNA letter at one variant. We compare their odds of disease with those of non-carriers; odds are the number of cases divided by the number of controls.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads s5-7_state.pgen, .pvar and .psam, which hold the final study genotypes and sample details. |
| `--snp` | Selects only the variant named 9:96426973:A:G. |
| `--export` | Uses A format to write a .raw table with the number of copies of the named allele (DNA version) for each sample. |
| &nbsp;&nbsp;&rarr; `A` | Writes one row per sample with allele copy counts of 0, 1 or 2, keeping missing values separate. |
| `--out` | Starts output file names with s6-1_example, including the s6-1_example.raw table. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 6.2 · The additive logistic model

We fit a logistic model, which describes the probability of being a case, using the number of copies of one DNA letter. We calculate how each extra copy changes the odds of disease, the ratio of cases to controls.


No PLINK options in this step.


#### Step 6.3 · Prepare covariates

We prepare covariates, extra factors used to adjust the disease comparison: age and ten numbers describing patterns of genetic variation. We match them to sample IDs and check for missing values and columns that repeat information from other columns.


No PLINK options in this step.


#### Step 6.4 · Run the association scan

We test variants whose less common DNA version occurs at a frequency of at least 1% in the final study group. We adjust for age, sex and ten numbers describing genetic variation, then check and save the results.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads s5-7_state.pgen, .pvar and .psam, which hold the final study genotypes and sample details. |
| `--maf` | Keeps variants whose less common allele (DNA version) has a frequency of at least 1% in the final study group. |
| `--covar` | Reads s6-3_covariates.tsv, matching age and genetic component scores to samples by their IDs. |
| `--covar-name` | Selects Age and PC1 to PC10 as extra factors to adjust the disease comparison; each PC describes one pattern of genetic variation. |
| `--covar-variance-standardize` | Rescales the numerical adjustment factors to mean zero and variance one, a common scale that helps the model calculation remain stable. |
| `--glm` | Fits a logistic model at each variant to estimate how each extra copy of the tested DNA version changes the odds of disease, the ratio of cases to controls. |
| &nbsp;&nbsp;&rarr; `sex` | Adds the recorded sex from s5-7_state.psam as an adjustment factor in the model. |
| &nbsp;&nbsp;&rarr; `hide-covar` | Reports the genetic tests without separate rows for the effects of age, sex and genetic component scores. |
| &nbsp;&nbsp;&rarr; `firth-fallback` | Uses Firth correction, which reduces bias with small groups, when the ordinary model calculation fails. |
| `--out` | Starts output file names with s6-4_association, including s6-4_association.Disease.glm.logistic.hybrid. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 6.5 · Read association output

We check model failure codes and calculate intervals that describe uncertainty in the estimated effects. We sort valid results by p-value, a measure of evidence against no effect, and save the first 20 with their tested DNA letters and sample counts.


No PLINK options in this step.


#### Step 6.6 · Sparse genotypes and Firth correction

We choose a tested variant with the lowest frequency of its less common DNA version and compare its ordinary model result with a forced Firth result. Firth correction reduces bias when groups are small, but it does not add information.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads s5-7_state.pgen, .pvar and .psam, which hold the final study genotypes and sample details. |
| `--extract` | Selects the single variant listed in s6-6_variant.txt, chosen for the lowest frequency of its less common DNA version among valid autosomal tests. |
| `--snp` | In the R command, selects the chosen variant by its exact ID instead of reading s6-6_variant.txt with --extract. |
| `--covar` | Reads s6-3_covariates.tsv, matching age and genetic component scores to samples by their IDs. |
| `--covar-name` | Selects Age and PC1 to PC10 as extra factors to adjust the disease comparison; each PC describes one pattern of genetic variation. |
| `--covar-variance-standardize` | Rescales the numerical adjustment factors to mean zero and variance one, a common scale that helps the model calculation remain stable. |
| `--glm` | Fits a logistic model at the selected variant to estimate how each extra copy of the tested DNA version changes the odds of disease, the ratio of cases to controls. |
| &nbsp;&nbsp;&rarr; `firth` | Always uses Firth correction, which reduces bias with small groups, rather than waiting for the ordinary model calculation to fail. |
| &nbsp;&nbsp;&rarr; `sex` | Adds the recorded sex from s5-7_state.psam as an adjustment factor in the model. |
| &nbsp;&nbsp;&rarr; `hide-covar` | Reports the genetic test without separate rows for the effects of age, sex and genetic component scores. |
| `--out` | Starts output file names with s6-6_firth for the forced Firth result. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 6.7 · First look and association checkpoint

We summarise the sample and variant counts, valid tests and results below the course significance threshold. We also measure whether test values are generally larger than expected without effects and save the key files in a checked checkpoint for restarting.


No PLINK options in this step.


#### Step 6.8 · Create the summary statistics file

We save the scan results in a standard table with one row per tested variant and a separate file explaining its columns. We read the saved table back and check its values and counts so the next plots use a verified file.


No PLINK options in this step.


### Module 7: Plots and reporting


#### Step 7.1 · QQ plot

We draw a QQ plot, which compares observed p-values with those expected by chance, using chromosomes 1 to 22. This helps us see whether most tests behave as expected and whether the strongest results stand out.


No PLINK options in this step.


#### Step 7.2 · Genomic inflation factor

We calculate lambda, a number that compares the middle of the test results with what chance predicts. We check that it is close to 1.016 and save it to help assess the results alongside the QQ plot.


No PLINK options in this step.


#### Step 7.3 · Manhattan plot

We draw a Manhattan plot, which shows the strength of each result at its position along chromosomes 1 to 22. We also check that eight variants have p-values below 0.00000005 to confirm the count of strong results.


No PLINK options in this step.


#### Step 7.4 · Multiple-testing thresholds

We compare rules for multiple testing, which means allowing for the many chances to obtain a false result. We count results below 0.00000005, below 0.05 divided by the number of valid tests, and below 0.05 after an adjustment for false discoveries.


No PLINK options in this step.


#### Step 7.5 · Clump correlated results

We group nearby variants whose DNA patterns are correlated, meaning they tend to vary together across people. We use the final cohort to measure this similarity and check that the significant results form three groups.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads s5-7_state.pgen, s5-7_state.pvar and s5-7_state.psam, which hold the final cohort's DNA calls, variant information and sample information. |
| `--clump` | Reads s6-4_association.Disease.glm.logistic.hybrid and groups nearby association results whose DNA patterns are correlated across samples. |
| `--clump-id-field` | Uses the ID column of the association report to identify variants. |
| `--clump-p-field` | Uses the P column of the association report for p-values, which measure how unusual each result would be without an effect. |
| `--clump-p1` | Allows a variant to lead a group when its p-value is at most 5e-8 (0.00000005). |
| `--clump-p2` | Lists other variants in a group when their p-values are at most 1e-5 (0.00001). |
| `--clump-r2` | Adds variants whose squared correlation with the group's strongest variant exceeds 0.1. |
| `--clump-kb` | Limits each group to variants within 250 kilobases, or 250,000 DNA positions, on either side of its strongest variant. |
| `--clump-unphased` | Calculates correlation from the number of copies of a DNA version at each variant, without assigning those copies to individual chromosomes. |
| `--out` | Starts output file names with s7-5_clump, including the grouped results in s7-5_clump.clumps. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 7.6 · Regional plot

We draw a detailed plot of the chromosome 9 region around variant 9:96426973:A:G. We show both the strength of each association and how closely its DNA pattern follows the strongest variant, using symbols and colours.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads s5-7_state.pgen, s5-7_state.pvar and s5-7_state.psam, which hold the final cohort's DNA calls, variant information and sample information. |
| `--chr` | Selects chromosome 9 for the regional comparison. |
| `--from-bp` | Starts the selected GRCh38 interval at DNA position 95926973. |
| `--to-bp` | Ends the selected GRCh38 interval at DNA position 96926973. |
| `--r2-unphased` | Reports squared correlations between the numbers of copies of DNA versions at pairs of variants, without assigning copies to individual chromosomes. |
| `--ld-snp` | Pairs variant 9:96426973:A:G with the other selected variants to measure their correlation with it. |
| `--ld-window-kb` | Limits pairs to variants within 500 kilobases, or 500,000 DNA positions, of variant 9:96426973:A:G. |
| `--ld-window-r2` | Sets the minimum reported squared correlation to 0 so weak correlations remain in the report. |
| `--out` | Starts output file names with s7-6_ld, including the correlation table s7-6_ld.vcor. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 7.7 · Compare without PCs and without QC

We repeat the association tests without genetic components, the numbers that summarise ancestry, and then without sample and variant quality checks as well. We compare counts and plots to see how these choices change the results.


**Command 1: Command 1: test the final cohort without genetic components**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads s5-7_state.pgen, s5-7_state.pvar and s5-7_state.psam, which hold the final cohort's DNA calls, variant information and sample information. |
| `--maf` | Tests only variants whose less common DNA version has a frequency of at least 0.01, or 1%, in the input cohort. |
| `--covar` | Reads s6-3_covariates.tsv and matches adjustment values to samples by their identifiers. |
| `--covar-name` | Selects only Age from the adjustment table, leaving out genetic component scores that summarise ancestry. |
| `--covar-variance-standardize` | Rescales age to have a mean of zero and a variance of one so the model calculation remains stable. |
| `--glm` | Fits a logistic model at each variant to estimate how each extra copy of the tested DNA version changes the odds of disease, the ratio of cases to controls. |
| &nbsp;&nbsp;&rarr; `sex` | Adds recorded sex from the input sample file as an adjustment factor. |
| &nbsp;&nbsp;&rarr; `hide-covar` | Reports genetic tests without separate rows for the effects of age and sex. |
| &nbsp;&nbsp;&rarr; `firth-fallback` | Uses Firth correction, which reduces bias with small groups, when the ordinary model calculation fails. |
| `--out` | Starts output file names with s7-7_no_pcs, including s7-7_no_pcs.Disease.glm.logistic.hybrid. |

**Command 2: Command 2: test the cohort before sample and variant quality checks**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the cohort before sample and variant quality checks from s2-8_state.pgen, s2-8_state.pvar and s2-8_state.psam. If the local PGEN file is absent, R uses checkpoints/2.8/state in the course data folder. |
| `--maf` | Tests only variants whose less common DNA version has a frequency of at least 0.01, or 1%, in the input cohort. |
| `--covar` | Reads s7-7_all_ages.tsv, which holds ages for all measured wells, and matches them to samples by their identifiers. |
| `--covar-name` | Selects only Age from the adjustment table, leaving out genetic component scores that summarise ancestry. |
| `--covar-variance-standardize` | Rescales age to have a mean of zero and a variance of one so the model calculation remains stable. |
| `--glm` | Fits a logistic model at each variant to estimate how each extra copy of the tested DNA version changes the odds of disease, the ratio of cases to controls. |
| &nbsp;&nbsp;&rarr; `sex` | Adds recorded sex from the input sample file as an adjustment factor. |
| &nbsp;&nbsp;&rarr; `hide-covar` | Reports genetic tests without separate rows for the effects of age and sex. |
| &nbsp;&nbsp;&rarr; `firth-fallback` | Uses Firth correction, which reduces bias with small groups, when the ordinary model calculation fails. |
| `--out` | Starts output file names with s7-7_no_qc_no_pcs, including s7-7_no_qc_no_pcs.Disease.glm.logistic.hybrid. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 7.8 · Final summary and reporting

We save a final report and a table of the strongest variant in each of the three groups. We calculate intervals that describe uncertainty in the estimated effects and check the saved report, tables and main figures so others can review the analysis.


No PLINK options in this step.


## 6. Commits on notebooks/all-modules (local, not pushed)

- 306b78c Write the generated module check table of R/guided.R with LF
- faf7be2 Skip the encrypted round trip test without a password or 7-Zip
- 394e90d Generalise the student notebook generator to all modules
- 6b1a2a7 Add student notebook fields and comments for module 0
- 3303cec Add student notebook fields and comments for module 1
- 44859f2 Add student notebook fields and comments for module 2
- b3c7484 Add student notebook fields and comments for module 4
- 0deb0df Add student notebook fields and comments for module 5
- 91ee7be Add student notebook fields and comments for module 6
- 24c238b Add student notebook fields and comments for module 7 and the complete notebook


## 7. Where I stopped

All items of the task were done: 0a to 0c, the local branch, modules 0, 1, 2, 4, 5, 6 and 7, the generator for the eight module notebooks and the complete notebook, and this file. No usage limit was reached. The branch is not pushed and not merged. After your approval, the next roadmap steps are the project ZIP (item C) and the website buttons (item D, with its own mockup).
