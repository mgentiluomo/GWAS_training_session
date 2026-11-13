# Open checks and author decisions, 12 November 2026

No executable main-path step remained failed after three attempts. The complete
0–7 run, generated script and seven restart integrations passed on Windows.
The items below are delivery/platform limits, not silently accepted QC failures.

## Before classroom distribution

### Windows: inherited C.UTF-8 locale prevents UTF-8 table reading

Observed on 13 November 2026 with R 4.5.2 on Windows. A child R process
inheriting `LANG=C.UTF-8` or related `LC_*` requests emits startup warnings
such as `Setting LC_CTYPE=C.UTF-8 failed`. The UTF-8/BOM table regression then
stops with `Could not safely read locale.tsv: invalid input found on input
connection`. A Windows student with this inherited locale cannot reliably
read UTF-8 course tables containing accented text. This is an environment
failure, not a genotype, threshold or analysis failure.

Removing `LANG`, `LANGUAGE`, `LC_ALL` and every `LC_*` variable only from the
child process environment allowed the unchanged `scripts/check_course.R` to
finish: `Syntax and identifier/p-value safeguards passed.` The parent shell
and Windows language settings were not changed.

Proposed fix, not implemented: extend `R/session_locale.R` to recognise
unsupported inherited UTF-8 locale aliases on Windows, clear those requests
for the R process and recover a working native Windows character locale even
after startup has fallen back to `C`. Keep `LC_NUMERIC=C`, preserve supported
locale requests and leave operating-system settings unchanged. Add a fresh
Windows subprocess regression with inherited `C.UTF-8`, checking accented
UTF-8/BOM table reading and restoration of unrelated session settings. Check
the realised `LC_CTYPE` after recovery rather than assuming that clearing an
environment variable repairs an already-started process. Startup warnings
can precede any R helper, so document that limit and the process-only launch
workaround as well. `R/session_locale.R` is unchanged in this revision.

1. Run the new main-path notebooks and preflight package preparation on Linux
   and macOS. The earlier author-reported Ubuntu archive extraction result does
   not validate the whole new notebook path or every Posit binary repository.
2. The masked `getPass` prompt, the first-time package installation and the Knit
   button were checked by the author in RStudio on Windows with R 4.5.2 on
   12 November 2026 (reported by the author, not repeated by the automated runs).
   The same checks remain to do on macOS and Linux. Automated tests mock the
   prompt or supply the local test password at runtime.
3. Review the staged main-path package, then create its AES-256 archive with a
   classroom password supplied outside the repository. Create `data-2026.1` and
   replace both URLs and both trusted hashes in `config.R`. The current 55-file
   test ZIP and its password must not become the classroom release.
4. Approve the classroom use of the current
   dataset dimensions and documented study-specific review rules. The HWE rule
   is calibrated at 1,000 controls and becomes more stringent above that size;
   it reproduces the existing reference cutoff for this dataset. It is a
   teaching policy, not a universal research recommendation.

## Known scope and verification limits

- Intermediate `check_step` checks compare expected counts; full genotype
  boundaries also compare file hashes. Small diagnostic/analysis checkpoints
  use SHA-256 manifests. Matching intermediate counts alone cannot establish
  genotype identity. The separate author integration test did compare complete
  restored metadata and genotypes, reporting zero differences at seven targets.
- Imported REF labels are provisional unless checked against a genomic reference.
  The notebooks audit agreement between supplied allele pairs and coordinates;
  they do not claim independent FASTA validation or causal gene identification.
- The isolated lift-over exercise retains same-chromosome mappings and reports
  reverse/unmapped sites. Its output is not position-sorted; sort explicitly
  before a later operation that requires order. It is not used as main-path input.
- Installer clicks and a complete clean-machine setup have not been executed.
  Full HTML rendering and actual analytical plots were checked on the author
  machine; this is not a WCAG certification or a test of every browser/device.
- Automated screenshots of a temporary all-expanded HTML review copy were blank.
  Original module 0/7 browser captures worked, all six result images were
  embedded with alt text, and the analytical PNGs were visually inspected.
  Manually opening each expected-result panel in the target classroom browser
  remains a presentation check; no executable analysis step depends on it.
- Figure prompts in the website JSON are unreviewed placeholders. No website
  has been deployed; visual mockup approval is still required before site work.
- Modules A/B, imputation work and post-GWAS analysis remain outside this session.
