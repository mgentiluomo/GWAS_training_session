# Trials of analysis changes (Part 3 of Riccardo's review)

Written for the course author. Nothing in the course or in the course data was changed. The trials ran in `C:\GWAS_trials`, on a copy of the project (branch `notebooks/all-modules`, commit 70316ae) and on the verified classroom data (108 files, all SHA-256 values match `MANIFEST.tsv`). Each trial runs the complete main path (`scripts/run_main_path.R`, R 4.5.2, PLINK 2.0.0-b.1.4, Windows 11) on 17 November 2026. In a trial, the course count checks print a note instead of stopping. The reference run (`base`) uses 20 components in the PCA of step 5.7 and gives exactly the 2026.3.3 numbers: the same `step_counts.tsv`, the same results table and lambda 1.01646459.

## Main table

Every trial changes one choice. The last row changes the three choices of 3a, 3b and 3c together. All trials keep ten PCs as covariates.

| Trial | What changes | Samples after 3.6 | Samples after 5.7 (variants) | Samples that change | Variance in the first 20 PCs | Lambda | Hits | Clumps |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base (2026.3.3) | Nothing | 1,920 | 1,811 (238,513) | none | 2.25% | 1.0165 | 8 | 3 |
| 3a | Riccardo's list of 18 long-range LD regions for the PCA | 1,920 | 1,811 (238,513) | none | 2.25% | 1.0171 | 8 | 3 |
| 3b | Relatives: remove the sample with the lower call rate | 1,920 | 1,811 (238,513) | 4 swapped at 3.6 | 2.25% | 1.0148 | 8 | 3 |
| 3c | Ancestry outliers: robust Mahalanobis distance (MCD) | 1,920 | 1,800 (238,513) | 11 more removed at 5.6 | 2.26% | 1.0160 | 8 | 3 |
| 3a + 3b + 3c | All three | 1,920 | 1,805 (238,513) | 4 swapped at 3.6, 6 more removed at 5.6 | 2.26% | 1.0142 | 8 | 3 |

In every trial the three lead variants of the clumps are the same: 9:96426973:A:G, 3:163224115:T:C and 12:120965921:G:A. The number of tests is 236,815 in all single trials, and 236,814 in the combined trial. The "variance in the first 20 PCs" is the sum of the 20 eigenvalues divided by the number of samples. This is an approximation of the share of the total variance, because the trace of the relationship matrix is about the number of samples.

## 3a. Long-range LD regions before the PCA

Files. `highLD_b38.bed` (18 regions, no `chr` prefix, four columns, the fourth is the source list) and `exclude_b38.txt` (the same regions with a `chr` prefix). The first file was used. It sits in the root of `C:\GWAS_course` and is not tracked by Git.

Coordinates. The file follows the BED convention, so the start is zero-based and the end is not included. The PLINK 2 modifier for this is `bed0`: `--exclude bed0 highLD_b38.bed`. The course file `s3-4_high_ld.bed1` is one-based and inclusive. The chromosome names of the file (`1`, `2`, and so on) match the chromosome names of the `.pvar` files (`1` to `22`). No array variant sits exactly at a zero-based start position, so a one-base mix-up would change nothing here.

Comparison of the two lists.

| | Course list | Riccardo's list |
| --- | --- | --- |
| Regions | 6 | 18 |
| In common (they overlap) | chr 2 (134 to 138 Mb), chr 6 (25 to 34 Mb), chr 8 (7 to 13 Mb), chr 17 (45 to 48 Mb) | the same four |
| Only in this list | chr 5 (44 to 51.5 Mb) and chr 11 (46 to 57 Mb) | 14 regions: chr 1, 2 (second region), 3 (two regions, and a third at 161.9 to 163.7 Mb), 5 (three regions at 98.6, 129.6 and 136.1 Mb), 6 (139.6 Mb), 8 (110.9 Mb), 11 (88.1 Mb), 12 (110.6 Mb), 14 and 20 |
| Array variants excluded (autosomal variants of state 3.3) | 5,716 | 9,500 |
| Variants kept by the pruning at 3.4 | 69,539 | 68,800 |
| Variants kept by the pruning at 5.7 | 68,622 | 67,897 |

