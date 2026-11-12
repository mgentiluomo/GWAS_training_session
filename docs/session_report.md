# Contact address verification, 12 November 2026

Checked `CLAUDE.md`, `README.md`, `lessons/module_00_preparation.Rmd`,
`docs/troubleshooting.md`, `docs/release_checklist.md` and this report for
incomplete contact sentences. No missing address or unresolved email reference
was found. The contact address is `manuel.gentiluomo@unipi.it`.
It was already correct in the data access instructions in CLAUDE.md, module 0,
troubleshooting and the release checklist. No correction to those files was needed.

Regenerated all 60 step JSON files and 8 module JSON files. Their content was
unchanged. Text checks passed with 0 errors and 0 warnings. All 9 export tests
passed.

# Author policies and final verification, 12 November 2026

This section updates the earlier session records below. Work stayed on
`course/2026-guided-training`. Each new item was committed and pushed separately.

- Checked the existing Part 1 commits: `80a1a0c` (beta), `93897f8` (module openings)
  and `6154ea9` (guided README). Moved the remaining legacy setup instructions
  into `docs/legacy_demo.md` in `f969f37`. No demo files were deleted.
- Recorded the author's confirmed licences, annual password form policy and
  gradual website release in `CLAUDE.md`. Added MIT and CC BY-NC-SA 4.0 notices,
  a README citation and the module 0 licence note in `f0080df`.
- Added university email form instructions and kept the masked prompt text in
  `272d0d8`. The form URL remains a placeholder. This session did not create it.
- Added deployment variable `COURSE_DATA_PASSWORD`, annual rotation and a test
  email to the release checklist in `43bbeb6`. The website keeps its staged
  release and "beta 2026" label. Repository and data releases stay complete.
- Reran modules 6 and 7 on Windows with R 4.5.2 and the tested PLINK build in
  `C:/WEB_site/data_sources/codex_work/beta_verified_20261112/`.
  Copied the verified earlier prerequisites into this new folder. The notebook
  chunks ran again and wrote new module 6 and 7 outputs. Their log is
  `modules67_run.log`. All expected numbers stayed unchanged: 236,815 tests,
  8 hits, lambda 1.016465, 3 clumps, and comparison hit counts of 15 and 19.
  The exported summary file passed the eleven-column order and beta checks.
- Regenerated all 60 step JSON files, 8 module JSON files and
  `scripts/run_main_path.R`. Text checks reported 0 errors and 0 warnings.
  All 9 export tests passed. Course checks and synthetic summary-statistics
  tests passed. The initial direct course check failed because Windows inherited
  the unsupported `C.UTF-8` locale. Rerunning both R checks after the existing
  `normalise_course_locale()` helper passed. No system settings changed.

No data files or passwords were committed. The other website repository was
not accessed. No website deployment, form email test or classroom data release
was performed. The generated full-path script was regenerated, not executed
end to end in this session. macOS and Linux were not tested.

# Follow-up session, 12 November 2026 (beta column, beginner openings, README)

Branch `course/2026-guided-training`, one commit per item, all pushed.

## What changed

- **Summary statistics.** A new column `beta` (natural log of `odds_ratio`) sits
  before `standard_error`. The file now has **eleven columns**: chromosome,
  base_pair_location, variant_id, effect_allele, other_allele,
  effect_allele_frequency, odds_ratio, beta, standard_error, p_value, n. A missing
  odds ratio gives `NA`, never a number. The R helpers, the column dictionary, the
  validation (beta must equal the log of the odds ratio), the synthetic tests, the
  step 6.8 table and expected result, step 7.8 (intervals now use `beta`) and
  `docs/data.md` are updated. The file is about 22 MB (it was 17 MB).
- **Module openings.** The opening paragraph of modules 0 to 7 is rewritten in short
  sentences without semicolons. The content is the same.
- **README and setup.** The README shows the guided path (modules 0 to 7) alone. The
  older 600-sample demonstration moved to `docs/legacy_demo.md`, linked at the end.
  `docs/setup.md` points to module 0 and keeps the demo setup in a labelled section.
  No demo file was deleted.
