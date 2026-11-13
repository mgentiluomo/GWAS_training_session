# Separate legacy demonstration

The older 600-sample demonstration lives in `legacy/demo_2025/`. Use
[modules 0 to 7](../README.md) for the current guided course. Do not mix the
two datasets or their checkpoints.

| Notebook | Purpose |
| --- | --- |
| [Quality control](../legacy/demo_2025/01_quality_control.Rmd) | Inspect files, run QC and save the demo checkpoint. |
| [Population structure](../legacy/demo_2025/02_population_structure.Rmd) | Calculate PCs and prepare the analysis cohort. |
| [Association](../legacy/demo_2025/03_association.Rmd) | Fit models and interpret the results. |

Open `GWAS_course.Rproj` at the repository root, then the notebook.
Run the notebooks in the order above. Run commands from the project root.

The builder `scripts/build_tutorial.py` reads the quality-control notebook in
this legacy folder. With the demo outputs prepared, `python -B
scripts/build_tutorial.py` rebuilds `tutorial/index.html`. The separate guided
export flags still build modules 0 to 7 without loading demo data.

The notebooks also remain in Git history at commit `4c99e7c`. The
[2025-original tag](https://github.com/mgentiluomo/GWAS_training_session/tree/2025-original)
contains the original 2025 material, not these later demonstration notebooks.

The static [browser draft](../tutorial/index.html) is historical. Its numbers,
checkpoints and teaching sequence do not belong to the guided 2026 main path.
Do not mix its data or outputs with the current course.

The archived RStudio installation link is the
[official RStudio Desktop download page](https://docs.posit.co/ide/user/download.html).
