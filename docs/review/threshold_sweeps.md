# Threshold trials: counts at other thresholds

Written for the course author. Every trial starts from the same input as its step and changes one threshold only. The course value is in bold and equals the count of the main path (`step_counts.tsv`) exactly. The numbers come from `scripts/author/threshold_sweeps.R`, run on the verified data and a complete main-path run on 17 November 2026.

## Step 3.1: Rough clean: variants (--geno)

Input: 2,013 samples and 296,510 variants.

| Threshold | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 0.01 | 0 | 3,705 | 2,013 | 292,805 |
| 0.02 | 0 | 958 | 2,013 | 295,552 |
| 0.05 | 0 | 735 | 2,013 | 295,775 |
| **0.1 (course value)** | 0 | 150 | 2,013 | 296,360 |
| 0.2 | 0 | 130 | 2,013 | 296,380 |

## Step 3.1: Rough clean: samples (--mind)

Input: 2,016 samples and 296,510 variants.

| Threshold | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 0.01 | 121 | 0 | 1,895 | 296,510 |
| 0.02 | 45 | 0 | 1,971 | 296,510 |
| 0.05 | 3 | 0 | 2,013 | 296,510 |
| **0.1 (course value)** | 3 | 0 | 2,013 | 296,510 |
| 0.2 | 3 | 0 | 2,013 | 296,510 |

## Step 3.2: Call rate of samples (--mind)

Input: 2,013 samples and 296,360 variants.

| Threshold | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 0.01 | 118 | 0 | 1,895 | 296,360 |
| **0.02 (course value)** | 42 | 0 | 1,971 | 296,360 |
| 0.05 | 0 | 0 | 2,013 | 296,360 |
| 0.1 | 0 | 0 | 2,013 | 296,360 |
| 0.2 | 0 | 0 | 2,013 | 296,360 |

## Step 3.5: Heterozygosity (F cutoff (standard deviations))

Input: 1,963 samples and 296,360 variants.

| Threshold | Samples removed | Variants removed | Samples remaining | Variants remaining | Samples flagged |
| --- | --- | --- | --- | --- | --- |
| 2 | 13 | 0 | 1,950 | 296,360 | 13 |
| 2.5 | 13 | 0 | 1,950 | 296,360 | 11 |
| **3 (course value)** | 13 | 0 | 1,950 | 296,360 | 8 |
| 3.5 | 13 | 0 | 1,950 | 296,360 | 5 |
| 4 | 13 | 0 | 1,950 | 296,360 | 0 |

## Step 3.6: Relatedness (KING kinship cutoff)

Input: 1,950 samples and 296,360 variants.

| Threshold | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 0.0442 | 30 | 0 | 1,920 | 296,360 |
| 0.0884 | 30 | 0 | 1,920 | 296,360 |
| **0.177 (course value)** | 30 | 0 | 1,920 | 296,360 |
| 0.354 | 20 | 0 | 1,930 | 296,360 |

## Step 4.1: Call rate of variants (--geno)

Input: 1,844 samples and 296,360 variants.

| Threshold | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 0.01 | 0 | 1,053 | 1,844 | 295,307 |
| **0.02 (course value)** | 0 | 801 | 1,844 | 295,559 |
| 0.05 | 0 | 561 | 1,844 | 295,799 |
| 0.1 | 0 | 0 | 1,844 | 296,360 |
| 0.2 | 0 | 0 | 1,844 | 296,360 |

## Step 4.3: Allele frequency (--maf)

Input: 1,844 samples and 295,439 variants.

| Threshold | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 0.001 | 0 | 33,951 | 1,844 | 261,488 |
| 0.005 | 0 | 47,184 | 1,844 | 248,255 |
| **0.01 (course value)** | 0 | 56,420 | 1,844 | 239,019 |
| 0.02 | 0 | 89,204 | 1,844 | 206,235 |
| 0.05 | 0 | 156,235 | 1,844 | 139,204 |

## Step 4.4: Hardy-Weinberg equilibrium (HWE p-value cutoff)

Input: 1,844 samples and 239,019 variants.

| Threshold | Samples removed | Variants removed | Samples remaining | Variants remaining |
| --- | --- | --- | --- | --- |
| 1e-03 | 0 | 700 | 1,844 | 238,319 |
| 1e-04 | 0 | 273 | 1,844 | 238,746 |
| 1e-06 | 0 | 167 | 1,844 | 238,852 |
| 1e-08 | 0 | 150 | 1,844 | 238,869 |
| 1e-10 | 0 | 127 | 1,844 | 238,892 |
| **course rule (course value)** | 0 | 167 | 1,844 | 238,852 |

## Sources (PLINK 2 documentation)

- Filters `--mind`, `--geno`, `--maf`, `--hwe`: https://www.cog-genomics.org/plink/2.0/filter . Read on 17 November 2026. `--mind` and `--geno` take the largest share of missing calls (the default for `--geno` is 0.1). `--maf` removes variants with a frequency below the value (default 0.01) and ignores non-founders by default when pedigree information is present. A dosage without a hard call counts as missing by default. The page does not state the order in which variant and sample filters are applied; it points to a separate order of operations page. Each trial here uses one filter only, so the order does not matter.
- KING cutoffs and `--king-cutoff`, `--make-king-table`, `--king-table-filter`: https://www.cog-genomics.org/plink/2.0/distance . The page gives 0.354 for repeats and identical twins and 0.177 for first-degree relatives. The degrees for 0.0884 (second degree) and 0.0442 (third degree) come from Manichaikul et al. 2010, doi:10.1093/bioinformatics/btq559, not from the PLINK page. Step 3.6 does not use `--king-cutoff`: it uses `--make-king-table --king-table-filter 0.0442` and an R rule.
- `--hwe`: the course does not use it. The cutoff of step 4.4 depends on the number of controls and is applied in R to the `--hardy midp` table. PLINK 2 `--hwe` can stop with an error when a cutoff is very strict for the sample size, unless a value `k` or `keep-fewhet` is given. PLINK 2 and PLINK 1.9 differ here, so the box only shows a fixed-cutoff terminal example.

## Notes

- Step 3.5: the F limit is a rule in R, not a PLINK option. The same 13 wells are removed at 2, 2.5, 3, 3.5 and 4 SD.
- Step 3.6: the cutoffs 0.0442, 0.0884 and 0.177 give the same 30 removals in this cohort. The trial uses the course rule with a changed relatives cutoff, so it is not the same as `--king-cutoff`.
- Step 4.4: with 920 controls the course rule equals the fixed cutoff 1e-6 (167 variants).
