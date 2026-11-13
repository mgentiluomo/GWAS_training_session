# Student project ZIP verification, 13 November 2026

No release was created and no file uploaded. The ZIP was built with
`scripts/package_project.py --fresh-check --check-urls` from the pushed commit
`e4ede0f3f29d5a60c4e66243295ffc0b8b04085d` on `course/2026-guided-training`,
with a clean working tree before and after the build. All 52 members are
byte-identical to that commit.

It replaces two earlier builds. The working-source snapshot
`ce4ebea3111093c7c05dbb19df21de1de61353da0ae0fef734117911590f9443` was built
before the source changes were committed. The build from commit `f06116a`
(`377de24a5b287adcae34ecbc8a87dfb8acfeba4ad02bc2353403b7bc61e9b992`) differs
from this one in two members only, both changed by commit `61ec467`, which
removed a Markdown link from the step 6.2 `success_line`:
`lessons/module_06_association.Rmd` (the `step_meta` comment) and
`scripts/run_main_path.R` (its module 6 SHA-256 comment). This report is not
a ZIP member, so committing it does not change the ZIP.

| Item | Result |
| --- | --- |
| Release tag | `project-2026.1` |
| Asset | `GWAS_course-2026.1.zip` |
| Checksum sidecar | `GWAS_course-2026.1.zip.sha256` |
| Source commit | `e4ede0f3f29d5a60c4e66243295ffc0b8b04085d` (pushed; clean tree) |
| Files | 52 |
| ZIP bytes | 163044 |
| Uncompressed file bytes | 496830 |
| SHA-256 | `2902bb25c08392b2640b115314c3e1c7160923d898b66a31318af99b47783b0d` |
| Outer folder | `GWAS_course/` |
| Local links and anchors | 423 checked; all resolve inside the ZIP |
| Website requests | 77 checked: 70 HTTP 2xx (54 with 200, 16 with 203); six HTTP 403; the project asset URL pending publication |
| Fresh-folder test | Passed as `GWAS_course` and after renaming to `GWAS_training_session` |

The ZIP, checksum and machine-readable inventory are outside the repository:
`C:/WEB_site/data_sources/codex_work/project-2026.1-review-20261113-claude-2/`.
`project-verification.json` lists every source hash, local target, website URL,
HTTP result and fresh-test log directory. A website request blocked with
HTTP 403 remains unverified. No other HTTP error remained in the final run.
The project asset URL,
`https://github.com/mgentiluomo/GWAS_training_session/releases/download/project-2026.1/GWAS_course-2026.1.zip`,
cannot resolve until the author publishes it.

## Final allowlist

Only these 52 student files are included. Directory selection is restricted to
tracked notebook sources, R sources and the authorised tiny invented examples.
Untracked files in those directories are not collected.

- `GWAS_course.Rproj`
- `LICENSE`
- `LICENSE-CONTENT.md`
- `R/course.R`
- `R/guided.R`
- `R/package_setup.R`
- `R/session_locale.R`
- `README.md`
- `bin/README.md`
- `config.R`
- `docs/data.md`
- `docs/glossary.md`
- `docs/international_setup.md`
- `docs/setup.md`
- `docs/troubleshooting.md`
- `examples/formats/invented_example.bgen`
- `examples/formats/invented_example.bgen.hex.txt`
- `examples/formats/invented_example.sample`
- `examples/formats/invented_example_alignments.sam`
- `examples/formats/invented_example_dosages.vcf`
- `examples/formats/invented_example_final_report.txt`
- `examples/formats/invented_example_intervals.bed`
- `examples/formats/invented_example_multisample.vcf`
- `examples/formats/invented_example_plink1.bed`
- `examples/formats/invented_example_plink1.bed.hex.txt`
- `examples/formats/invented_example_plink1.bim`
- `examples/formats/invented_example_plink1.fam`
- `examples/formats/invented_example_plink1.map`
- `examples/formats/invented_example_plink1.ped`
- `examples/formats/invented_example_plink1_transposed.tfam`
- `examples/formats/invented_example_plink1_transposed.tped`
- `examples/formats/invented_example_plink2.pgen`
- `examples/formats/invented_example_plink2.pgen.hex.txt`
- `examples/formats/invented_example_plink2.psam`
- `examples/formats/invented_example_plink2.pvar`
- `examples/formats/invented_example_reads.fastq`
- `examples/formats/invented_example_reference.fasta`
- `examples/formats/invented_example_reference.fasta.fai`
- `examples/formats/invented_example_sample.g.vcf`
- `examples/formats/invented_example_summary_statistics.tsv`
- `lessons/module_00_preparation.Rmd`
- `lessons/module_01_from_dna_to_array_data.Rmd`
- `lessons/module_02_files_and_formats.Rmd`
- `lessons/module_03_sample_quality_control.Rmd`
- `lessons/module_04_variant_quality_control.Rmd`
- `lessons/module_05_population_structure.Rmd`
- `lessons/module_06_association.Rmd`
- `lessons/module_07_plots_and_reporting.Rmd`
- `scripts/check_course.R`
- `scripts/install_packages.R`
- `scripts/preflight.R`
- `scripts/run_main_path.R`