- **Exports.** The 60 step JSON files, 8 module JSON files and
  `scripts/run_main_path.R` were regenerated. Most JSON changes are only new source
  hashes. Step 6.8 has the real content change.

## What ran (Windows 11, R 4.5.2, PLINK 2.0.0-b.1.4)

- Modules 6 and 7 ran in a new external folder,
  `C:/WEB_site/data_sources/codex_work/beta_rerun_20261112/`, starting from a copy of
  the step 5.7 state with the old module 6 and 7 outputs removed.
- `scripts/check_text.py`: 0 errors, 0 warnings.
  `scripts/tests/test_course_exports.py`: 9 tests passed.
  `scripts/check_course.R` and `scripts/tests/test_summary_stats.R`: passed.

## Results

- Every expected number is unchanged: 236,815 tests, 8 hits below 5e-8, lambda
  1.016465, 3 clumps, 15 hits without PCs (lambda 1.546351) and 19 hits without PCs
  and QC (lambda 1.654731).
- The new file has 236,815 rows and no missing `beta`. The first row has odds ratio
  1.03471 and `beta` 0.0341212.

## Not done

- `scripts/run_main_path.R` was regenerated but not run end to end. Modules 6 and 7
  ran through the notebooks.
- `test_main_path_recovery.R` and the classroom staging folder were not rerun. The
  staging folder was built before step 6.8 existed.
- macOS and Linux were not tested.
- I copied `plink2.exe` into `bin/` to run the notebooks. The folder is ignored by Git.

# Guided-training session, 12 November 2026 (final report)

This section reports the unattended session that followed the earlier main-path
authoring session (kept below, unchanged). It was done on branch
`course/2026-guided-training`, with one commit per item, all pushed.

## What was done

- **Step 0 (already finished by the previous tool; checked, not redone).** The
  exporter gives each PLINK option only its own clause, with `explained_at` when the
  explanation comes from an earlier step of the same module (44 options carry it).
  Step 3.2 has `interactive_data`: 20 rows, 90% to 99.5% in steps of 0.5, counts
  only. The restart points of step 3.8 and `CLAUDE.md` agree (2.8, 3.8, 4.6, 5.7).
- **Step 2, summary statistics.** New step 6.8 creates
  `results/guided/s6-8_gwas_summary_statistics.tsv` and a column dictionary. Columns:
  `chromosome, base_pair_location, variant_id, effect_allele, other_allele,
  effect_allele_frequency, odds_ratio, standard_error, p_value, n`. The step explains
  every column in plain words. Module 7 builds the QQ plot, lambda, Manhattan plot,
  thresholds, regional plot and final table from this file. The main path is now
  **60 steps** (it was 59).
- **Step 3, beginner pass.** All eight notebooks were rewritten in short sentences.
  Each module starts with "Module N at a glance" (what you will do, learn, how long)
  and ends with "Module N recap". Technical terms are explained at first use and
  linked to `docs/glossary.md` (now 126 anchored entries). `scripts/check_text.py`
  checks dashes, US spellings, the module frame and glossary links.
- **Step 4, release preparation (not published).** `scripts/package_release.py` reads
  the password only from `COURSE_RELEASE_PASSWORD`, refuses passwords shorter than 12
  characters, tests the finished archive with 7-Zip, and writes `SHA256SUMS.txt` with
  the archive and manifest hashes. `docs/release_checklist.md` lists the exact steps
  to create `data-2026.1` and update `config.R`. No release was created.
- **Step 1, student rehearsal.** Four passes from a clean clone with an empty package
  library. Fixes are listed in `docs/student_rehearsal.md`. The last pass needed no fix.
- **Step 5, exports.** The 60 step JSON files, 8 module JSON files
  (`site_content/modules/`) and `scripts/run_main_path.R` were regenerated.

## Verified on Windows (Windows 11, R 4.5.2, PLINK 2.0.0-b.1.4)

