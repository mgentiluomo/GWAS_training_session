# Release checklist: data-2026.1

This checklist is for the course author. It creates the encrypted data release
`data-2026.1` on GitHub and connects it to the course. Nothing in it has been
done yet: the release does not exist, and the repository contains no password.

Work from `C:\GWAS_course` in Windows PowerShell. Take the steps in order and
stop at the first one that fails.

## 1. Before you start

1. Check that the branch is up to date and clean.

   ```powershell
   git status
   git log -3 --oneline
   ```

2. Run the text and export checks.

   ```powershell
   python -I -B scripts\check_text.py
   python -I -B scripts\tests\test_course_exports.py
   & "C:\Program Files\R\R-4.5.2\bin\Rscript.exe" scripts\check_course.R
   ```

3. Confirm that the student rehearsal finished with no fixes needed. The
   result is recorded in `docs/student_rehearsal.md`.
4. Choose the classroom password in your password manager. Use at least 16
   characters. Do not reuse the throwaway passwords of earlier tests. Keep it
   out of files, chat messages, shell history and screenshots.

## Password for the form

Set the classroom password only as the website deployment environment variable
`COURSE_DATA_PASSWORD`. Never put its value in a file, the repository or a page.
Use the same password for the encrypted classroom archive. The packaging tool
reads it separately at runtime through `COURSE_RELEASE_PASSWORD`, as shown below.

Update `COURSE_DATA_PASSWORD` every academic year together with the new data
release. Then test the form once with your own university address. Check that
the automatic email arrives and that its password opens the matching archive.

The form uses the placeholder path `/teaching/gwas/data-access` on
manuelgentiluomo.it. It sends the password automatically only to addresses ending
in `@unipi.it` or `@studenti.unipi.it`. The classroom QR code opens that same
form. Other users write to `manuel.gentiluomo@unipi.it`.

## 2. Verified final classroom staging

The final staging folder was created on 12 November 2026. It is ready for the
author to build the encrypted archive. No archive or release was created.

| Item | Verified value |
| --- | --- |
| Source commit | `1dac31bc7ea8ba6ebd8287dfc9198e27d6b1ce58` on `course/2026-guided-training`. |
| Complete run | `C:/WEB_site/data_sources/codex_work/main_path_release_20261112/` |
| Official student inputs | `C:/WEB_site/data_sources/sim2026/student/` |
| Run input copy | `C:/WEB_site/data_sources/codex_work/main_path_release_20261112/student_inputs/` |
| Official chain | `C:/WEB_site/data_sources/codex_work/classroom-stage-2026.1/grch37_exercise/hg19ToHg38.over.chain.gz` |
| Final staging folder | `C:/WEB_site/data_sources/codex_work/classroom-stage-2026.1-final/` |
| SHA-256 inventory | `C:/WEB_site/data_sources/codex_work/classroom-stage-2026.1-final.MANIFEST.tsv` |
| Files inside staging | **108**. The external inventory is not included in this count. |
| Total size inside staging | **656,298,229 bytes**. |

The following command created this folder. It is a record of the completed
operation. Do not run it again with the same destination. The script requires
a new folder and refuses an existing one.

```powershell
python -B scripts\author\stage_main_path.py `
  --run "C:\WEB_site\data_sources\codex_work\main_path_release_20261112" `
  --chain "C:\WEB_site\data_sources\codex_work\classroom-stage-2026.1\grch37_exercise\hg19ToHg38.over.chain.gz" `
  --destination "C:\WEB_site\data_sources\codex_work\classroom-stage-2026.1-final"
