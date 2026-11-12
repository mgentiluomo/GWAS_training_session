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

## 2. Stage the verified main path again

The package must contain the checkpoint files that the final notebooks write,
including the summary statistics checkpoint of step 6.8. The old staging
folder `classroom-stage-2026.1` was made before step 6.8 existed, so make a
new one from a run of the final notebooks. A new destination is required: the
staging script refuses a folder that already exists.

```powershell
python -B scripts\author\stage_main_path.py `
  --run "C:\WEB_site\data_sources\codex_work\PATH_TO_VERIFIED_RUN" `
  --chain "C:\WEB_site\data_sources\codex_work\classroom-stage-2026.1\grch37_exercise\hg19ToHg38.over.chain.gz" `
  --destination "C:\WEB_site\data_sources\codex_work\classroom-stage-2026.1-final"
```

Replace `PATH_TO_VERIFIED_RUN` with the output folder of the last complete run
of modules 0 to 7. Look inside the new folder before you continue. It must
contain `array`, `checkpoints`, `final_report`, `grch37_exercise`,
`lab_export`, `pca_reference` and `phenotypes`, and nothing from `instructor`.

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
   encrypted, the password is given in class or on the course channel, and the
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
| `lessons/module_00_preparation.Rmd` (step 0.5 and the "55 files" remarks) | Use the file count printed by the new manifest. Tell students to run `download_course_data()` without `zip_path`. |
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
   Type the password at the masked prompt (this prompt has only been tested
   through automated runs so far, see `docs/open_issues.md`).
3. Run module 0 step 0.7 and check that it reports the expected file count.
4. Commit `config.R` and the text changes in separate, small commits, and push.

## 8. After the release

- Give the password to students in class or on the course channel only.
- Keep the throwaway test archives and the old staging folder outside the
  repository. They are not for students.
- The next academic year, build `data-2027.1` with a new password and delete this
  release.
