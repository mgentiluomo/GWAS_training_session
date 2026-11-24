# Module A build, 24 November 2026

Goal: module A (imputation) ready to publish, in preview only. Code, notebook, export and website.
Rules: one branch per repository, no merge, no release, no encryption, no push to `main`.

Course branch: `course/module-a-data`. Website branch: `course/module-a` (from an up-to-date `main`).

## Before phase 1: a conflict with the identity proof of phase 2

`course/module-a-data` descends from `course/2026.5`. Its lessons have 63 main-path steps: step 6.2 was removed
in 2026.5. The website holds the 2026.4 export: 64 steps, from commit `1e05565` of
`course/2026-guided-training` (`src/content/gwas/index.json`). A normal export from this branch therefore
writes the 2026.5 JSON for modules 0 to 7, which differ from the website JSON (checked: `step-3-2.json` and
`module-3.json` already differ in the committed `site_content/`). The required proof (JSON of modules 0 to 7
byte-identical to the 2026.4 JSON of the website) fails by construction, whatever module A does.

The rule for this case is: stop and document. Phase 1 does not depend on the export, so it goes ahead. Phase 2
prepares the lesson and the exporter, runs the proof, and stops there if the proof fails.

## Phase 1. Course code

### R helpers (`R/imputation.R`) and tests (`scripts/tests/test_imputation.R`)

New file `R/imputation.R`, sourced after `R/guided.R`. All PLINK calls go through `run_plink`.

- `prepare_imputation_input(cfg)`: one VCF per region from the state at 5.7. PLINK writes VCF 4.2 with bgzip,
  the `chr` prefix and IID as the sample name. The REF list (one file per region) holds the GRCh38 `Ref_Plus`
  of the array annotation. R checks that every REF equals that allele, removes the PR flag and its header
  line, and writes the file again as BGZF with plain line ends. Base R has no BGZF writer:
  `imputation_write_bgzf` compresses each block with R's gzip writer and replaces the gzip header with the
  BGZF header. `bgzip -t`, `tabix -p vcf` and `bcftools view` (htslib 1.25, WSL) accept the files.
- `read_imputation_info(path)`: R2, ER2, AF, MAF, TYPED and IMPUTED from the dosage VCF, as a data.frame.
- `compare_with_truth(dose, truth, panel)` and `imputation_quality_table()`: R2 against true r2 by frequency
  class, array sites left out (INFO flag `ARRAY`, also when bcftools has added AC and AN).
- `imputation_association(cfg, dose)` (the command of A.9 through `run_plink`) and `imputation_l4()`.

Checks on the real data (Windows 11, R 4.5.2, PLINK 2.0 b.1.4):

- **The data release matters.** The imputed output in `stage-module-a-2026.1` was made from the cohort of
  `data-2026.1` (course 2026.4). The cohort of `data-2026.2` (course 2026.5) has 4 different samples
  (relatives rule at 3.6): SIM26_0017, 0423, 0678, 1088 against 1264, 1291, 1329, 1636. So the checks
  below use `release-data-2026.1/payload` (checkpoint 5.7 as `s5-7_state`, `s6-3_covariates.tsv` as
  `s6-2_covariates.tsv`) in the new work folder `codex_work/module-a-build-20261124`. **Open:** module A
  with the 2026.5 course needs its imputed output made again from the 2026.2 cohort.
- `prepare_imputation_input`: 161 sites on chr18 and 277 on chr22, 1,811 samples; PLINK wrote 168 and 284
  CRLF lines and 161 and 277 PR flags, all removed. Against the target of the night
  (`module_a_work/target/full`): samples, sites, REF and ALT, INFO and every genotype identical. Only the
  `##fileDate` line differs (23 and 24 November).
- `read_imputation_info` (chr22, 60,224 variants, 10 seconds): 277 typed sites, median ER2 0.586.
- `compare_with_truth` (chr22, about 75 seconds): the table of draft section A.8, row by row (19,832
  variants; for example at least 5%: 7,826, median R2 0.79, median true r2 0.70; all: 0.62 and 0.35). Against
  `per_variant_chr22.tsv` of the night: same 19,832 variants, same R2, true r2 within 5e-7.
- `imputation_association` (chr18): 8,334 variants tested. L4 `chr18:38042715:G:A`: MACH r2 0.946, OR 1.47,
  p 1.65e-6. Best of the region `chr18:38106879:G:C`: OR 1.54, p 4.19e-8. Same as the night.