```

The staging folder contains `array`, `checkpoints`, `final_report`,
`grch37_exercise`, `lab_export`, `pca_reference` and `phenotypes`.
It also contains `README_simulated.txt`. It excludes instructor keys,
manufacturer manifests and imputation material. All 108 inventory hashes were
verified. Student input copies and the chain match their source hashes.

Modules 0 to 7 ran from the source commit above. Each module used a fresh
R 4.5.2 process on Windows. Every runnable notebook chunk passed. Chunks marked
`eval=FALSE` cover manual actions and were excluded. The input copy contains
the official student files and the official chain. Original inputs were unchanged.
PLINK identified itself as `PLINK v2.0.0-b.1.4 AVX2 (7 Nov 2026)`, matching
`config.R`. The course helper cleared unsupported inherited locale variables
for each R session. No system language settings changed.

All genotype-state and sample-removal counts agree with the external instructor
key and reference report. Notebook diagnostic counts also agree. Final results
are 1,811 samples (900 cases, 911 controls), 238,513 post-QC variants, 236,815
finite tests, 8 significant variants, lambda 1.016465 and 3 clumps. The two
comparison models have 15 and 19 significant variants. No analytical count
differences were found.

`scripts/tests/test_main_path_recovery.R` passed all seven restart targets
against the final staging folder and the new canonical run. Metadata matched
and PLINK reported zero genotype differences at each target. The 7.7 restart
included the 6.8 summary file. An additional independent restore at 7.1 verified
the completed 6.8 checkpoint. Its manifest hashes, 236,815 summary rows, eleven
columns, column dictionary and `beta = log(odds_ratio)` checks all passed.
No test or helper correction was needed.

Logs and verification scripts remain in the complete run folder:
`module_00.log` through `module_07.log`, `count_verification.log`, `recovery.log`
and `checkpoint68_verification.log`.

The final staging folder has 108 files. Module 0 step 0.5 and its recap use
`Course data are ready: 108 files verified.` as the expected download result.
The download step was a manual action and was not executed in this run.

## 3. Build the encrypted archive

The packager reads the password only from the environment variable
`COURSE_RELEASE_PASSWORD`. These commands ask for it without showing it and
remove it afterwards.

```powershell
$secure = Read-Host "Classroom password" -AsSecureString
$env:COURSE_RELEASE_PASSWORD = [System.Net.NetworkCredential]::new("", $secure).Password
python -B scripts\package_release.py `
  --source "C:\WEB_site\data_sources\codex_work\classroom-stage-2026.1-final" `
  --output "C:\WEB_site\data_sources\codex_work\release-data-2026.1"
Remove-Item Env:COURSE_RELEASE_PASSWORD
```

The script refuses an output folder that exists, a password shorter than 12
characters, and anything that looks like instructor material. It tests the
finished archive with 7-Zip before it writes the checksums.

The output folder contains three files to publish:

| File | Purpose |
| --- | --- |
| `course-data-2026.1.zip` | The AES-256 archive. |
| `MANIFEST.tsv` | Every file in the archive with its size and SHA-256. |
| `SHA256SUMS.txt` | The SHA-256 of the archive and of the manifest. |

The folder also holds `payload\` (an unencrypted copy of the files) and
`members.txt`. Do not upload those two.

Write down the two checksums printed by the script. They are also in
`SHA256SUMS.txt`: the first line is the archive, the second is the manifest.

## 4. Check the archive before publishing

1. Compare the checksums with an independent tool.

   ```powershell
   Get-FileHash "C:\WEB_site\data_sources\codex_work\release-data-2026.1\course-data-2026.1.zip" -Algorithm SHA256
   Get-FileHash "C:\WEB_site\data_sources\codex_work\release-data-2026.1\MANIFEST.tsv" -Algorithm SHA256
   ```

2. Test the download function on a scratch copy of the repository. Replace the
   four values with your own, and type the password when asked.

   ```r
   source("R/course.R")
   download_course_data(
     destination = "data/course_test",
     zip_path = "C:/WEB_site/data_sources/codex_work/release-data-2026.1/course-data-2026.1.zip",
     release = list(
       archive_url = "https://example.invalid/a", manifest_url = "https://example.invalid/m",
       archive_sha256 = "PASTE_ARCHIVE_SHA256", manifest_sha256 = "PASTE_MANIFEST_SHA256"))
   ```

   It must end with `Course data are ready` and the file count of the manifest.
   Test one wrong password as well: it must be refused.

## 5. Create the release on GitHub

The repository `mgentiluomo/GWAS_training_session` is public, so students can
download release files without signing in. There is no earlier release to
delete.

Use the web page:

1. Open <https://github.com/mgentiluomo/GWAS_training_session/releases/new>.
2. Click **Choose a tag**, type `data-2026.1` and choose **Create new tag**.
3. Set the target to the branch `course/2026-guided-training`.
4. Title: `Course data 2026.1`.
5. Description: one paragraph saying that the files are simulated, the archive is
   encrypted, students request the password through the university email form, and the
   SHA-256 values are in `config.R`. Do not write the password.
6. Drag in exactly three files: `course-data-2026.1.zip`, `MANIFEST.tsv` and
   `SHA256SUMS.txt`.
7. Leave **Set as a pre-release** and **Set as the latest release** as you prefer,
   then click **Publish release**.

Or use the GitHub command line from `C:\GWAS_course`. Write the description in a
file outside the repository first.

```powershell
gh release create data-2026.1 `
  "C:\WEB_site\data_sources\codex_work\release-data-2026.1\course-data-2026.1.zip" `
  "C:\WEB_site\data_sources\codex_work\release-data-2026.1\MANIFEST.tsv" `
  "C:\WEB_site\data_sources\codex_work\release-data-2026.1\SHA256SUMS.txt" `
  --repo mgentiluomo/GWAS_training_session `
  --target course/2026-guided-training `
  --title "Course data 2026.1" `
  --notes-file "C:\WEB_site\data_sources\codex_work\release-notes-2026.1.txt"
```

