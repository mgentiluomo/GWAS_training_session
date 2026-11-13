# Optional extension: 1000 Genomes

This document describes the older demonstration's optional extension. In the
guided 2026 main path the GRCh38 reference is part of
[module 5](../lessons/module_05_population_structure.Rmd): reference PCA,
study projection and within-cohort PCs are separate tested operations.

[Course home](../README.md) · [Lesson 2](../legacy/demo_2025/02_population_structure.Rmd)

The [original PCA notebook](https://github.com/mgentiluomo/GWAS_training_session/blob/2025-original/01_Codes/02_PCA_GWAS_training_session_2025.Rmd)
includes a reference-panel exercise. It is historical material, not a validated
extension of the guided workflow: its paths and PLINK 1.9 merge commands differ.

## Before merging

Document both sources and releases. Confirm genome build, chromosome naming,
positions, unique variant IDs and allele coding. Identify palindromic A/T or C/G
sites, multiallelic records and duplicates. A matching rsID alone is insufficient.

Use well-called common autosomal variants shared by the datasets; audit unmatched
and excluded sites. Resolve merge failures by cause, rather than assuming every
mismatch is a strand flip. BED/BIM reference labels are not necessarily validated
against a reference genome.

## Questions to investigate

1. Do study samples overlap reference patterns across multiple PCs?
2. Could platform differences or differential missingness explain separation?
3. Would projection avoid distortion from unequal study/reference sizes?
4. Is a proposed cohort restriction justified independently of association results?
5. Does the interpretation change with variant selection or reference choice?

Two-PC distances are exploratory, not definitive ancestry classifications. Do not
equate reference labels with ethnicity or nationality. If the cohort changes,
recompute PCs and covariates, and reconsider control-only HWE diagnostics.

See [PLINK PCA and projection](https://www.cog-genomics.org/plink/2.0/strat).
