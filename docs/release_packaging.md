# Encrypted release packaging

Run `scripts/package_release.py` on the author machine. The hard rule protecting
`scripts/author/` takes precedence over the requested location in that directory.
The script reads only `sim2026/student/`. It creates a new `codex_work/release/`
directory. An existing destination is refused. It never uploads anything.

Supply the password through `COURSE_RELEASE_PASSWORD`. Never put a real password
in a command history, script, argument, notebook or report. The packager passes
it to 7-Zip through standard input. The child environment does not retain it.

The ZIP uses AES-256 for every payload member. `MANIFEST.tsv` sits beside the ZIP
and records each member's relative path, byte count and SHA-256. It is not inside
the ZIP. `SHA256SUMS.txt` records the encrypted ZIP checksum. Pin both the archive
and manifest checksums in the final course configuration before publication.
Hashes detect a changed download when compared with a trusted configuration.

Links, junctions, restricted path names and unrecognised top-level inputs are
refused. PLINK `.log` files are omitted because they contain author-machine paths
and hostnames. All other approved student files retain their original bytes.
No source files are modified. No instructor material is copied.

## Windows test package, 11 November 2026

This is a local encryption test, not a published release. Its password is a
throwaway value. It must not become the classroom release.

- Payload: 55 files, 416,075,409 bytes.
- Encrypted ZIP: 210,326,584 bytes (200.58 MiB).
- Build time: 14.767 seconds with 7-Zip 24.09 on Windows.
- Five packaging regression checks passed. The 36 existing generator checks passed.

The package includes the small GRCh37 exercise. Historical full-size `DB_A` and
`DB_1000G` inputs are absent from the authorised student folder and are not added.
The final array naming, data version and public distribution remain author decisions.
