# Screenshot capture list

Eight views, each captured on Windows and macOS. No screenshots have been taken.
Save the 16 planned PNG files under `Figures/screenshots/`. The names below are
reserved. Notebook comments hold the paths, platforms, placement and draft alt
text. Exported assets stay `null` until the corresponding file exists.

Capture real software windows. Do not generate or draw replacement screenshots.
Record the operating system, RStudio version and capture date when reviewing a
capture. Installer labels can change. Match the visible labels to the current
lesson before adding the file. Keep text legible at the website's normal width.
Use pane labels and a short caption rather than colour alone to explain a target.

For every capture, hide personal user names in paths, email addresses, account
avatars, browser profiles, notifications and unrelated windows. Passwords must
never appear, including in console history. Capture the password dialog empty.
Prefer a clean demonstration account and neutral folder names. Crop or redact
personal details before saving the PNG in the repository. Check the final PNG,
not only the window, for private information. Keep relevant error text readable.

| Step | System | File name | Must be visible | Must be hidden, in addition to the common rules | Draft alt text |
| --- | --- | --- | --- | --- | --- |
| 0.1 | Windows | `s0-1_r_download_windows.png` | The CRAN download area and the next Windows installer link, including the base link if present. | Browser profile, account avatar, bookmarks, downloads list and any personal path. | CRAN page showing the Windows R download link. |
| 0.1 | macOS | `s0-1_r_download_macos.png` | The macOS R download area with the Apple Silicon and Intel package labels visible. | Browser profile, account avatar, bookmarks, downloads list and any personal path. | CRAN page showing the Apple Silicon and Intel R installer choices. |
| 0.2 | Windows | `s0-2_rstudio_console_windows.png` | The RStudio window, the Console tab and its empty > prompt. Keep the pane labels visible. | Recent projects, user name in window titles, console startup paths and Environment contents. | RStudio on Windows with the Console tab selected and an empty R prompt. |
| 0.2 | macOS | `s0-2_rstudio_console_macos.png` | The RStudio window, the Console tab and its empty > prompt. Keep the pane labels visible. | Recent projects, user name in window titles, console startup paths and Environment contents. | RStudio on macOS with the Console tab selected and an empty R prompt. |
| 0.6 | Windows | `s0-6_plink_executable_windows.png` | File Explorer showing the extracted plink2.exe in the project bin folder. Show file extensions and the folder breadcrumb. | Home folder name, sidebar favourites, unrelated files and the personal part of the address bar. | Windows File Explorer showing plink2.exe extracted into the course bin folder. |
| 0.6 | macOS | `s0-6_plink_executable_macos.png` | Finder showing the extracted plink2 executable in the project bin folder. Show its name and the folder location. | Home folder name, sidebar favourites, unrelated files and the personal part of the address bar. | macOS Finder showing plink2 extracted into the course bin folder. |
| 0.7 | Windows | `s0-7_password_prompt_windows.png` | The empty getPass password dialog and its Course data password label. Show enough RStudio context to identify the prompt. | Every password value, even masked entries, email, inbox, autofill, password manager and personal paths. | Empty masked course password prompt opened from RStudio on Windows. |
| 0.7 | macOS | `s0-7_password_prompt_macos.png` | The empty getPass password dialog and its Course data password label. Show enough RStudio context to identify the prompt. | Every password value, even masked entries, email, inbox, autofill, password manager and personal paths. | Empty masked course password prompt opened from RStudio on macOS. |
| 0.7 | Windows | `s0-7_incomplete_data_error_windows.png` | The Console error naming a missing manifest or file, and the exact recovery command with overwrite = TRUE. Use a disposable demonstration copy. | Personal path segments, unrelated console history and all passwords or email addresses. | RStudio Console on Windows showing an incomplete-data error and its backup recovery command. |
| 0.7 | macOS | `s0-7_incomplete_data_error_macos.png` | The Console error naming a missing manifest or file, and the exact recovery command with overwrite = TRUE. Use a disposable demonstration copy. | Personal path segments, unrelated console history and all passwords or email addresses. | RStudio Console on macOS showing an incomplete-data error and its backup recovery command. |
| 0.4 | Windows | `s0-4_project_panes_windows.png` | The project name GWAS_course, Files pane with config.R and lessons, the module 0 Source tab and the Console. Show pane labels together. | Personal project paths, recent files, Environment contents, History entries and unrelated Source tabs. | Course project open in RStudio on Windows, with the lesson in Source beside Console and Files. |
| 0.4 | macOS | `s0-4_project_panes_macos.png` | The project name GWAS_course, Files pane with config.R and lessons, the module 0 Source tab and the Console. Show pane labels together. | Personal project paths, recent files, Environment contents, History entries and unrelated Source tabs. | Course project open in RStudio on macOS, with the lesson in Source beside Console and Files. |
| 0.8 | Windows | `s0-8_preflight_success_windows.png` | The end of the Console output with Preflight passed, the PLINK version and the returned > prompt. Keep the Console tab visible. | User name in report paths, unrelated console history, email addresses and machine identifiers. | Successful Windows setup check in RStudio, with Preflight passed and the R prompt visible. |
| 0.8 | macOS | `s0-8_preflight_success_macos.png` | The end of the Console output with Preflight passed, the PLINK version and the returned > prompt. Keep the Console tab visible. | User name in report paths, unrelated console history, email addresses and machine identifiers. | Successful macOS setup check in RStudio, with Preflight passed and the R prompt visible. |
| 5.5 | Windows | `s5-5_saved_plot_preview_windows.png` | The Files pane entry s5-5_reference_projection.png and its opened image preview. Show axes and legend. Use the preview location of the captured RStudio version. | Personal paths, unrelated files or windows, email addresses and any individual sample labels. | Saved reference PCA image opened from RStudio Files on Windows, showing labelled axes and reference groups. |
| 5.5 | macOS | `s5-5_saved_plot_preview_macos.png` | The Files pane entry s5-5_reference_projection.png and its opened image preview. Show axes and legend. Use the preview location of the captured RStudio version. | Personal paths, unrelated files or windows, email addresses and any individual sample labels. | Saved reference PCA image opened from RStudio Files on macOS, showing labelled axes and reference groups. |

Do not damage a student's data to capture the incomplete-data error. Use a
disposable demonstration copy and show the real helper message. Do not run the
recovery command merely to make a screenshot.

Step 0.4 covers the first Source and Files views together. Step 5.5 covers the
first saved analytical image preview. The plot is written to a PNG file, so do
not imply that it automatically appears in the Plots pane. A preview may open
in a separate window in some RStudio versions.

No extra captures are planned for Next buttons, simple calculations, repeated
Console output or every possible error. The text already explains these cases.
