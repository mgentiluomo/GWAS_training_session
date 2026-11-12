# Revision checks

## Guided modules 0 to 7: verified on Windows, 12 November 2026

- Windows 11 x64, R 4.5.2, PLINK 2.0 b.1.4 AVX2, build 7 November 2026.
- All eight guided notebooks executed in order in a fresh external output
  folder, with a new module environment and the fixed block-order checks.
- Initial data: 2,016 measured wells, 299,523 array entries. Final cohort:
  1,811 samples (900 cases, 911 controls), 238,513 post-QC variants. The final
  cohort MAF filter leaves 236,815 finite additive association tests.
- External instructor key/reference comparisons covered sample removal IDs
  (except interchangeable relative-pair choices), step counts, leading
  regional p-values, eight conventional genome-wide hits and lambda 1.016465.
- The no-PC and no-sample/variant-QC comparisons reproduced 15 and 19 hits;
  autosomal lambda approximately 1.546 and 1.655.
- Seven restart targets passed metadata identity and PLINK `--pgen-diff`
  with missing calls included: zero genotype differences. Diagnostic pruning,
  projection and covariate files were restored with their parent states.
- The `café_α_中文` Windows regression passed using ASCII relative/short paths.
  Invalid inherited locale requests were neutralised in the R process only.
- The generated whole-path R script executed against the staged package in a
  separate external output folder and reproduced the main summary and plots.
- Manhattan, QQ, common-scale comparison QQ and regional plots were visually
  inspected. RStudio's bundled Pandoc was used for notebook HTML rendering.
- Generator, packaging, download, locale, checkpoint and export regression
  checks passed. Data URL tests used mocked local copies, never real downloads.

To execute notebook chunks outside the repository, set `COURSE_DATA_DIR`,
`COURSE_OUTPUT_DIR` and, for the older input folder, `COURSE_CHAIN_FILE`, then run:

```sh
Rscript --vanilla scripts/tests/test_guided_modules.R
```

`COURSE_MODULE_MIN` and `COURSE_MODULE_MAX` can select a module range when its
earlier inputs already exist. The staged classroom folder includes the chain;
the unchanged stage 1 test ZIP does not. See [the session report](docs/session_report.md)
for exact paths, remaining manual checks and release decisions. New main-path
notebooks have not been executed on Linux or macOS. The masked RStudio prompt
and clean-machine installer flow remain untested.

The checks below describe the separate earlier 600-sample demonstration.

## Verified on 11 November 2026

- R 4.5.0 on Linux; PLINK 2.0 beta 1.4, build 7 November 2026.
- All three new notebooks executed in order on the simulated data.
- Each notebook also executed in a separate, fresh R process, with `lessons/` as
  its working directory, using only files saved by earlier lessons.
- Demo QC: 600 samples / 6000 variants initially; 592 samples / 5920 variants at
  the final QC checkpoint. All 5920 additive tests completed in both models.
- Baseline and PC-adjusted models used identical per-variant sample counts.
- PCA, Manhattan and QQ PNGs were generated and visually inspected.
- Original supplied phenotype, sex and covariate tables matched all 3185 samples
  in the original FAM by FID/IID, without modifying those inputs.
- New student-facing entry points have no missing relative file-link targets.
- New R files and notebook chunks parse; chunk labels are unique. Identifier and
  p-value safeguards are checked by the validation script.

## Reproduce the checks

From the project root, with R and PLINK 2 installed:

```r
source("scripts/check_course.R")
```

To additionally regenerate and execute the complete demo (overwrites demo outputs):

```r
Sys.setenv(GWAS_RUN_DEMO_CHECK = "1")
source("scripts/check_course.R")
Sys.unsetenv("GWAS_RUN_DEMO_CHECK")
```

The full check requires `mode = "demo"`. Do not use demo figures as expected
results for the original dataset.

## Browser tutorial checks

The draft in `tutorial/index.html` covers the course home, setup, the full QC
walkthrough, practice, recovery downloads and a glossary. Scientific R blocks
are extracted from the tested QC notebook rather than maintained as a second
analytical implementation.

- Six synthetic-only ZIPs pass archive CRC and SHA-256 manifest checks.
- Restoring only the final QC ZIP into a clean project allowed lessons 2 and 3
  to execute in fresh R processes without the initial genotype input or an R workspace.
- Chromium headless browser checks cover navigation, operating-system panels,
  copy fallback, local checklist persistence, missingness slider, quiz feedback,
  worked explanations, all six download cards and the mobile navigation menu.
- Widths 390, 768 and 1440 pixels were checked for document-level horizontal overflow.
- Desktop, mobile and a QC section were visually inspected.
- The main heading/navigation identify independent University of Pisa learning
  materials. Omics (552EE) appears once in the web page, as a possible teaching
  context; the twelve-hour route is explicitly optional.
- With JavaScript disabled, the written pages and all OS instructions remain
  readable. The quiz has no form submission, including in that mode.

Run `node scripts/check_tutorial.cjs` with Playwright and compatible Chromium
installed; `TUTORIAL_BROWSER` selects an executable. This browser QA is an
authoring check, not a student prerequisite. It does not certify every browser
or assistive-technology combination. No website deployment is included.

## International-settings regression checks

The full demo and preflight were rerun with R's initial decimal-display option
set to a comma. They also passed under a French-language Linux environment, with
the project and PLINK executable in paths containing spaces, accents, Greek and
Chinese characters. Separate checks cover a UTF-8 BOM, Windows CRLF line endings,
zero-padded identifiers, canonical decimal-point exports and rejection of
decimal-comma numeric fields and semicolon-separated input passed as course TSV.

These checks do not replace execution on Windows and macOS.

## Remaining classroom checks

The original class BED is access-controlled and was not available for a complete
original-data run. Validate its matching release, provenance, genome build,
population structure and study-specific exclusions before teaching with it.
Test institutional access and prepare authorised lesson checkpoints before class.

Windows and macOS instructions have not been executed on those platforms. The
new `.Rmd` source and its generated analytical figures were checked; RStudio's
Knit-to-HTML presentation has not been visually inspected in this environment.
The existing 2025 HTML and notebooks are historical and are not outputs of this
validation. No website has been published or deployment configuration added.