Result. The retained cohort, the removed samples and the hits do not change. Lambda goes from 1.0165 to 1.0171. The 18 regions come from several published lists (Price et al. 2008 AJHG 83:132-135; Anderson et al. 2010 Nat Protoc 5:1564-1573; Privé et al. 2020 Bioinformatics 36:4449-4457; the repository GrindeLab/PCA, Grinde et al. 2019). Nine centromeric regions that cannot be converted from build 36 are missing from the file, as you noted. One region of the new list (chr 3, 161.9 to 163.7 Mb) holds the association signal rs1994750. It is only excluded from the PCA pruning, not from the association, so it causes no problem.

Recommendation. Use Riccardo's list in the course. It is longer, it is documented, and it costs nothing in this dataset. Keep the text about one-based and zero-based files, and use `bed0` for the new file. Then the numbers at 3.4 (69,539) and 5.7 (68,622) change to 68,800 and 67,897, so the expected results and the checkpoints of 3.4 must be updated in the same release.

## 3b. Relatives: keep the sample with the better call rate

The course keeps one person of each related pair and removes the one with the larger alphabetical identifier (`max(a, b)`). The trial removes the sample with the lower call rate, and uses the alphabetical rule only when two call rates are equal. The call rate comes from `--missing sample-only` on the cohort saved at 3.5.

- Both rules remove 30 samples (1,920 remain).
- Four samples change. Removed by the course rule but kept in the trial: SIM26_1088, SIM26_1291, SIM26_1329 and SIM26_1636. Removed in the trial but kept by the course rule: SIM26_0017, SIM26_0423, SIM26_0678 and SIM26_1264.
- This moves one variant at step 4.3 (239,018 instead of 239,019), because the allele frequencies depend on the samples. Lambda goes to 1.0148. Hits and clumps are the same.

Recommendation. Use the call-rate rule. It is easy to explain (keep the better data) and it does not depend on how the identifiers happen to be written. The numbers after 3.6 do not change, but the identifiers in the removal list do, and the checkpoints and the expected count at 4.3 (239,019) must be updated.

## 3c. Ancestry outliers: robust Mahalanobis distance

The course measures each study score on PC1 to PC4 against the mean and spread of the European reference, and removes samples more than six standard deviations away on any component. The trial adds a robust Mahalanobis distance: the centre and the covariance come from the Minimum Covariance Determinant (`MASS::cov.rob`, `method = "mcd"`) of the European reference scores. A sample is an outlier when its squared distance is above the 99.9% point of a chi-squared distribution with four degrees of freedom (18.47).

- The six-SD rule removes 33 samples at step 5.6. The Mahalanobis rule removes 44. The 33 are the same in both lists. The 11 extra samples are SIM26_0106, SIM26_0147, SIM26_0299, SIM26_0461, SIM26_1149, SIM26_1442, SIM26_1498, SIM26_1572, SIM26_1808, SIM26_1811 and SIM26_1879.
- In `C:\GWAS_trials\3c_outliers.png` the 33 samples that both rules remove form three small groups far from the European cluster (African, East Asian and South Asian ancestry). The 11 extra samples lie at the edge of the large European cluster. Their largest distance is only 2.3 to 4.3 SD on a single component.
- The cohort falls to 1,800 samples. Lambda is 1.0160. Hits and clumps are the same.

Recommendation. Keep the six-SD rule in the course for now. The 11 extra samples are not ancestry outliers. The European cluster of this dataset is not a Gaussian cloud, so the chi-squared cutoff is too tight. If the Mahalanobis distance is wanted, use it with a more careful cutoff and show the plot first.

## 3d. How many PCs?

The 20 eigenvalues of the retained cohort are 13.998, 1.426, 1.423, 1.422, 1.416, then values near 1.41 down to 1.396. PC1 holds 0.77% of the total variance. Every later PC holds about 0.078%. Only PC1 is associated with the disease (p = 1.1e-17). The p-values of PC2 to PC20 are between 0.17 and 0.81.

Criteria (explicit rules).

| Criterion | Rule | k |
| --- | --- | --- |
| Course | Ten PCs | 10 |
| Cumulative variance | Smallest k whose PCs hold at least 50% of the variance of the first 20 PCs | 6 |
| Scree elbow | The k after which the eigenvalue falls most (largest ratio to the next one) | 1 |
| Outcome | The highest PC with a p-value below 0.05 / 20 in a logistic regression of the disease on that PC | 1 |
| Reference | No PCs, or all 20 | 0 and 20 |

