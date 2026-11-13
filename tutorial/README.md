# Archived browser draft

`index.html` is the separate older demonstration. Its analysis and numbers remain
unchanged. Notebook links point to `legacy/demo_2025/` on the guided branch.
See [the legacy guide](../docs/legacy_demo.md).

The current source export is:

```sh
python -B scripts/build_tutorial.py --export-steps site_content/steps --export-main-script scripts/run_main_path.R
```

To rebuild the legacy browser tutorial, prepare the demo outputs with
`GWAS_RUN_DEMO_CHECK=1` and `scripts/check_course.R`, then run:

```sh
python -B scripts/build_tutorial.py
```

The builder reads `legacy/demo_2025/01_quality_control.Rmd` and the existing
demo outputs. It does not use the guided notebooks for this legacy HTML.