`scripts/tests/test_imputation.R` (synthetic data, PLINK in `bin/`): BGZF blocks and EOF, REF check and swap,
PR and CRLF removal, the error for a REF that matches neither allele, INFO reading, true r2 and classes, the
`ARRAY` flag with AC and AN, a missing sample, association with the R2 filter, and the L4 table. Passed.

### Lesson and notebook

- New lesson `lessons/module_A_imputation.Rmd`, the single source of the notebook and of the website content.
  It holds the overview ("Module A at a glance"), steps A.1 to A.10 with the fixed blocks of every course
  step, and the recap. A.1 to A.6 and A.10 are reading steps. A.7 (input files), A.8 (quality and truth) and
  A.9 (association) run R code; each has a success line, a student summary and the table of PLINK options.
  Eagle2 and Minimac4 are in the optional box ("Another approach") of A.7, with the tested commands; the
  masking exercise is the optional box of A.8. The discussion questions of A.6 are its quick check.
- Prerequisites (`module_meta`): the checkpoint at 6.2 (state 5.7 and the covariates of 6.2), the array
  annotation and the module A data in `data/course/module_a/`. `R/guided.R` gets the `A` entry of the
  generated table; `guided_check_module` gives the right restart advice for a letter module.
- Three glossary entries: haplotype, reference panel, imputation quality (R2 and INFO).
- Figure A.8: `plot_imputation_quality()` in `R/imputation.R` draws it from `compare_with_truth()`. The same
  PNG is the module asset `Figures/module_a/figure_A8_r2_chr22.png`, declared in the lesson with alt text and
  caption (`result_figure` comment).
- Notebook `notebooks/module_A_imputation.qmd`, generated from the lesson. It is not part of the complete
  notebook of modules 0 to 7.
- Render with Quarto (RStudio's quarto.exe, R 4.5.2, Windows 11) on `data-2026.1` (checkpoint 5.7 and
  covariates) and the module A data: exit 0, about 1.5 minutes. Outputs: 161 and 277 sites with 1,811
  samples; the A.8 table identical to the draft; L4 OR 1.47, p 1.65e-6, best variant p 4.19e-8.

### Pipeline changes (needed by phase 2, checked here)

- `scripts/course_exports.py`: lessons named `module_<letter>_*.Rmd` are additional modules, exported beside
  the main path (`step-a-1.json` to `step-a-10.json`, `module-a.json`). The main path keeps its 63-step check
  and its combined script. New optional figure kind `result` (a PNG made by the course code under
  `Figures/`). `--export` accepts `vcf-4.2` and `bgz`, and `--extract` accepts `bed1`, as modifiers.
- `scripts/student_notebooks.py`: one notebook per additional module, with no previous or next module.
- `scripts/check_text.py` checks the letter lessons too (0 errors).
- **Main path unchanged.** The export of this branch was saved before the changes. After the changes
  (with module A), the 63 step files, the 8 module files, the formats, `run_main_path.R` and the 9 notebooks
  are byte-identical to it.

### Tests (Windows 11, R 4.5.2, Python 3.12, PLINK 2.0 b.1.4)

- Python, `python -B -m unittest discover -s scripts/tests`: 103 tests, OK, 2 skipped (the encrypted round
  trip without a password, as before). Three tests assumed modules 0 to 7 only (63 JSON files, 9 notebooks,
  the generated module table); they now count the additional modules separately.
- R, every file in `scripts/tests/` and `scripts/check_course.R` with `COURSE_DATA_DIR` set to
  `classroom-stage-2026.2`: 17 of 18 exit 0, including `test_guided_modules.R` (151 s) and the new
  `test_imputation.R`. `test_main_path_recovery.R` stops at its first line: it needs `COURSE_STAGE_DIR` and
  `COURSE_CANONICAL_RUN` (an author integration run), which were not set. It does not use module A code.
- `python -I scripts/author/tests/test_sim2026.py`: 40 of 40.
- `python -B scripts/check_text.py`: 0 errors (2 old warnings in `docs/site_content_schema.md`).
- `--export-notebooks notebooks --check-notebooks`: up to date, 10 files.

## Phase 2. Course export

