# Website step content schema, version 1.0

The canonical sources are `lessons/module_00_*.Rmd` through
`lessons/module_07_*.Rmd`. Do not edit generated JSON or the combined R script.
Regenerate both without reading genotype data or building the older demo site:

```sh
python -B scripts/build_tutorial.py --export-steps site_content/steps --export-main-script scripts/run_main_path.R
```

The command creates 64 JSON files, one per main-path step. It does not generate
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
| `setup_code` | string | Student setup required before the step. Excludes the `knit_setup` chunk. Empty when no setup is needed. |
| `r_commands` | array | Source chunk `label`, literal R `code`, and boolean `run_by_default`. |
| `notebook_only_expected_code` | array | Render-only R helpers extracted from expected-result blocks; never display these as student instructions on the website. |
| `plink` | object | Boolean `applicable`, literal `commands`, and one explanation per unique option name. |
| `interactive_data` | optional object | Count-only threshold table at step 3.2; see below. |
| `figures` | array | Schematic placeholders or screenshot records. Both have `kind`, nullable `asset`, `alt_text` and `reviewed`. Screenshot fields are described below. |

The block keys are `what_we_do`, `why`, `you_need`, `command`,
`expected_result`, `troubleshooting`, optional `what_this_check_can_reveal`,
`quick_check` and `files_created`. Preserve this order. Expected results and
troubleshooting are collapsed by default; quick-check answers retain their
native `<details>` markup. Keep step numbers visible and provide previous/next
navigation when the approved website design is implemented.

Chunks labelled `knit_setup` contain only notebook rendering configuration.
They run when knitting a notebook. The website setup and combined R script omit
them. Keep student setup, such as loading `R/guided.R` and initialising `cfg`,
in a separate chunk. Do not mix it into `knit_setup`.

Steps 0.1 to 0.4 have no R command blocks and no `setup_code`.
Their `r_commands` arrays are empty and their verification is `manual_required`.
They use operating system settings and installer windows. R checks start later.
Render an empty command array without a code panel. Hide the module setup panel
when `setup_code` is empty. The operating system and version checks run at 0.7.

`windows_executed` refers to the executable R chunks, not to untested installer
clicks or masked GUI prompts. Step 0.5 is `manual_required`: its interactive
download chunks are intentionally not run by the whole-path script. Local ZIP
extraction and the URL branch have separate integration/mocked tests.

PLINK option explanations come from the step's prose. Each `plink.options` entry has `name` and `explanation_markdown`, containing
only the sentence or clause explaining that option. Shared options may reuse
an explanation from an earlier step of the same module. These entries also
have `explained_at`, the originating step ID (for example `3.1`). Locally
explained options omit this field. Forward references and cross-module
fallbacks are forbidden; the exporter rejects an option with no explanation. Laboratory and R-only steps explicitly
have `plink.applicable = false`; do not invent a PLINK command for a laboratory
measurement. Terminal commands use the standard project paths; the R helper
prints exact safe paths at runtime. Rendering a command must preserve quotes,
dollar signs and template strings such as `@:#:$r:$a`.

Screenshot declarations are stored in notebook HTML comments beside the
relevant teaching block. They are removed from exported text blocks. For example:

```html
<!-- screenshot: {"kind":"screenshot","asset_path":"Figures/screenshots/s0-3_rstudio_console_windows.png","platform":"windows","placement":"expected_result","alt_text":"RStudio on Windows with the Console tab selected and an empty R prompt."} -->
```

The exporter adds a `figures` record with these fields:

| Field | Meaning |
| --- | --- |
| `kind` | `screenshot`. A real software capture, not an illustration prompt. |
| `asset_path` | Planned PNG path relative to the repository, under `Figures/screenshots/`. |
| `asset` | `null` until that file exists. Then the same repository-relative path as `asset_path`. |
| `platform` | `windows` or `macos`. |
| `placement` | A teaching block key, such as `what_we_do`, `command`, `expected_result` or `troubleshooting`. |
| `alt_text` | Draft accessible description from the notebook. |
| `reviewed` | `false`. File existence alone does not establish privacy or teaching review. |

Screenshot records have no `gemini_prompt`. The exporter never creates images.
It rejects paths outside the repository and duplicate screenshot paths within
a step. Rendering should show the matching platform capture beside its named
block. A `null` asset must not create a broken image. Keep expected results and
troubleshooting collapsed. The [capture list](screenshot_list.md) records what
to show, what to hide and the draft alt text for each planned file.

Figure placeholders are not generated images or verified result figures.
Gemini prompts request a schematic to complement the actual analytical plot,
without invented results or individual identities. A future author must review
the image, add a suitable asset, and replace the provisional alt text before
publication. Tested data plots remain external generated outputs. Meaning must
not rely on colour alone; the renderer must preserve text summaries and labels.

