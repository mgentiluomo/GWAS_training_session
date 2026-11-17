# Removing step 6.2: what changes outside the repository

Written for the course author. Step 6.2 ("The additive logistic model") is removed. Its text and code moved into step 6.1. Steps 6.3 to 6.8 are now 6.2 to 6.7. Nothing was published. The change is on the branch `course/2026.5`.

## The new numbering

| Old step | Title | New step |
| --- | --- | --- |
| 6.1 | One variant by hand | 6.1 (now also holds the logistic model) |
| 6.2 | The additive logistic model | removed, merged into 6.1 |
| 6.3 | Prepare covariates | 6.2 |
| 6.4 | Run the association scan | 6.3 |
| 6.5 | Read association output | 6.4 |
| 6.6 | Sparse genotypes and Firth correction | 6.5 |
| 6.7 | First look and association checkpoint | 6.6 |
| 6.8 | Create the summary statistics file | 6.7 |

Module 6 now has 7 steps. The main path has 63 steps (it had 64).

## Inside the repository (done)

The lessons, the text of steps in modules 6 and 7, the chunk labels, the output file prefixes (`s6-4_association` is now `s6-3_association`, and so on), `R/guided.R`, `R/course.R` (restart table), the checkpoint registration (`guided_register`, `guided_artifact_checkpoint`), `check_step()` expectations, the nine notebooks, the exported JSON, `scripts/run_main_path.R`, the tests, the glossary and `CLAUDE.md`. The step count checks (64 to 63) and the module step counts are updated in the exporter and its test.

## Outside the repository (you must act)

1. **Data release (`data-2026.1`).** The checkpoint folders and the file names inside them carry the old numbers. The old data release does not work with the new project and the other way round. A new data release is needed together with the new project release. The new staging folder `classroom-stage-2026.2` has the new names. The mapping for the folders is: `6.3` to `6.2`, `6.4` to `6.3`, `6.5` to `6.4`, `6.7` to `6.6`, `6.8` to `6.7` (the folders `6.1`, `7.6` and `7.8` keep their names). The rows of `checkpoints/index.tsv` change in the same way, including the `parent` column.
2. **Instructor key.** `answer_key.json` and `build_report.md` in `sim2026\instructor` use the old step numbers in places. They were not changed. New files `answer_key_2026.2.json` and `build_report_2026.2.md` sit beside them.
3. **Project and data must be released together.** A student who has the new project and the old data (or the reverse) gets "unexpected checkpoint" or "file not found" errors. The password form and step 0.7 stay the same, but `config.R` must point to the new data archive and its SHA-256.
4. **Website addresses.** The step pages `/teaching/gwas/module-6/step-6-N` change meaning. There is a conflict: the old and new numbers share the same addresses. Old `step-6-3` is now `step-6-2`, but `step-6-3` still exists and shows what used to be `step-6-4`. A permanent redirect can only be set for an address that no longer exists. The only address that no longer exists is `step-6-8`, and the preview branch redirects it to `step-6-7`. The other old addresses cannot be redirected without hiding the new pages. Old links are rare (the course is in beta and is not indexed). I made this choice because it is the cautious one: no page is hidden. If you want old links to keep working, the only clean way is a new address scheme for module 6 (for example `step-6-1` to `step-6-7` under `/module-6/`, with the old ones under a legacy path), which needs a decision.
5. **Students' own notes and saved scripts.** A student who wrote down `restore_checkpoint("6.8")` or `check_step("6.4")` needs the new number. Add a line to the release notes. The notebooks are regenerated, so the numbers inside them are correct.
6. **Screenshots and figures.** `docs/screenshot_list.md` has no module 6 entries. No figure file of module 6 uses a step number.
7. **Published notebooks on the website.** `public/gwas/notebooks/` is copied by `npm run sync:gwas`. The preview branch carries the new copies.
8. **Release notes and changelog.** Mention the renumbering in the notes of the new release.
9. **Earlier release assets** (`project-2026.1` to `project-2026.4`) stay as they are and use the old numbering. They must not be mixed with the new data.
