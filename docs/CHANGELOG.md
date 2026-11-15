# Changelog

## 2026.2 (project release, 15 November 2026)

- Student notebooks are Quarto files (`notebooks/*.qmd`), one per module and one for the whole course.
- Each notebook has a contents list, an "In this module" box, code notes, option tables, a "What you do" box for steps without code, and a glossary appendix.
- Each step has a short student summary. Many texts were reviewed and corrected, for example the definition of odds, the Firth correction, the p-value and the thresholds.
- Module 0 sends students to `notebooks/module_00_preparation.qmd`. The folder list at step 0.3 includes `notebooks`.
- Long code lines wrap in the rendered notebooks.
- PLINK 2 is not in the package. The four non-AVX2 builds are pinned in the `plink/bundle` branch. They wait for the comparison at the office.
- The data release is unchanged (`data-2026.1`).

## 2026.1 (project release)

- First guided course, modules 0 to 7, with the project ZIP and the encrypted classroom data.
