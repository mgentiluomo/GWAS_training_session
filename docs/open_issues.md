# Open checks and author decisions, 12 November 2026

No executable main-path step remained failed after three attempts. The complete
0–7 run, generated script and seven restart integrations passed on Windows.
The items below are delivery/platform limits, not silently accepted QC failures.

## Before classroom distribution

1. Run the new main-path notebooks and preflight package preparation on Linux
   and macOS. The earlier author-reported Ubuntu archive extraction result does
   not validate the whole new notebook path or every Posit binary repository.
2. Test the masked `getPass` prompt interactively in RStudio on each platform.
   Automated tests mock the prompt or supply the local test password at runtime.
3. Review the staged main-path package, then create its AES-256 archive with a
   classroom password supplied outside the repository. Create `data-2026.1` and
   replace both URLs and both trusted hashes in `config.R`. The current 55-file
   test ZIP and its password must not become the classroom release.
4. Confirm the proposed licences and approve the classroom use of the current
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
