# Different computers, one data convention

[Course home](../README.md) · [Setup](setup.md) · [Troubleshooting](troubleshooting.md)

You can keep your operating system in your preferred language. The course uses
the same file conventions on Windows, macOS and Linux. Language and regional
settings vary independently; check the files rather than guessing from a student's
language, nationality or operating system.

## The conventions we use

| Item | Course convention | Example |
|---|---|---|
| Decimal separator | Point | `23.5` |
| Thousands separator | None | `12500`, not `12,500` or `12.500` |
| Table separator | Tab for metadata and generated TSV files | Separate FID, IID, Age and Group columns |
| Text encoding | UTF-8 | Accents and other alphabets remain text |
| Missing values | Explicit field-specific codes | `NA` in R tables; phenotype `-9` for PLINK |
| Sample identifiers | Text, unchanged | `00123` must keep its initial zeros |
| File paths | Built by the project | No manual translation of a Desktop folder name |

PLINK's native text formats may use spaces or tabs according to their format.
Do not change them to a regional CSV convention. Scientific notation such as
`5e-8` is valid. A decimal comma or a grouping separator in a required numeric
field stops the course import with a message; it is not silently changed.

## Decimal mark and column separator are different

These are two representations of a similar table, but they need different import
instructions:

```text
# Course TSV: tabs between columns, points within numbers
FID     IID     Age
001     001     23.5

# A possible regional CSV: semicolons between columns, commas within numbers
FID;IID;Age
001;001;23,5
```

The spacing above illustrates columns; use the actual downloaded files, not this
display example, as analytical input. A `.csv` extension alone does not tell you
which convention was used. Never replace every comma in a file: it could change
separators, labels or an ambiguous value such as `1,234`.

For this course, use the supplied files unchanged. If another project supplies a
regional CSV, first confirm its documented delimiter, decimal mark and encoding,
then import it separately with explicit settings and validate it before conversion.

## Avoid an Excel round trip

Opening and resaving analytical inputs in a spreadsheet can change identifier
zeros, dates, delimiters and numeric formatting. Inspect tables in RStudio's data
viewer or a text editor. Keep the original files and write derived outputs to a
new file. The course does not require Excel.

## What the setup changes

`course_config()` sets R's decimal display option to `.` for the current R
session. It does not change your operating-system language or regional settings.
Imports specify the format, numeric fields are validated, exports specify decimal
points and UTF-8, and numeric PLINK thresholds are formatted explicitly. The
software record includes locale information to help diagnose a problem.

## Paths and keyboards

- Extract and open the complete RStudio project. Paths are built with `file.path()`;
  no instruction depends on a translated name for Desktop or Downloads.
- Spaces and non-English characters are tested in Linux paths. Windows/macOS
  execution still requires platform checks; if an external tool rejects a path,
  try a short writable project folder such as `C:/gwas_training` or a
  `gwas_training` folder in your home directory, while keeping your original copy.
- Copy code using plain quotes (`"` or `'`) and ordinary minus signs (`-`). Smart
  quotes and typographic dashes pasted from formatted documents are not R syntax.
- Use the notebook's Run button if keyboard shortcuts differ on your keyboard.
  Identify RStudio panes by their purpose, not only by an English menu label.

## Before the first class

Run `source("scripts/preflight.R")` from the project root. It reports the system,
numeric conventions, writable output location, input file consistency and
whether PLINK can read data and write results in a path containing spaces and
non-English characters. It is a diagnostic, not a guarantee that every later
analysis or operating-system configuration will succeed.

If it stops, keep the error message and the generated `preflight.txt`. You can
still read the tutorial and discuss the supplied examples while resolving setup.

### A quick self-check

An input has headers `FID;IID;Age` and a value `24,5`. Will renaming it from
`.csv` to `.tsv` make it a valid course input? Explain what needs to be checked.

## Reference

R's official documentation describes [input delimiters and decimal marks](https://stat.ethz.ch/R-manual/R-devel/library/utils/html/read.table.html),
[output formatting](https://stat.ethz.ch/R-manual/R-devel/library/utils/html/write.table.html)
and [locale settings](https://stat.ethz.ch/R-manual/R-devel/library/base/html/locales.html).