- Final rehearsal pass: modules 0 to 7 ran without error, each in a fresh R session
  from a fresh clone. All counts matched the notebooks' expected results and the
  instructor answer key: 1,844 samples and 296,360 variants after module 3; 238,513
  variants after module 4; 1,811 samples after module 5 (900 cases, 911 controls);
  236,815 tests, eight hits below 5e-8 and lambda 1.016465 in module 6; Bonferroni
  2.11e-7 and three clumps; 8, 15 and 19 hits with lambda about 1.016, 1.546 and 1.655
  in module 7. One content difference: at step 3.6 four relative pairs lose the other
  member than the key's list (the choice is by ID, the counts are identical).
- The regenerated `scripts/run_main_path.R` ran end to end in the clean student clone:
  20 file and figure comparisons printed `matches`, no error, same final summary.
- The summary statistics file has 236,815 rows and ten columns, about 17 MB. The
  Manhattan and QQ plots were opened and inspected: eight points above the line on
  chromosomes 3, 9 and 12; the QQ plot is labelled lambda GC = 1.016.
- `test_course_exports.py` (9 tests) and `test_package_release.py` (5 tests) pass.
  The packager built a 105-file, 327,539,339-byte AES-256 archive from the real
  staging folder in 19 seconds with a throwaway password. That archive was used only
  for the rehearsal and is not a release.
- `scripts/check_course.R`, `test_summary_stats.R`, `test_checkpoints.R`,
  `test_checkpoint_replay.R` and `test_session_locale.R` passed (author-side runs by
  the helper that built step 6.8).

## Not verified

- RStudio itself and the masked password prompt were not used in the rehearsal (it used
  `Rscript` and `rmarkdown::render`). The author reports having checked the masked
  `getPass` prompt, the first-time package installation and the Knit button in RStudio
  on Windows with R 4.5.2 on 12 November 2026; I did not observe this. Installation of
  R and RStudio and a real download from a URL remain unverified.
- macOS and Linux for the new notebooks and for step 6.8.
- Button and menu names on the CRAN, RStudio, PLINK and GitHub pages in module 0 were
  written from memory and must be checked against the live pages.
- `test_main_path_recovery.R` was not run for 6.8, because the staging folder
  `classroom-stage-2026.1` was made before step 6.8 existed. `test_unicode_plink.R`
  and `test_course_setup.R` were not rerun after this session's edits. The old 55-file
  test ZIP could not be used: its password is not recorded anywhere I could read, and
  I did not try to guess it. A new throwaway archive of the 105-file staging folder
  was built and used instead. The checksums in `config.R` still describe the old archive.
- The module time estimates are estimates. The rehearsal measured compute time only
  (every module under 30 seconds), not reading time.
- Small facts added to glossary entries and notebook text by the writing helpers were
  not checked against sources, for example "GRCh38 dates from 2013", "the GC score runs
  from 0 to 1", "first-degree relatives have kinship about 0.25", "96 wells per plate"
  and "MT comes from the mother only". Please read the glossary once.

## Decisions for the author

1. **Step 6.8 and the count of 60.** I added a separate step rather than hiding the
   file in 6.7. The column names follow the GWAS Catalog style. `standard_error` is the
   standard error of the log odds ratio, and the step says so. Say if you want `beta`.
2. **Restart logic.** Steps 7.6 and 7.8 now have parent 6.8 so that a restart restores
   the summary file. `s7-8_leads.tsv` keeps its name but uses the standard column names.
3. **Re-stage before release.** The classroom package must be staged again from a run
   of the final notebooks so that it holds the 6.8 checkpoint (see
   `docs/release_checklist.md`, section 2).
4. **Working copies.** `C:\GWAS_course` already existed as a clean clone, so it stayed
   the authoring copy. The rehearsal used new clones `C:\GWAS_course_rehearsal` and
   `C:\GWAS_course_rehearsal2`, empty libraries `C:\GWAS_rehearsal_lib` and `...lib2`,
   and outputs in `C:\GWAS_rehearsal_out`. They can be deleted. The packaging tests left
   temporary `package-tests-*` folders, and the rehearsal archive is in
   `codex_work\release-rehearsal-20261112`. All of these are outside the repository.
