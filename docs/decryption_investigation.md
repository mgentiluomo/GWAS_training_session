# AES-256 extraction investigation

## Evidence

On 11 November 2026, R 4.5.2 on Windows 11 extracted the stage 1 AES-256 ZIP
using `archive` 1.1.14. All 55 payload SHA-256 checks passed. A wrong password
was rejected. Extraction and verification took 5.0 seconds. `digest` 0.6.39
provided hashing. All investigation packages were installed under `codex_work/`.
No system library or repository data directory was populated.

Reproduce with `scripts/author/probe_archive.R`. Set `COURSE_WORK_DIR` to the
existing authorised work folder containing `release/`. Set `TMP` and `TEMP`
beneath that folder before starting R. Supply the test password through
`COURSE_RELEASE_PASSWORD`. The script creates a fresh extraction directory on
each run. Missing packages use binary installation on Windows and macOS and
source installation on Linux.

The official [archive extraction API](https://archive.r-lib.org/reference/archive_extract.html)
accepts a password. [CRAN](https://CRAN.R-project.org/package=archive) provides
Windows and macOS binaries, including Apple Silicon and Intel builds. It lists
libarchive as a system requirement for source installation. This is an R package
route with native dependencies. It is not a pure R implementation.

## Platform status

| Platform | Status |
| --- | --- |
| Windows x64 | Full local encrypted archive and wrong-password test passed. |
| macOS ARM64 and Intel | Binary availability verified. Actual extraction not tested. |
| Linux | Source installation may need libarchive development files and a compiler. Actual extraction not tested. |

The probe covers a non-interactive supplied password. The masked classroom
prompt needs an interactive RStudio check on each platform.

## Decision and remaining checks

Keep AES-256 ZIP with `archive` for extraction. Do not
silently fall back to another format or weaken encryption. Before classroom use,
test the same archive on macOS and Linux and decide how Linux dependencies are
provided. Do not require 7-Zip on student machines. The author-side packager
uses 7-Zip to create the ZIP; student extraction uses `archive`.

| Option if the package route fails | Benefit | Cost |
| --- | --- | --- |
| Official 7-Zip | AES-256 ZIP support; available across the target platforms. | A separate executable must be installed and checked. Password handling needs care. |
| System unzip | May already be installed. | AES support varies. A command named unzip does not prove compatibility. |
| Another R-readable encrypted format | Could make the R interface simpler. | Changes the agreed ZIP format and needs a new security and portability review. |
| Unencrypted files with a licence notice | Simplest installation. | A licence does not restrict access. Conflicts with the current distribution decision. |

These alternatives were considered during the investigation. None is selected.
Validate `archive` on the remaining platforms before classroom use.
