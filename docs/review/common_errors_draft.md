# Common errors and how to fix them, draft

Written for students, in the course style. This page is a draft. It is not linked from the menu and not in the site. Each entry has the message, the cause and the fix. Only errors that happened in this course, or that the course tests reproduce, are listed.

## 1. `could not find function "region_leads"`

(The same message appears for `guided_variant_labels`, `threshold_counts`, `plot_threshold_trials` and other course functions.)

- **Message.** `Error in region_leads(...) : could not find function "region_leads"`.
- **Cause.** Your project is older than the page. The page shows code of a newer project, and the new functions are not in your copy of the course files. A student with project 2026.3.3 met this at steps 7.6 and 7.7.
- **Fix.** Run these two lines in the console.

  ```r
  source("R/guided.R")
  cfg <- guided_init()
  ```

  Read the line `Project version: ...`. If it is older than the version at the top of the page, or if it prints nothing, download the new project at step 0.3. Unzip it in a new folder. Copy your `data/` and `results/` folders into it if you want to keep your work.

## 2. `This step needs project version 2026.5 or later. Your project is ...`

- **Message.** The text is the message itself.
- **Cause.** The step uses functions that your project does not have. The check stops the step before a less clear error appears.
- **Fix.** Download the new version at step 0.3, as the message says.

## 3. PLINK 2 not found

- **Message.** `PLINK 2 not found` or `plink2.exe` is not recognised.
- **Cause.** The program is not in the `bin/` folder of the project, or you downloaded PLINK 1.9 or a ZIP file that you did not unpack.
- **Fix.** Unpack the PLINK 2 ZIP and move `plink2.exe` (on Mac and Linux, `plink2`) into `bin/`. Run the setup check again with `source("scripts/preflight.R")`.

## 4. The password is wrong

- **Message.** `Incorrect passphrase` or a similar line when the data are unpacked.
- **Cause.** A typing error, or the password of an earlier year.
- **Fix.** Type the password again and check the capital letters. Request it again at the data access form if you lost it. Never paste the password in a screenshot or a shared file.

## 5. The download fails the SHA-256 check

- **Message.** The helper says that a checksum does not match.
- **Cause.** The file is incomplete or changed, often after a lost connection.
- **Fix.** Download it again. Do not replace the expected value with the hash of the bad file.

## 6. Accented text or strange characters in a path

- **Message.** Warnings about `C.UTF-8`, or a file that cannot be found when the folder name has letters such as `à`, `è` or `ü`.
- **Cause.** Windows R can ask for a locale that Windows does not have.
- **Fix.** Run `source("scripts/preflight.R")`. It repairs the locale for the current R session. The test of the night run (see the report `night_2026-11-18.md`) used a project folder with spaces and accented letters, to check that the course still runs.

## 7. Decimal comma

- **Message.** `expected decimal points` or a table with the wrong number of columns.
- **Cause.** A spreadsheet program saved a file with a comma as the decimal mark and a semicolon as the separator.
- **Fix.** Use the files supplied by the course without opening and saving them in a spreadsheet.

## 8. A later step fails after an earlier step failed

- **Message.** A file is missing, or a count does not match.
- **Cause.** An earlier command stopped and you ran the next one anyway.
- **Fix.** Go back to the first error. Read the first message, not the last. If you lost the files of a module, restart from the checkpoint that the module names in its first step.

## Notes for the author

- Entry 6 is a placeholder until the full run in a path with spaces and accents ends (task B2). I will complete it with the result.
- The messages in entries 1 and 2 are exact. The others are the usual wording and should be checked on a real run before the page is published.