5. **Legacy text.** `README.md`, `docs/setup.md` and `config.R` (`mode = "demo"`) still
   describe the earlier 600-sample demonstration beside the guided path. A beginner may
   be confused. Trimming it is a separate decision.
6. **Step order in module 0.** Steps 0.4 and 0.5 need the project from 0.6. The text now
   says so, and the numbers were kept. Reordering would renumber the course.
7. **Glossary quality.** The 23 original entries are terse and expert-style (for example
   Lambda GC and HWE). Rewriting them for beginners is not done.
8. **Still open from before:** classroom password and release, licences, Linux and
   macOS runs, and the website mockup (see
   `docs/open_issues.md`).

---

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

## Completed main path

All eight main-path notebooks are implemented and executed on Windows. The
generated complete script and the 59-step website export are also implemented.
Modules were committed and pushed separately; subsequent recovery and export
changes were kept in separate commits. All analytical outputs remain external.

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

- Module 3: Windows execution matched all reference sample counts, ending at
  1,844 samples and 296,360 variants. Pruning retained 69,539 sites; 13 low-F
  samples, 30 duplicate/related records and 76 remaining P14 wells were removed.
  Eight high-F samples were flagged and retained. One failed first attempt
  exposed scientific notation in interval coordinates; explicit integer formatting
  fixed it, and the full module passed on the next attempt.

- Module 4: Windows execution matched the reference counts, ending at
  1,844 samples and 238,513 variants. HWE removed 167 sites, including the
  three named ancestry markers; chromosome review removed 33 sites and
  duplicate review another 306 entries. The sample-size-aware HWE policy is
  calibrated at 1,000 controls with a 10^(-6) mid-p cutoff and tightens for
  larger samples; at this dataset size it reproduces the reference rule.
  This teaching policy must not be presented as a universal research threshold.

- Module 5: Windows reference PCA/projection passed with 48,614 shared sites.
  After removing 33 projected outliers, the retained cohort has 1,811 samples
  and 238,513 variants. Ten within-cohort PCs and a scree plot were generated.
  A first attempt found a long PVAR metadata header; streaming over all header
  lines fixed the reader. The PCA figure was visually inspected and its legend
  was corrected to use the four groups actually present in the supplied subset.

- Module 6: Windows main scan produced 236,815 finite tests and eight genome-wide
  hits, with autosomal lambda 1.016465. The model includes age, sex and ten PCs.
  All main-scan FIRTH flags were N; a separate low-frequency retained autosomal
  site was deliberately analysed with forced Firth for teaching. A manifest
  protects the 6.7 analysis checkpoint.

- Module 7: Windows execution produced Manhattan, QQ, common-scale QQ comparison
  and L2 regional plots, three LD clumps, effect-allele lead tables and a final
  Markdown summary. Final cohort: 900 cases and 911 controls. The no-PC and
  no-sample/variant-QC contrasts reproduced 15 and 19 significant variants and
  lambda approximately 1.546 and 1.655. All main plots were visually inspected;
  the regional legend was changed to ASCII ranges for Windows font portability,
  and the comparison plots now share a vertical scale.

- Full main-path rerun: all eight notebooks executed in order in a fresh external
  folder and passed instructor key/reference comparisons, including sample
  removal identities (except the intentionally interchangeable relative-pair
  choice), leading association p-values and main-scan test counts.
- Recovery: seven restart targets (2.6, 3.2, 3.5, 4.5, 5.6, 6.4, 7.7) passed
  metadata identity, expected counts and zero PLINK genotype differences with
  missing calls included. Early source conversion and required diagnostic files
  are now replayed too; full genotype copies remain at the four boundaries only.
