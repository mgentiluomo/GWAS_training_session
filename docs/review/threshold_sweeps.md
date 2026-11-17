# Threshold trials: counts at other settings

Written for the course author. Every trial starts from the same input as its step and changes one setting at a time. The course value is in bold and equals the count of the main path exactly (`step_counts.tsv`, the kept variants of step 3.4 and the hits and lambda of step 7.7). An alternative method has no course value. The numbers come from `scripts/author/threshold_sweeps.R`, run on `classroom-stage-2026.2` and a complete main-path run of the 2026.5 course on 18 November 2026. The 2026.4 numbers are in the history of this file.

## Step 3.1: Rough clean: variants (--geno)

Input: 2,013 samples and 296,510 variants.

| Setting | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 0.01 | 0 | 3,705 | 2,013 | 292,805 |
| 0.02 | 0 | 958 | 2,013 | 295,552 |
| 0.05 | 0 | 735 | 2,013 | 295,775 |
| **0.1 (course value)** | 0 | 150 | 2,013 | 296,360 |
| 0.2 | 0 | 130 | 2,013 | 296,380 |

## Step 3.1: Rough clean: samples (--mind)

Input: 2,016 samples and 296,510 variants.

| Setting | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 0.01 | 121 | 0 | 1,895 | 296,510 |
| 0.02 | 45 | 0 | 1,971 | 296,510 |
| 0.05 | 3 | 0 | 2,013 | 296,510 |
| **0.1 (course value)** | 3 | 0 | 2,013 | 296,510 |
| 0.2 | 3 | 0 | 2,013 | 296,510 |

## Step 3.2: Call rate of samples (--mind)

Input: 2,013 samples and 296,360 variants.

| Setting | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 0.01 | 118 | 0 | 1,895 | 296,360 |
| **0.02 (course value)** | 42 | 0 | 1,971 | 296,360 |
| 0.05 | 0 | 0 | 2,013 | 296,360 |
| 0.1 | 0 | 0 | 2,013 | 296,360 |
| 0.2 | 0 | 0 | 2,013 | 296,360 |

## Step 3.3: Sex check: female limit (max-female-xf)

Input: 1,971 samples and 296,360 variants.

| Setting | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 0.1 | 14 | 0 | 1,957 | 296,360 |
| **0.2 (course value)** | 8 | 0 | 1,963 | 296,360 |
| 0.3 | 8 | 0 | 1,963 | 296,360 |
| 0.4 | 8 | 0 | 1,963 | 296,360 |

## Step 3.3: Sex check: male limit (min-male-xf)

Input: 1,971 samples and 296,360 variants.

| Setting | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 0.6 | 8 | 0 | 1,963 | 296,360 |
| 0.7 | 8 | 0 | 1,963 | 296,360 |
| **0.8 (course value)** | 8 | 0 | 1,963 | 296,360 |
| 0.9 | 8 | 0 | 1,963 | 296,360 |

## Step 3.4: LD pruning: r2 limit (r2 limit)

Input: 1,963 samples and 125,061 variants.

| Setting | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 0.1 | 0 | 76,459 | 1,963 | 48,602 |
| **0.2 (course value)** | 0 | 56,261 | 1,963 | 68,800 |
| 0.5 | 0 | 24,308 | 1,963 | 100,753 |

## Step 3.4: LD pruning: window (window (kb))

Input: 1,963 samples and 125,061 variants.

| Setting | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 50 | 0 | 46,961 | 1,963 | 78,100 |
| **200 (course value)** | 0 | 56,261 | 1,963 | 68,800 |
| 1000 | 0 | 57,375 | 1,963 | 67,686 |

## Step 3.5: Heterozygosity (F cutoff (standard deviations))

Input: 1,963 samples and 296,360 variants.

| Setting | Samples removed | Variants removed | Samples remaining | Variants remaining | Samples flagged |
| --- | --- | --- | --- | --- | --- |
| 2 | 13 | 0 | 1,950 | 296,360 | 14 |
| 2.5 | 13 | 0 | 1,950 | 296,360 | 11 |
| **3 (course value)** | 13 | 0 | 1,950 | 296,360 | 8 |
| 3.5 | 13 | 0 | 1,950 | 296,360 | 5 |
| 4 | 13 | 0 | 1,950 | 296,360 | 0 |

## Step 3.6: Relatedness (KING kinship cutoff)

Input: 1,950 samples and 296,360 variants.

| Setting | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 0.0442 | 30 | 0 | 1,920 | 296,360 |
| 0.0884 | 30 | 0 | 1,920 | 296,360 |
| **0.177 (course value)** | 30 | 0 | 1,920 | 296,360 |
| 0.354 | 20 | 0 | 1,930 | 296,360 |

## Step 4.1: Call rate of variants (--geno)

Input: 1,844 samples and 296,360 variants.