## 6. Update config.R

Open `config.R`. Replace the `data_release` block and its comment with:

```r
  # Classroom data release data-2026.1. Never store a password here.
  data_release = list(
    archive_url = "https://github.com/mgentiluomo/GWAS_training_session/releases/download/data-2026.1/course-data-2026.1.zip",
    manifest_url = "https://github.com/mgentiluomo/GWAS_training_session/releases/download/data-2026.1/MANIFEST.tsv",
    archive_sha256 = "FIRST LINE OF SHA256SUMS.TXT",
    manifest_sha256 = "SECOND LINE OF SHA256SUMS.TXT"
  ),
```

The four values are the only things that change in that file. Then update the
text that still says the release is not published:

| File | What to change |
| --- | --- |
| `README.md` (the "data release is not published yet" paragraph) | State that the data come from the release `data-2026.1`. |
| `docs/data.md` | Remove the remarks about the stage 1 test package. |
| `lessons/module_00_preparation.Rmd` (step 0.5 and the recap) | Confirm that the manifest and expected result both report 108 files. Tell students to run `download_course_data()` without `zip_path`. |
| `R/course.R` | The message about a local `zip_path` can stay. Check that nothing else refers to stage 1. |
| `scripts/tests/test_course_setup.R` | The test that uses the old 55-file archive needs the new local archive or must be skipped. |

Then regenerate the exports and run the checks again:

```powershell
python -B scripts\build_tutorial.py --export-steps site_content\steps
python -B scripts\build_tutorial.py --export-main-script scripts\run_main_path.R
python -I -B scripts\check_text.py
```

## 7. Check the published release from a clean folder

1. Clone the repository into an empty folder and switch to the branch
   `course/2026-guided-training`.
2. In R, run `source("scripts/preflight.R")` and then `download_course_data()`.
   Type the password at the masked prompt (checked by the author in RStudio on
   Windows on 12 November 2026; not yet tested on macOS or Linux, see
   `docs/open_issues.md`).
3. Run module 0 step 0.7 and check that it reports the expected file count.
4. Commit `config.R` and the text changes in separate, small commits, and push.

## 8. After the release

- Direct students to the university email form. In class, show a QR code for
  the same form. Never display or publish the password.
- Keep the throwaway test archives and the old staging folder outside the
  repository. They are not for students.
- The next academic year, build `data-2027.1` with a new password and delete this
  release.

## Website release stages

Label the website "beta 2026". Release modules 0 to 2 first, then 3 to 4,
then 5 to 7. Keep the repository and the data release complete at each stage.
