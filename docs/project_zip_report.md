# Student project ZIP verification, 13 November 2026

No release was created and no file uploaded. The project-file rename is the
separate local commit `8fb4ea4`. Other reviewed source changes remain
uncommitted. The ZIP is a working-source snapshot; its per-file hashes, not
that commit alone, identify its complete contents.

| Item | Result |
| --- | --- |
| Release tag | `project-2026.1` |
| Asset | `GWAS_course-2026.1.zip` |
| Checksum sidecar | `GWAS_course-2026.1.zip.sha256` |
| Files | 52 |
| ZIP bytes | 162873 |
| Uncompressed file bytes | 496346 |
| SHA-256 | `ce4ebea3111093c7c05dbb19df21de1de61353da0ae0fef734117911590f9443` |
| Outer folder | `GWAS_course/` |
| Local links and anchors | 423 checked; all resolve inside the ZIP |
| Website requests | 70 HTTP 2xx; six HTTP 403; asset URL pending publication |

The ZIP, checksum and machine-readable inventory are outside the repository:
`C:/WEB_site/data_sources/codex_work/project-2026.1-review-20261113-checked/`.
`project-verification.json` lists every source hash, local target, website URL,
HTTP result and fresh-test log directory. A website request blocked with
HTTP 403 remains unverified. No other HTTP error remained in the final run.
The future project asset URL cannot resolve until the author publishes it.

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

- The 22 guided-export tests and four project-package tests passed.
- The text check reported zero errors and zero warnings.
- ZIP CRC, exact member inventory, source-byte equality and SHA-256 passed.
- Two builds from the same sources produced identical ZIP bytes.
- The fresh extracted project passed with folder name `GWAS_course`.
- The same project passed after its folder was renamed `GWAS_training_session`.
- Each folder passed root-file checks, R version display, `2 + 3`, syntax and
  identifier/p-value safeguards, package availability and the PLINK preflight.
- Child R processes inherited no `LANG`, `LANGUAGE` or `LC_*` requests.
  Parent-shell and operating-system settings were unchanged.
- Verified existing classroom inputs were supplied externally. PLINK was
  copied into the extracted `bin/` after extraction, following step 0.6.
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
