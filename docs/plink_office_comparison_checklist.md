# PLINK comparison (status)

Status: **the office confirmation is done and passed** on 16 November 2026. See `docs/review/plink_office_confirmation.md` and `docs/review/student_fields_review.md`. The current release is `project-2026.3.1`. Only the test on the Apple Silicon Mac (modules 3 and 5 to 7) is open.

## Apple Silicon check (your Mac)

1. Extract the release ZIP `GWAS_course-2026.3.1.zip`. Run step 0.6 (`prepare_course_plink()` must choose `macos-arm64` from the package) and the preflight. Record the hardware, macOS, R, PLINK version and executable hash.
2. Restore the verified 2.8 baseline into a fresh output folder with `restore_checkpoint`.
3. Run modules 3 and 5 to 7. Module 3 alone cannot test PCA, logistic regression or clumping.
4. Compare with the Windows run: counts exact, lambda equal to three decimals (1.016), same hits and clumps. Report every difference in p-values, PCs and plot inputs.
5. If `bin/plink2` is blocked, run `xattr -d com.apple.quarantine bin/plink2`. Note that you needed it.

If a count, lambda, hit or clump differs, stop and do not change an expected result. PLINK must then leave the package and a new project release is needed.

Test the provisioning and the preflight on Intel macOS and on Linux before you announce four-platform support.