Gemini production prompts are stored in notebook HTML comments and exported
only as figure metadata. They are not displayed in student-facing text blocks.

JSON contains code, teaching text and the explicitly allowed aggregate table
below, never the instructor key, phenotype records, sample identifiers,
passwords, archive bytes or individual analytical records. The R script
omits `eval=FALSE` chunks for interactive installation and data retrieval. It
starts from already installed tools and verified data, and executes modules
0â€“7 in order. Set `COURSE_DATA_DIR`, `COURSE_OUTPUT_DIR` and, if needed,
`COURSE_CHAIN_FILE` before running it from the project root.

This export prepares source content only. It is not a website implementation;
the visual mockup still requires approval before site work.

Step 3.2 has an `interactive_data` object with these fields:

| Field | Meaning |
| --- | --- |
| `kind` | `sample_call_rate_threshold_counts`. |
| `source_state` | `3.1`, after both rough sample and variant filters, before step 3.2. |
| `sample_count` | 2,013 measured wells in that fixed input state. |
| `comparison` | `strictly_below`: equality passes. Counts are cumulative, not histogram bins. |
| `call_rate_definition` | `100 * (OBS_CT - MISSING_CT) / OBS_CT`, using the PLINK sample report's integer counts and default hardcall missingness. |
| `source_report_sha256` | SHA-256 of the external `.smiss` report used for authoring. The report itself is never committed. |
| `rows` | 20 records with `threshold_percent` (90 to 99.5 inclusive, increment 0.5) and integer `samples_below`. No sample IDs or per-sample rates. |

All thresholds use the same state-3.1 denominator and variant set. They do not
rerun preceding QC filters. At 98%, the count is 42, matching the exclusions at
step 3.2. Other steps omit `interactive_data` when no aggregate is supplied.

The canonical aggregate is stored in a notebook HTML comment, removed from
student-facing blocks and exported as metadata. Ordinary JSON regeneration
still needs no data access. To refresh the aggregate after a validated data
change, generate a report outside the repository and update the notebook:

```sh
bin/plink2 --pfile <external-state-3.1-prefix> --missing sample-only --out <external-report-prefix> --threads 2 --memory 2048
python -B scripts/author/export_call_rate_counts.py --smiss <external-report-prefix>.smiss
python -B scripts/build_tutorial.py --export-steps site_content/steps --export-main-script scripts/run_main_path.R
```

The author tool checks the 2,013 input wells and the 42 exclusions at 98%.
It compares integer cross-products to avoid rounding `F_MISS` at boundaries.
The source report uses PLINK 2.0 b.1.4 (7 November 2026), on the verified Windows
main-path state. It stays external alongside its PLINK command and log.

## Module pages

`site_content/modules/module-N.json` (N = 0 to 7) holds the text that sits around
the steps of one module. It is exported from the same notebook, so it is never
edited by hand.

| Field | Meaning |
| --- | --- |
| `schema_version` | `1.0`. |
| `module`, `title` | Module number and title from the notebook header. |
| `source`, `source_sha256` | Notebook path and the SHA-256 of its text. |
| `overview_markdown` | The "Module N at a glance" section: what the student will do, learn and how long it takes. |
| `recap_markdown` | The "Module N recap" section: a short list of what was done, and a **Next:** line. |

A step ends at the next level-2 heading, so the recap never becomes part of the
last step's "Files created" block.


## Invented format examples

The export also copies the authorised tiny files from `examples/formats/` to
`site_content/formats/examples/`. These are invented reading aids, not classroom
data. It generates one JSON description per example plus descriptions without
assets for IDAT, GTC, CEL, BAM, CRAM and POD5. The descriptions come from
`scripts/author/make_format_examples.py`. Exporting reads existing examples;
it does not run PLINK or generate new genotypes.

Each description has `file_name`, `format`, `encoding` (text or binary),
`producer`, `pipeline_position`, `columns_or_fields` (a name and one sentence per
field), `header_notes`, `magic_bytes` and `asset`. Concrete examples also record
`label`, `size_bytes` and `sha256`. `asset` is relative to the formats folder.
Description-only records have null `file_name`, `asset` and `magic_bytes`; they
link to official documentation. No vendor binary is supplied. Binary examples
have companion hex dumps. Strict indexes and binaries carry the invented-example
label in their filename and JSON because arbitrary comments would corrupt them.
The copied bytes are identical, including newlines and FASTA index offsets.
When resolving notebook links under `../examples/formats/`, the website can use
this catalogue to select the matching asset under `formats/examples/`.

Steps 1.8 to 1.11 have no executable commands and no `setup_code`. Conversion
syntax appears in their reading text only. It never enters the main-path script.
