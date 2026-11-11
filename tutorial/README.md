# Browser tutorial — review draft

Open `index.html` in a browser. The file contains its styles, scripts, example
data for the slider and scientific figures; no external JavaScript or font is
required. Data download links point to the review branch on GitHub.

The draft covers preparation and lesson 1. Lessons 2 and 3 link to their tested
RStudio notebooks. It does not run R/PLINK in the browser or collect submissions.
Checklist ticks are stored only in the current browser when local storage is
available. The personal website has not been modified and no website has been
deployed.

## Source and regeneration

`scripts/build_tutorial.py` builds this page using `tutorial_src/`, R chunks from
`lessons/01_quality_control.Rmd` and validated outputs from the default simulated
walkthrough. Do not hand-edit the generated HTML. For authoring, install Python
and matplotlib, run the full demo validation, then:

```sh
python3 scripts/build_tutorial.py
```

The builder packages only enumerated `data/demo/` and `results/demo/` inputs,
checks synthetic FAM identifiers and creates checksum manifests. It refuses to
include non-demo inputs. Checkpoint downloads are versioned derived teaching
assets; they are not expected results for the original class data.

After changing scientific settings or the generator, update the default-demo
checks and explanatory counts, rerun the notebooks, regenerate this page and
repeat browser, link and archive validation. The builder deliberately stops if
the baseline and final dimensions differ from the documented default example.
