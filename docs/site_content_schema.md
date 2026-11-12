# Website step content schema, version 1.0

The canonical sources are `lessons/module_00_*.Rmd` through
`lessons/module_07_*.Rmd`. Do not edit generated JSON or the combined R script.
Regenerate both without reading genotype data or building the older demo site:

```sh
python -B scripts/build_tutorial.py --export-steps site_content/steps --export-main-script scripts/run_main_path.R
```

The command creates 59 JSON files, one per main-path step. It does not generate
images, download data, publish a website or create an encrypted release.

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | string | Currently `1.0`. |
| `id`, `module`, `step` | string, integer, integer | Stable identifier such as `3.2` and its components. |
| `anchor` | string | Stable page anchor, such as `step-3-2`. |
| `title` | string | Step title from the notebook. |
| `source` | string | Repository-relative canonical notebook path. |
| `source_sha256` | string | SHA-256 of UTF-8 notebook text with normalised line endings. |
| `verification` | string | `windows_executed`, `manual_required` or `unverified`; read alongside the session report's limits. |
| `blocks` | object | The fixed teaching blocks, in their source order, as Markdown/HTML. |
| `setup_code` | string | Module setup chunks required before the step. |
| `r_commands` | array | Source chunk `label`, literal R `code`, and boolean `run_by_default`. |
| `notebook_only_expected_code` | array | Render-only R helpers extracted from expected-result blocks; never display these as student instructions on the website. |
| `plink` | object | Boolean `applicable`, literal `commands`, and one explanation per unique option name. |
| `figures` | array | Placeholder records: `kind`, nullable `asset`, `gemini_prompt`, `alt_text`, `reviewed`. |

The block keys are `what_we_do`, `why`, `you_need`, `command`,
`expected_result`, `troubleshooting`, optional `what_this_check_can_reveal`,
`quick_check` and `files_created`. Preserve this order. Expected results and
troubleshooting are collapsed by default; quick-check answers retain their
native `<details>` markup. Keep step numbers visible and provide previous/next
navigation when the approved website design is implemented.

`windows_executed` refers to the executable R chunks, not to untested installer
clicks or masked GUI prompts. Step 0.5 is `manual_required`: its interactive
download chunks are intentionally not run by the whole-path script. Local ZIP
extraction and the URL branch have separate integration/mocked tests.

PLINK option explanations come from the step's prose. Shared options may use
their explanation elsewhere in the same canonical notebook set; the exporter
rejects an option with no explanation. Laboratory and R-only steps explicitly
have `plink.applicable = false`; do not invent a PLINK command for a laboratory
measurement. Terminal commands use the standard project paths; the R helper
prints exact safe paths at runtime. Rendering a command must preserve quotes,
dollar signs and template strings such as `@:#:$r:$a`.

Figure placeholders are not generated images or verified result figures.
Gemini prompts request a schematic to complement the actual analytical plot,
without invented results or individual identities. A future author must review
the image, add a suitable asset, and replace the provisional alt text before
publication. Tested data plots remain external generated outputs. Meaning must
not rely on colour alone; the renderer must preserve text summaries and labels.

Gemini production prompts are stored in notebook HTML comments and exported
only as figure metadata. They are not displayed in student-facing text blocks.

JSON contains code and teaching text only, never the instructor key, phenotype
records, passwords, archive bytes or generated analytical tables. The R script
omits `eval=FALSE` chunks for interactive installation and data retrieval. It
starts from already installed tools and verified data, and executes modules
0–7 in order. Set `COURSE_DATA_DIR`, `COURSE_OUTPUT_DIR` and, if needed,
`COURSE_CHAIN_FILE` before running it from the project root.

This export prepares source content only. It is not a website implementation;
the visual mockup still requires approval before site work.
