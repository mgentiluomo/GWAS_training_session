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