All other paths are excluded. In particular, there are no classroom data,
PLINK binaries, instructor files, author scripts, build folders, website
exports, tutorials, legacy notebooks, author working documents or caches.
The inventory and reports stay beside the ZIP, not inside it.

## Verification

- Before the commits, the full check set passed on Windows with R 4.5.2: text
  check (zero errors, zero warnings), guided-export tests, `check_course.R`,
  the preflight output test, the project-package tests, the other R tests, the
  author tests, the legacy tutorial build, `test_guided_modules.R` for modules
  0 to 7 and `test_main_path_recovery.R` on the staged classroom data.
  `test_package_release.py` needs `COURSE_RELEASE_PASSWORD` and
  `check_tutorial.cjs` needs Playwright; neither was available.
- ZIP CRC, exact member inventory, source-byte equality and SHA-256 passed.
  The SHA-256 sidecar matches a recomputed hash.
- The fresh extracted project passed with folder name `GWAS_course`.
- The same project passed after its folder was renamed `GWAS_training_session`.
- Each folder passed root-file checks, R version display, `2 + 3`, syntax and
  identifier/p-value safeguards, package availability and the PLINK preflight.
- Child R processes inherited no `LANG`, `LANGUAGE` or `LC_*` requests.
  Parent-shell and operating-system settings were unchanged.
- Verified existing classroom inputs were supplied externally. PLINK was
  copied into the extracted `bin/` after extraction, following step 0.6
  (PLINK 2.0 b.1.4 executable SHA-256
  `05255a1945e03108b06948993a95fe8341ab3cd903b6ff55b0dfc5a067dcfa00`).
  Neither the data nor the executable is a ZIP member.

The first fixture used an external `PLINK2_BIN` path and failed in Windows
`system2` when invoking its relative path. The final fixture follows the
student installation sequence instead. No R code or analytical check was
changed to pass it. The earlier fixture logs remain outside the repository.
RStudio GUI opening, installer interaction and macOS/Linux execution were
not exercised. No analysis threshold or expected number changed in this task.

## Website requests requiring manual review

- https://community.ukbiobank.ac.uk/hc/en-gb/articles/15468170680605-Genome-wide-genotyping
- https://community.ukbiobank.ac.uk/hc/en-gb/articles/26272701015837-Initial-DRAGEN-whole-genome-sequencing-WGS-data-release
- https://community.ukbiobank.ac.uk/hc/en-gb/articles/26273057297949-ML-Corrected-DRAGEN-whole-genome-sequencing-WGS-release
- https://support.researchallofus.org/hc/en-us/articles/14927774297620-The-new-VariantDataset-VDS-format-for-All-of-Us-short-read-WGS-data
- https://www.chg.ox.ac.uk/~gav/bgen_format/spec/v1.2.html
- https://www.completegenomics.com/products/sequencing-platforms/dnbseq-t7-plus/

These six official sources returned HTTP 403 to the automated client. They
were retained and explicitly marked unverified. Review them in a normal browser
before publication. The versioned project asset is the only planned link.