- Local release staging: 105 files, 634,410,035 bytes, under codex_work/classroom-stage-2026.1,
  with a separate SHA-256 manifest. It includes the official chain and excludes
  imputation material and instructor keys. The old 55-file test ZIP is unchanged.

## Script and website exports

`scripts/run_main_path.R` is generated directly from executable notebook chunks;
manual install/download chunks are omitted. It was executed against the staged
package in `codex_work/combined_script_20261112/`, reproducing the summary,
eight significant variants, all required figures and comparison hit counts.

`scripts/build_tutorial.py` now exports one JSON per step under
`site_content/steps/`, without reading genotype data or building the old demo
website. The 59 exports preserve fixed blocks, R commands, PLINK commands and
per-option explanations. Shared explanations come from the same notebook set.
Figure placeholders include Gemini prompts and are explicitly unreviewed.
The schema is documented in `docs/site_content_schema.md`; generated files must
not become a second manually maintained source. Step 0.5 is labelled
`manual_required`; automated URL tests used mocked local files only.

## Verification record and external outputs

- The generator's 36 tests and the five packaging checks passed.
- The 20 download/setup regression checks (including the original local AES-256 ZIP),
  session-locale checks, synthetic checkpoint
  tests, seven real restart integrations and six export consistency tests passed.
- `scripts/check_course.R` passed on Windows. All 59 steps satisfy the fixed
  block order; executable chunks were evaluated from each notebook.
- The student-artifact check covered all eight notebook sources against the
  external instructor key and found no educator-only text. Expected results and
  quick-check answers remain intentionally collapsed as required by the course.
- RStudio's bundled Pandoc was found and used without installation. All eight
  notebooks rendered to HTML externally. Initial image-path warnings were fixed
  with absolute render-only image paths; plots appear within the expected-result
  details blocks. The final analytical PNGs were visually inspected. HTML structure checks confirmed
  six embedded result images with alt text and collapsed details by default;
  browser layout sampling covered the original preparation and module 7 pages.
  Captures of an all-expanded temporary review copy were blank, so expanded
  details were checked structurally rather than claimed as fully browser-tested.
- Final text QA found lossy question-mark substitutions in mathematical prose
  introduced by a Windows shell pipe. Formulae now use clear ASCII notation
  (`5e-8`, `r^2`, `1-p`, `+/-`), and a regression rejects those corrupt patterns.
  The calculations were unchanged; JSON and the combined script were regenerated.

External locations, all under `C:/WEB_site/data_sources/codex_work/`:

| Path | Contents |
| --- | --- |
| `main_path_final_20261112/` | Fresh complete notebook run and verified checkpoint tree. |
| `combined_script_20261112/` | Independent generated-script run. |
| `classroom-stage-2026.1/` | Main-path inputs, official chain and release-ready checkpoint staging. |
| `classroom-stage-2026.1.MANIFEST.tsv` | Staging inventory, byte counts and SHA-256. |
| `rendered_notebooks_20261112/` | Rendered notebook HTML; generated course data are not committed. |
| `rendered_notebook_run_20261112/` | Analytical outputs produced during notebook rendering. |

The original simulated inputs, instructor key and local test ZIP were not
overwritten. The manufacturer array manifest remains local; SHA-256 payload
manifests are separate integrity inventories, not manufacturer design manifests.

## Unverified items and decisions for the author

No main-path executable step remains failed after the permitted repair attempts.
Linux/macOS execution of the new main path, clean-machine installer actions,
the masked RStudio prompt and broad accessibility/device coverage remain to test.
The earlier Ubuntu AES-256 extraction result is recorded as author-reported,
not as a test of the new complete main path.

Before classroom distribution, approve the staged dataset and teaching policies,
confirm licences, choose the classroom password outside the repository, create
the encrypted release, and replace the local test URLs/checksums in `config.R`.
The current HWE calibration is study-specific and should receive author review;
it preserves the reference cutoff at this course size. No new GitHub data release
or website was created. Website design still starts with an approved mockup.
See `docs/open_issues.md` for precise limits. Modules A/B and post-GWAS work
were not started.