- Lesson structure: one step per section, A.1 to A.10, with the blocks of `docs/site_content_schema.md`
  (what we do, why, you need, command, expected result, troubleshooting, quick check, files created). The
  discussion questions of A.6 are its quick check (seven questions, each with its answer).
- Normal pipeline: `python -B scripts/build_tutorial.py --export-steps site_content/steps --export-main-script
  scripts/run_main_path.R`. It writes the 63 main-path steps and 8 module pages as before, plus
  `step-a-1.json` to `step-a-10.json` and `module-a.json`. Verification field: A.7, A.8 and A.9
  `windows_executed`; the reading steps `manual_required`, as for the reading steps of module 1.
- Figure A.8 is in the export of step A.8 as a figure of kind `result`, asset
  `Figures/module_a/figure_A8_r2_chr22.png`, with alt text and caption.

### Required proof: JSON of modules 0 to 7 against the 2026.4 JSON of the website. FAILED: stopped here.

Compared: every file of `src/content/gwas/steps/` and `src/content/gwas/modules/` on `origin/main` of the
website (export of commit `1e05565`, 64 steps) with `site_content/` of this branch.

| Result | Files |
| --- | ---: |
| byte-identical | 9 |
| different | 62 |
| only on the website (`step-6-8.json`) | 1 |

Cause: this branch descends from `course/2026.5`, whose lessons differ from 2026.4 (step 6.2 removed, steps
renumbered, new text and boxes). It is not module A: on this branch, the export of modules 0 to 7 is
byte-identical before and after module A (phase 1, "Main path unchanged").

As the rule says, the work stops here. **Phase 3 (website) was not started**: no website branch, no sync, no
preview. The JSON of module A are committed on this branch only.

**To decide.** Two ways forward:

1. Publish module A together with the 2026.5 course (and `data-2026.2`). The website then takes the 2026.5
   JSON of modules 0 to 7 in the same change. The imputed output of module A must first be made again from
   the 2026.2 cohort (4 different samples), or the A.9 numbers will not match the students' cohort.
2. Publish module A on the 2026.4 course now. Module A (lesson, helpers, pipeline changes) must then be
   carried over to a branch from `course/2026-guided-training`; there the proof can pass. The numbers of the
   lesson already match the 2026.4 cohort (`data-2026.1`). On 2026.4 the covariates are `s6-3_covariates.tsv`
   (step 6.3), so the module prerequisites and the A.9 defaults change from 6.2 to 6.3.

## Port to 2026.4 (way forward 2, chosen by the author)

Branch `course/module-a-2026.4`, from `course/2026-guided-training` (release 2026.4, commit `1e05565`). Nothing
of 2026.5 is carried over.

- Cherry-picked from `course/module-a-data`: the HRC rule (`d8177d9`), the R helpers and tests (`e42da52`), the
  lesson, notebook, figure and pipeline (`a5eb2b8`), the module A JSON (`2d25e50`).
- Conflicts solved by hand. `AGENTS.md` keeps the 2026.4 line on the 6.8 rule and adds the HRC rule.
  `R/guided.R` keeps the 2026.4 table of module 7 and adds module A. The exporter keeps the 2026.4 option
  modifiers (`--exclude bed1`) and adds `--export vcf-4.2 bgz` and `--extract bed1`. The 64-step check stays.
- 2026.4 had no "Another approach (optional)" block. It is added to the exporter and to the notebook generator
  (optional, collapsed, after "Files created"). No main-path lesson uses it, so the main path does not change.
- The `R/guided.R` of commit `98fed00` lacked one closing parenthesis after the conflict. The next commit
  fixes it. Every test below ran on the fixed file.
- `scripts/package_project.py`: additional modules (`lessons/module_<letter>_*.Rmd` and their notebooks) are
  left out of the main project package. They ship with the module A data release. The main project package
  stays as in 2026.4, apart from the new `R/imputation.R` and the module A entry of `R/guided.R`.

### Changes for 2026.4

- Covariates: `s6-3_covariates.tsv` (step 6.3). The module prerequisites become checkpoint 6.3, restart 6.4.
  The A.9 default of `imputation_association()` reads `guided_path(cfg, "6.3", "covariates.tsv")`.
- Text: "your files at step 6.3", "the covariates from step 6.3", "the main analysis (step 6.4)". The A.9
  command and its option table read `s6-3_covariates.tsv`.
