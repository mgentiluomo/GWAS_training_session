# PLINK 2 for the course package

This folder holds the pins and licence texts for the PLINK 2 programs that the course project package can include. It holds no program files. Programs and archives never enter Git.

## Status

The pins in `releases.tsv` are a **first pin, to be verified by the author against the official page**. They were measured on 15 November 2026 from the files that the official download address served on that day. A hash taken at the first download detects later changes. It does not prove that the first file was genuine. Compare each value with the publisher's own checksum or signature, if one exists, before the first release.

On 15 November 2026 the four archive hashes were confirmed by a second, independent download of the same files with a web browser. The values matched. This rules out a corrupted first download. It still does not replace a comparison with a publisher checksum.

The Windows x86_64 program was run with `--version` on Windows and printed `PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)`. The other three programs were not run, because they need their own operating systems.

## Files

| File | Content |
| --- | --- |
| `releases.tsv` | One row for each supported platform: official archive address, archive SHA-256 and size, the executable inside the archive with its SHA-256 and size, and the source tag and commit. |
| `COPYING` | GNU General Public License version 3, taken from the source tag. |
| `notices/` | Licence texts of the parts that PLINK 2 includes (LGPL, BSD, MIT and a QD library licence) and the Intel licence text that the Linux archive ships. |

## Builds

Four builds, all without AVX2 and without 32-bit support: Windows x86_64, macOS Apple Silicon, macOS Intel and Linux x86_64. The version is PLINK 2.0.0-b.1.4 (build 7 November 2026). The source is tag `v2.0.0-b.1.4`, commit `760ee7329e8914de52f75a4e470cecabccbde0d9`, of the PLINK 2 source repository.

## Licence

PLINK 2 is free software under the GNU General Public License version 3 or later. Anyone who receives the program may also receive the source. The course licence (CC BY-NC-SA 4.0 for text, MIT for code) does not apply to PLINK 2. Release notes must link the exact source tag and attach its source.

## Changing a pin

A pin changes only by a reviewed commit that edits `releases.tsv`. The packager never writes or accepts a new hash by itself.