| Setting | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 0.01 | 0 | 1,052 | 1,844 | 295,308 |
| **0.02 (course value)** | 0 | 801 | 1,844 | 295,559 |
| 0.05 | 0 | 560 | 1,844 | 295,800 |
| 0.1 | 0 | 0 | 1,844 | 296,360 |
| 0.2 | 0 | 0 | 1,844 | 296,360 |

## Step 4.2: Differential missingness (test-missing p-value cutoff)

Input: 1,844 samples and 295,559 variants.

| Setting | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 1e-03 | 0 | 126 | 1,844 | 295,433 |
| 1e-04 | 0 | 121 | 1,844 | 295,438 |
| **1e-05 (course value)** | 0 | 120 | 1,844 | 295,439 |
| 1e-06 | 0 | 106 | 1,844 | 295,453 |
| 1e-08 | 0 | 3 | 1,844 | 295,556 |

## Step 4.3: Allele frequency (--maf)

Input: 1,844 samples and 295,439 variants.

| Setting | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 0.001 | 0 | 33,941 | 1,844 | 261,498 |
| 0.005 | 0 | 47,187 | 1,844 | 248,252 |
| **0.01 (course value)** | 0 | 56,421 | 1,844 | 239,018 |
| 0.02 | 0 | 89,210 | 1,844 | 206,229 |
| 0.05 | 0 | 156,222 | 1,844 | 139,217 |

## Step 4.4: Hardy-Weinberg equilibrium (HWE p-value cutoff)

Input: 1,844 samples and 239,018 variants.

| Setting | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 1e-03 | 0 | 701 | 1,844 | 238,317 |
| 1e-04 | 0 | 274 | 1,844 | 238,744 |
| 1e-06 | 0 | 166 | 1,844 | 238,852 |
| 1e-08 | 0 | 149 | 1,844 | 238,869 |
| 1e-10 | 0 | 124 | 1,844 | 238,894 |
| **course rule (course value)** | 0 | 166 | 1,844 | 238,852 |

## Step 5.6: Ancestry outliers: robust Mahalanobis (alternative) (MCD chi-squared quantile)

Alternative method: no course value.

Input: 1,844 samples and 238,513 variants.

| Setting | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 0.99 | 86 | 0 | 1,758 | 238,513 |
| 0.999 | 39 | 0 | 1,805 | 238,513 |
| 0.9999 | 34 | 0 | 1,810 | 238,513 |

## Step 5.6: Ancestry outliers (SD limit)

Input: 1,844 samples and 238,513 variants.

| Setting | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 4 | 34 | 0 | 1,810 | 238,513 |
| 5 | 33 | 0 | 1,811 | 238,513 |
| **6 (course value)** | 33 | 0 | 1,811 | 238,513 |
| 7 | 33 | 0 | 1,811 | 238,513 |
| 8 | 33 | 0 | 1,811 | 238,513 |

## Step 5.7: Number of principal components (Number of PCs)

Input: 1,811 samples and 238,513 variants.

| Number of PCs | Hits below 5e-8 | Lambda |
| --- | --- | --- |
| 0 | 17 | 1.5273 |
| 1 | 8 | 1.0101 |
| 2 | 8 | 1.0136 |
| 3 | 8 | 1.0137 |
| 5 | 8 | 1.0150 |
| **10 (course value)** | 8 | 1.0157 |
| 15 | 8 | 1.0185 |
| 20 | 8 | 1.0183 |

## Notes

- Step 3.3: only the female limit changes the count (14 flagged at 0.1, 8 from 0.2 up). The male limit gives 8 from 0.6 to 0.9.
- Step 3.4: the trials count variants. "Removed" is the number pruned out and "remaining" is the number kept. The course value keeps 68,800 variants.
- Step 3.6: the relatedness trials use the call-rate rule of the 2026.5 course (the sample with the lower call rate is removed). The counts are the same as in 2026.4 (30, 30, 30 and 20).
- Step 4.4: with 922 controls the course rule equals the fixed cutoff 1e-6 (166 variants).
- Step 5.6: the 33 outliers are the same from 5 to 8 SD. The robust Mahalanobis distance is an alternative: 86, 39 and 34 samples at the 99%, 99.9% and 99.99% points.
- Step 5.7: the ten-PC trial gives the hits and lambda of the main path (8 and 1.0157).

## Sources (PLINK 2 documentation)

- Filters `--mind`, `--geno`, `--maf`, `--hwe`: https://www.cog-genomics.org/plink/2.0/filter . Read on 17 November 2026. The page does not state the order of the filters, so each trial uses one filter only.
- KING cutoffs, `--king-cutoff`, `--make-king-table`: https://www.cog-genomics.org/plink/2.0/distance . The degrees for 0.0884 and 0.0442 come from Manichaikul et al. 2010, doi:10.1093/bioinformatics/btq559 (verified, see `references_checked.md`).
- `--check-sex`, `--test-missing` and `--indep-pairwise` are used with the same options as the steps. The trials change one number.