- Cohort: `data-2026.1`. The numbers of the lesson are unchanged.

### Checks (Windows 11, R 4.5.2, Python 3.12, PLINK 2.0 b.1.4)

- Python, `python -B -m unittest discover -s scripts/tests`: 88 tests, OK, 2 skipped. Before the package fix,
  6 tests of `test_project_package.py` failed on the new lesson ("Unexpected student lesson source"). The
  same failure exists on `course/module-a-data`: there the earlier run of 103 tests came before the lesson
  was committed, so `git ls-files` did not list it yet.
- R, every file in `scripts/tests/` and `scripts/check_course.R` with `COURSE_DATA_DIR` set to
  `classroom-stage-2026.1-final`: 15 of 16 exit 0. `test_main_path_recovery.R` needs `COURSE_STAGE_DIR` and
  `COURSE_CANONICAL_RUN`, as before.
- `python -I scripts/author/tests/test_sim2026.py`: exit 0.
- `python -B scripts/check_text.py`: 0 errors, 0 warnings. `--check-notebooks`: up to date, 10 files.
- Render of `notebooks/module_A_imputation.qmd` with Quarto on the `data-2026.1` checkpoint 5.7 and
  `s6-3_covariates.tsv`: exit 0. The A.7 VCF files, the A.8 table and figure and the A.9 association file are
  byte-identical to the earlier render. L4: R2 0.95, OR 1.47, p 1.65e-6.

### Required proof: JSON of modules 0 to 7 against the website in production. PASSED.

Compared every file of `src/content/gwas/steps/` and `src/content/gwas/modules/` on `origin/main` of the
website (commit `4b54b05`) with `site_content/` of this branch: 72 of 72 byte-identical (64 steps, 8 modules).
Module A adds `step-a-1.json` to `step-a-10.json` and `module-a.json`.

## What changes in module A when 2026.5 is released

- Covariates move back to step 6.2 (`s6-2_covariates.tsv`). Prerequisites: checkpoint 6.2, restart 6.3. The
  A.9 default reads `guided_path(cfg, "6.2", "covariates.tsv")`. The text says "step 6.2" for the covariates
  and "step 6.3" for the main analysis. These are the values of `course/module-a-data`.
- The 2026.5 cohort (`data-2026.2`) differs by 4 samples each way: in 2026.2 only SIM26_0017, SIM26_0423,
  SIM26_0678, SIM26_1088; in 2026.1 only SIM26_1264, SIM26_1291, SIM26_1329, SIM26_1636. The target VCF, the
  imputed output and the truth files of the module A data must be made again from `data-2026.2`. Then every
  number of A.7 to A.9 is checked again: sample count, the A.8 table and figure, the L4 result, the best
  variant of the region and the variant count of A.9.
- The 2026.5 exporter already has the "Another approach" block; keep one copy when the branches meet.
- The packaging fix for additional modules (`scripts/package_project.py`) is needed on 2026.5 too.
- The module A data package is made again for 2026.5, with its own version, and the website link changes.

## Phase 3. Website

Website branch `course/module-a`, from `origin/main` (`4b54b05`), commit `09e3632`, pushed. No merge.

- `scripts/sync-gwas-content.mjs` copies the additional modules (`step-a-1.json` to `step-a-10.json`,
  `module-a.json`), their notebook and the result figures (`public/gwas/figures/`). They are listed apart in
  `index.json`. The main-path checks and counts do not change. The JSON of modules 0 to 7 have no content change.
- `release.ts`: `PUBLISHED_ADDITIONAL_MODULES` is empty, so module A is built in review builds only (local
  development, Vercel preview, `GWAS_REVIEW_BUILD=1`). The production build generates no module A page and the
  course map shows module A as "Not yet available", as before.
- Data link placeholder: `ADDITIONAL_MODULE_DATA.A.url` in `release.ts` is `null`. The module page then says
  "not published yet". To publish: set the https URL of the module-a package there, then add "A" to
  `PUBLISHED_ADDITIONAL_MODULES`.
- Step page: new "Another approach (optional)" box; result figures (kind `result`) shown with alt text and
  caption inside the expected result. Module page: "Where the module ends" says to go back to step 6.4.
- The notebook and the PNG are static files: in production they are not linked, but they can be reached by
  their URL.
- `index.json` names the source branch `course/module-a-2026.4`, used for links to course documents. After the
  course branch is merged, run the sync again from the merged branch.

