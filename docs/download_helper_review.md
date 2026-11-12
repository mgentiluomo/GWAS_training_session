# Download rerun and command review, 12 November 2026

The helper now checks a saved manifest against the configured SHA-256 and
checks every expected file. A complete rerun needs no network access, password
or file chooser. Missing or changed data produce a diagnosis and an exact
recovery command. The classroom message reports 108 verified payload files.

New installations keep `data/course.MANIFEST.tsv` beside `data/course/`.
This does not add a file to the 108-file payload. A trusted `MANIFEST.tsv`
inside an existing folder can also be used. Older installations with no saved
manifest cannot be verified offline. They need one backup and reinstall with
`download_course_data(overwrite = TRUE)`.

Replacement data are downloaded and verified before any old data are moved.
The old folder and manifest receive a dated backup name. A numbered suffix
prevents a later backup from replacing an earlier one. The helper reports the
backup path. Failed download or verification leaves the old copy in place.

## Copyable command audit

Reviewed all 60 steps in modules 0 to 7. Also searched the three older demo
notebooks for editable placeholder paths and values.

| Location | Finding and action |
| --- | --- |
| Step 0.5 local ZIP command | Removed the `yourname` path from the main command block. The troubleshooting fallback now uses `download_course_data(zip_path = file.choose())`. |
| Steps 0.1 to 0.4 | Manual installation instructions. No copyable R commands. |
| Steps 0.6 to 0.8 and all steps in modules 1 to 7 | No placeholder path or value that students must replace before running the supplied R commands. No commands changed. |
| Plain PLINK terminal examples | Paths refer to the standard project layout. The Windows executable alternative remains documented. No placeholder data paths found. No commands changed. |
| Older demo notebooks | No copyable placeholder paths or mandatory placeholder values found. No commands changed. |
| Troubleshooting document | Replaced the local ZIP example that required `COURSE_WORK_DIR` with `file.choose()`. Updated rerun and backup guidance. |

The step 0.5 main command is now only `download_course_data()`. Package and
helper preparation appear under "You need". Local selection and backup recovery
appear under "If something goes wrong". Passwords are still entered through
the masked prompt. Tests use synthetic fixtures only.
