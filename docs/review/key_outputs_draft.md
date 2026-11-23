# Key output of each module, draft

Written for the course author. This is a draft. It is not exported and not shown on the site.

Each module gets one line that says what the student has at the end of it. The site would show the line in the course map panel and on the module page. That way a student knows where each module leads before starting it.

Every line comes from the `expected_result` and `files_created` fields of the 2026.4 step JSON, as exported to the site (`src/content/gwas/steps/`, site commit `4b54b05`). The last column names the step that each line comes from. No step JSON was changed.

## Lines

| Module | Key output | Source |
|---|---|---|
| 0. Prepare your computer | A working project: the course data verified in `data/course/` (108 files) and a setup check that passes, saved in `results/guided/preflight.txt`. | step 0.7, step 0.8 |
| 1. From DNA to array data | No files. You can read the export: 2,016 sample wells and 299,523 variants, before any QC. | step 1.7 |
| 2. Files and formats | The data in PLINK 2 format, with phenotype and covariates: 2,016 samples and 296,510 variants. | checkpoint 2.8 |
| 3. Sample quality control | A clean set of samples: 1,844 samples and 296,360 variants. | checkpoint 3.8 |
| 4. Variant quality control | A clean set of variants: 1,844 samples and 238,513 variants. | checkpoint 4.6 |
| 5. Population structure | An ancestry-matched cohort of 1,811 samples and 238,513 variants, with ten cohort PCs and a scree plot. | step 5.6, checkpoint 5.7 |
| 6. Association | The summary statistics file `s6-8_gwas_summary_statistics.tsv`: 236,815 tested variants, eight below 5e-8, lambda about 1.016. | checkpoint 6.7, step 6.8 |
| 7. Plots and reporting | A final report: `s7-8_summary.md`, the three lead variants with alleles, odds ratios and intervals in `s7-8_leads.tsv`, and all main figures. | checkpoint 7.8 |

The module titles are the `title` fields of the 2026.4 module JSON.

## Proposal for the site

- Store the line in the module JSON, in a new field, for example `"key_output": "A clean set of samples: 1,844 samples and 296,360 variants."`, with the source step in a second field, for example `"key_output_step": "3.8"`.
- Export it with release 2026.5. The site shows it under the module title in the course map panel, and near the top of the module page, as "You finish with: ...".

## Notes for review

- These numbers are those of 2026.4. Release 2026.5 changes module 6: the old step 6.2 is removed, the summary statistics move to step 6.7, and the 2026.5 source counts 236,820 tests instead of 236,815 (see `release_2026-11-19.md`, section 3, finding 7). Lines 6 and 7, and possibly 3 to 5, must be checked against the 2026.5 export before they go into the JSON.
- Module 1 has no files. Its line describes what the student can read, not a file. If you prefer, it can say what the student understands instead, for example "You know how an array turns DNA into genotype calls, and which errors start in the laboratory."
- Module 5 cites two steps: 5.6 gives the 1,811 samples, and checkpoint 5.7 holds the PCs.
- Module 6 cites checkpoint 6.7 for lambda and the eight hits, and step 6.8 for the file. Step 6.8 also writes `checkpoints/6.8/MANIFEST.tsv`.