### Checks

- `tsc --noEmit`: 0 errors. ESLint: 0 errors (11 old warnings in other files).
- `next build` (production): exit 0, no module A page. `GWAS_REVIEW_BUILD=1 next build`: exit 0, module A and
  its 10 steps generated.
- axe-core 4.14.1 (WCAG 2.0, 2.1, 2.2 AA and best practice), light and dark, 390 and 1280 px, every `details`
  open: course home, module A, steps A.1 to A.10, step 6.4. 52 runs, 0 violations, no horizontal overflow, no
  broken image. The first run found an empty table header in A.4; the lesson now heads it "Feature" (`49d5014`).
- Screenshots of A.6 and A.8 at 390 and 1280 px (light theme, full page):
  `C:\WEB_site\data_sources\codex_work\module-a-build-20261124\screenshots\`.
- Vercel preview: built (status success). It is behind Vercel login, so the checks above ran on the local
  review build of the same commit.

## Before publication

### Student code against the 2026.4 project ZIP

Built with `scripts/package_project.py --version 2026.4` from tag `project-2026.4` and from this branch
(outside Git, no PLINK). 71 files against 72. Three files differ, every other file is byte-identical:

- `R/imputation.R`: new (381 lines).
- `R/guided.R`: the `A` entry of `guided_module_inputs`, and the restart advice of `guided_check_module()`
  limited to numbered modules (`grepl("^[0-9]+$", module)`). For modules 0 to 7 the test is always true, so
  the advice is as before.
- `docs/glossary.md`: three new entries (haplotype, reference panel, imputation quality).

The module A lesson and notebook are not in the ZIP. The website offers the notebook.

`R/guided.R` does not change any output of modules 0 to 7:

- `scripts/run_main_path.R` ran twice on `classroom-stage-2026.1-final`, from the tag and from this branch, into
  two new folders: exit 0 both. 379 files each. 249 byte-identical. The other 130 are PLINK logs and command
  texts: equal once the folder name, the times and PLINK's random seed line are removed, and line wraps are
  ignored (a longer folder name moves the wrap). No other difference.
- `test_guided_module_check.R` (exact student messages of modules 0 to 7): exit 0 on both.
- `test_main_path_recovery.R`, with `COURSE_STAGE_DIR` the same data and `COURSE_CANONICAL_RUN` the run of the
  tag: exit 0, seven restarts.

Two ways to give students the code (not chosen yet):

1. Inside the module A package: `R/imputation.R` and `R/guided.R`, with a README that says to copy them into
   the project folder `R/`. The notebook stays a website download. `R/guided.R` replaces the student's
   file; it is the 2026.4 file plus module A only. A variant avoids replacing it: the module A notebook checks
   its inputs with a function of `R/imputation.R`, so only a new file is copied.
2. Project release `project-2026.4.1`: the same ZIP with the three files above. `package_project.py` requires
   the step 0.3 URL of the new version in the module 0 lesson, so step 0.3 changes, and its website JSON
   with it. Students already in the course must copy the new files or download the project again.

### Website: module A out of the production build

Website commit `cb1ec03` on `course/module-a`:

- The sync keeps module A apart: `src/content/gwas/additional.json` and source copies in
  `src/content/gwas/additional-public/`. Nothing of module A is in `public/` or `content.generated.ts`.
- `scripts/stage-gwas-modules.mjs` runs before `next dev` and `next build`. It imports and copies only the
  visible modules (review builds, or a letter in `PUBLISHED_ADDITIONAL_MODULES`).
- `scripts/check-gwas-production.mjs` runs after `next build`. In a production build it fails if a hidden
  module has a file, a page or a title in `public/` or `.next/`. Phrases also used elsewhere in the site
  (for example "Imputation servers" in the lecture slides) are not used as markers.

Checks: `tsc` 0 errors, ESLint 0 errors. Production build: exit 0, check OK (2,650 files, no module A).
Served: module A pages, notebook and figure 404, no link to module A. Review build: module A included;
the forced production check on it fails, as it must (217 problems). axe on the review build: 52 runs,
0 violations, no overflow, no broken image.

### Publication sequence

Written in `docs/release_packaging.md` ("Publish module A"). It notes one gap: `package_release.py` refuses
`stage-module-a-2026.1` as a source today.

## Author decisions: helpers in the module A data, packaging rule

### Student code (way 1, without copying files into the project)

- `R/imputation.R` ships in the module A data, as `data/course/module_a/R/imputation.R`.
- The first chunk of the module A notebook (generated, `ADDITIONAL_HELPERS` in `scripts/student_notebooks.py`)
  sources `R/imputation.R` of the project if it is there, otherwise the copy in the module A data
  (`COURSE_MODULE_A_DIR`, or `module_a` in the course data folder). If both are missing it stops with one
  sentence: "R/imputation.R was not found in the project or in the module A data. Extract the module A data
  into ... and run this chunk again." Then it runs `imputation_check_module()`.
- `imputation_check_module()` (in `R/imputation.R`, base R only) checks the annotation, the module A data and
  the files of step 6.3, with the messages of `guided_check_module()`. Its list repeats `module_meta` of the
  lesson; a Python test checks that they agree.
- `R/guided.R` is the 2026.4 file again: byte-identical content to `project-2026.4` (line ends aside). The
  generated module table lists modules 0 to 7 only. `scripts/run_main_path.R` is unchanged.
- The three glossary entries stay: the website reads them.
- Lesson: "What you need" says that the data hold `R/imputation.R` and that nothing is copied into the
  project. Step A.1 "You need" lists how to get the data ready (download, password, extract into
  `data/course/module_a`, open the notebook, run its first chunk). A.1 reading time: 3 minutes (469 words).
- Export and notebooks regenerated. JSON of modules 0 to 7: 72 of 72 byte-identical to `origin/main` of the
  website. Module A JSON change (A.1 text, setup code, overview).
- Course commits: `f8c7acc` (packaging), `6cb7181` (module A).

**For 2026.5.** The 2026.5 project will hold both `R/guided.R` with the module A entry and `R/imputation.R`.
The notebook then finds `R/imputation.R` in the project first. Keep the copy in the module A data until no
student uses a 2026.4 project.

### Packaging rule

Ported from `course/module-a-data` (`f19b815`) in its own commit (`f8c7acc`), adapted to 2026.4:
`--package module-a`, its own top folders (`reference_panel`, `genetic_map`, `imputed`, `true_genotypes`),
`README_simulated.txt`, `panel_samples.tsv`, and one named file, `R/imputation.R`. No other R file is
accepted. The source must be a `stage-module-a-*` folder under `codex_work`. `FORBIDDEN` and the
`classroom-stage-*` rule of the main package are unchanged; a test checks that the main package still
refuses `R/imputation.R`. New `--dry-run`: MANIFEST.tsv and members.txt only, no ZIP, no password.

Dry run on `stage-module-a-2026.1`, after copying `R/imputation.R` of `6cb7181` into its `R/` folder (nothing
else in the stage was changed): 22 files, 229,691,213 bytes, MANIFEST.tsv SHA-256
`46d63ba77ddbc7fd8e079064d12781e79c2f95809900669b1c42fd3aece74ac4`
(`codex_work/dryrun-module-a-2026.1/`). 21 rows equal the stage sidecar
`stage-module-a-2026.1.MANIFEST.tsv`; the new row is `R/imputation.R`. The four Eagle and Minimac4 logs of
`imputed/` are left out, as for every package. The sidecar itself was not changed: it does not list
`R/imputation.R`.

### Render from a clean 2026.4 project

The published `GWAS_course-2026.4.zip` (release `project-2026.4`, SHA-256 checked) extracted into a new
folder. PLINK copied from `third_party/` into `bin/`, as at step 0.6. The 22 files of the dry run copied into
`data/course/module_a` (the extracted package), the array annotation into `data/course/array`, and the files
of step 6.3 (from the main-path run of the tag) into `results/guided`. No `COURSE_*` variable set. The
project has no `R/imputation.R` and its `R/guided.R` has no module A entry.

Quarto render of the module A notebook of `6cb7181`: exit 0, 82 s. First chunk: "Module A input files are
present." The 8 data outputs of A.7 to A.9 are byte-identical to the earlier render; the other 9 files are
PLINK logs and command and console texts (paths and times). L4: R2 0.95, OR 1.47, p 1.65e-6; best variant
`chr18:38106879:G:C`, p 4.19e-8.

### Checks after the author decisions

- R: `scripts/check_course.R` and every file in `scripts/tests/`, with `COURSE_DATA_DIR` set to
  `classroom-stage-2026.1-final`: 15 of 15 exit 0, including `test_imputation.R` (new loader and input-check
  tests) and `test_main_path_recovery.R` (`COURSE_STAGE_DIR` the same data, `COURSE_CANONICAL_RUN` the run
  of the tag).
- Python, `python -B -m unittest discover -s scripts/tests`: 93 tests, OK, 2 skipped (the encrypted round trip
  without a password).
- `python -I scripts/author/tests/test_sim2026.py`: exit 0.
- `python -B scripts/check_text.py`: 0 errors, 0 warnings. `--check-notebooks`: up to date, 10 files.

## Before encryption

- `stage-module-a-2026.1.MANIFEST.tsv` regenerated from the stage with the rules of the package: 22 rows, no
  logs, byte-identical to `dryrun-module-a-2026.1/MANIFEST.tsv` (SHA-256 `46d63ba7...74ac4`). The old file
  (25 rows: 21 files and 4 logs, no `R/imputation.R`) is kept as
  `module-a-build-20261124/stage-module-a-2026.1.MANIFEST.before-20261124.tsv`.
- Packaging (`bc8a7b0`): the module A rule pins `R/imputation.R` to `course/module-a-2026.4`. `build()` and
  `dry_run()` read the committed file with git (line ends of the working tree do not matter) and stop with
  "Copy it again" when the stage copy is missing or different. Three new tests; 96 Python tests OK, 2 skipped.
  The dry run on the stage passes the check and gives the same MANIFEST.
- Author script, outside the repositories: `codex_work/module-a-build-20261124/encrypt/encrypt_module_a_2026.1.ps1`
  with `test_open_zip.py`. Not run. Syntax checked with the PowerShell parser. The open-test helper was
  checked on a synthetic ZIP with a throwaway password: right password OK, wrong password refused, password
  not in the output.
- The pin names the branch `course/module-a-2026.4`. After the merge into `course/2026-guided-training`,
  change it in `PACKAGES["module-a"]["pinned"]` before packaging again.

## Publication up to the preview

- Encryption by the author with the script: `module-a-data-2026.1.zip`, 222,857,264 bytes, SHA-256
  `623e15a87a3f9a8e4fd743b6b31ff352840e841fbea2921f004a9e0df123770b`, MANIFEST SHA-256 `46d63ba7...74ac4`
  (equal to the stage MANIFEST). The folder `release-module-a-2026.1.old-password` is an earlier attempt and
  was not used.
- GitHub release `module-a-2026.1` (tag on `196ab4d`, the commit of the package), not "Latest"
  (`project-2026.4` stays latest). Assets: the ZIP, `SHA256SUMS.txt`, `MANIFEST.tsv`. Downloaded again:
  ZIP SHA-256 and MANIFEST equal.
- `SHA256SUMS.txt` of the release has Windows line ends (CRLF): `sha256sum -c` on Linux and macOS reads the
  file names with a trailing CR and fails. The checksums are right (checked with the CR removed). The asset
  was left as published. The packager writes Unix line ends from `119bfb1` on.
- Merge: `course/module-a-2026.4` into `course/2026-guided-training` (was `1e05565`), `--no-ff`, no
  conflict: `fa6d067`. Then `61a1ade`: the module A pin names `course/2026-guided-training` and reads
  `origin/<branch>`; a local branch that differs from origin stops the packager. In this clone the local
  `course/2026-guided-training` is 26 commits behind origin: update it before packaging again. The stage copy
  of `R/imputation.R` equals the file on `origin/course/2026-guided-training`. 97 Python tests OK.
- Website `course/module-a` (`5fed8ec`): sync from `course/2026-guided-training` at `119bfb1` (document links
  point there), module A data URL set, `"A"` in `PUBLISHED_ADDITIONAL_MODULES`. JSON of modules 0 to 7: 72 of
  72 identical to production. tsc 0 errors, ESLint 0 errors. Production build: module A included,
  `check-gwas-production` accepts it. Local production server: module A pages, notebook and figure 200;
  the data button points to the release asset; axe 52 runs, 0 violations. ZIP link 200 (HEAD only). Step 0.3
  still links `GWAS_course-2026.4.zip` (release checksum `dba5184b...0facaa`); step 0.7 answers 200.
  Vercel preview built. No website merge.
