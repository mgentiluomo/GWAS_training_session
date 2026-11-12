# AES-256 extraction investigation

## Evidence

On 11 November 2026, R 4.5.2 on Windows 11 extracted the stage 1 AES-256 ZIP
using `archive` 1.1.14. All 55 payload SHA-256 checks passed. A wrong password
was rejected. Extraction and verification took 5.0 seconds. `digest` 0.6.39
provided hashing. All investigation packages were installed under `codex_work/`.
No system library or repository data directory was populated.

On 12 November 2026, the author tested the same stage 1 archive on Ubuntu
24.04.4 LTS with R 4.6.1. Extraction passed all 55 payload SHA-256 checks and
rejected a wrong password in 7.78 seconds. This result was reported by the
author, rather than reproduced on the Windows development machine.

CRAN source installation failed without `libarchive-dev` for `archive` and
`libuv1-dev` for `fs`, a dependency needed by `rmarkdown`. Only the runtime
library `libarchive.so.13` was present. All packages then installed as binaries
from `https://packagemanager.posit.co/cran/__linux__/noble/latest`, without a
compiler or administrator rights. The following R option was essential;
without it the server returned source packages:

```r
options(HTTPUserAgent = sprintf("R/%s R (%s)", getRversion(),
  paste(getRversion(), R.version["platform"], R.version["arch"], R.version["os"])))
```

The [Posit Package Manager documentation](https://docs.posit.co/rspm/admin/serving-binaries.html)
explains how distribution-specific URLs and the R user agent select binaries.

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
| Ubuntu 24.04.4 LTS, R 4.6.1 | Author-reported binary installation and extraction passed: 55 SHA-256 checks, wrong password rejected, 7.78 seconds. Other Linux distributions remain untested. |

The probe covers a non-interactive supplied password. The masked classroom
prompt needs an interactive RStudio check on each platform.

## Decision and remaining checks

Keep AES-256 ZIP with `archive` for extraction. Do not
silently fall back to another format or weaken encryption. Before classroom use,
test the same archive on macOS and the masked RStudio prompt on each platform.
Use matching Posit Package Manager binaries on supported Linux distributions;
source installation needs development packages and a compiler. Do not require
7-Zip on student machines. The author-side packager
uses 7-Zip to create the ZIP; student extraction uses `archive`.

| Option if the package route fails | Benefit | Cost |
| --- | --- | --- |
| Official 7-Zip | AES-256 ZIP support; available across the target platforms. | A separate executable must be installed and checked. Password handling needs care. |
| System unzip | May already be installed. | AES support varies. A command named unzip does not prove compatibility. |
| Another R-readable encrypted format | Could make the R interface simpler. | Changes the agreed ZIP format and needs a new security and portability review. |
| Unencrypted files with a licence notice | Simplest installation. | A licence does not restrict access. Conflicts with the current distribution decision. |

These alternatives were considered during the investigation. None is selected.
Validate `archive` on the remaining platforms before classroom use.