Association with k PCs (Age and sex are always in the model).

| k | Criterion | Tests | Hits | Lambda | Clumps |
| --- | --- | --- | --- | --- | --- |
| 0 | No PCs | 236,815 | 15 | 1.5464 | 3 |
| 1 | Elbow and outcome | 236,815 | 8 | 1.0121 | 3 |
| 6 | Cumulative variance | 236,815 | 8 | 1.0154 | 3 |
| 10 | Course | 236,815 | 8 | 1.0165 | 3 |
| 20 | All 20 | 236,815 | 8 | 1.0231 | 3 |

The same trial on the combined run (3a, 3b and 3c) gives the same picture: 17 hits and 4 clumps without PCs, then 8 hits and 3 clumps with 1, 6, 10 and 20 PCs, with lambda 1.5190, 1.0079, 1.0134, 1.0142 and 1.0185.

Recommendation. In this dataset one PC is enough: the elbow and the outcome rule agree. Ten PCs give almost the same result and keep lambda close to 1.0165, but PC2 to PC10 add only noise. Twenty PCs raise lambda a little (1.0231). For teaching, keep ten PCs and say that this is a common default. Add one sentence at step 5.7 that the scree plot shows that only PC1 stands out here. Do not change the course number of PCs without a new decision, because every later number depends on it.

## How the trials were run

- `C:\GWAS_trials\make_trial.py` builds each trial from `git archive` of the branch, patches the copy (and never the repository), and runs `scripts/run_main_path.R`. The tolerant overrides are in `C:\GWAS_trials\trial_prelude.R`.
- `C:\GWAS_trials\analyse_trials.py` reads the outputs. `C:\GWAS_trials\pc_criteria.R` runs 3d.
- The runs took 108 to 123 seconds each and ended with exit code 0.

## Update of 18 November 2026: what the 2026.5 course does

Decisions taken for the course branch `course/2026.5` (nothing is published):

- 3a, the long-range LD list: adopted in the main path (steps 3.4 and 5.7). The list is the file `highLD_b38.bed`, read with `bed0`. It is not in the repository. It travels with the course data in `pca_reference/highLD_b38.bed`. The repository GrindeLab/PCA has no declared licence, and the file comes from the review notes, so the decision is to keep it in the data release only. Its sources are Price et al. 2008, Anderson et al. 2010 and Privé et al. 2020 (DOIs verified in `references_checked.md`).
- 3b, the call-rate rule for relatives: adopted (step 3.6). The call rate comes from `--missing sample-only` on the cohort saved at 3.5.
- 3c, the robust Mahalanobis distance: kept as an alternative in a box of step 5.6. The main method stays at six standard deviations. A second alternative, the nearest 1000 Genomes group, is also in the box.
- 3d, the number of PCs: ten PCs stay in the main path. The box of step 5.7 explains the scree plot, the PCs associated with the outcome and lambda against the number of PCs.

Numbers of the main path with 3a and 3b together, on the new data (this replaces the 2026.4 numbers):

| Quantity | 2026.4 | 2026.5 |
| --- | --- | --- |
| Samples after 3.6 | 1,920 | 1,920 (4 samples swapped) |
| Variants after 4.3 | 239,019 | 239,018 |
| Variants after 4.4 | 238,852 | 238,852 (166 removed instead of 167) |
| Pruned sites at 3.4 | 69,539 | 68,800 |
| Shared sites with the reference (5.2) | 48,614 | 48,615 |
| Pruned sites at 5.7 | 68,622 | 67,905 |
| Final cohort | 1,811 samples (900 cases, 911 controls), 238,513 variants | 1,811 samples (898 cases, 913 controls), 238,513 variants |
| Finite tests | 236,815 | 236,820 |
| Hits, lambda, clumps (main) | 8, 1.0165, 3 | 8, 1.0157, 3 |
| Hits and lambda without PCs | 15, 1.546 | 17, 1.527 |
| Hits and lambda without QC and PCs | 19, 1.655 | 19, 1.655 |

The ancestry-outlier results on the new data: the six-SD rule and the nearest-group method remove the same 33 samples at step 5.6. The robust Mahalanobis distance removes 39 (6 more, at the edge of the European cluster, with squared distances between 18.8 and 24.6 against a cutoff of 18.47).
