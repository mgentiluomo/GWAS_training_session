# A short GWAS glossary

[Course home](../README.md)

| Term | Meaning in this course |
|---|---|
| Genotype | Observed alleles at a genomic position for one sample. |
| SNP | A single-nucleotide polymorphism. |
| FID / IID | The identifier pair used to match samples between files. |
| Phenotype | The outcome; here a binary case/control variable. |
| Covariate | An additional model predictor, such as age or a PC. |
| Call rate | Fraction of genotypes successfully called: one minus missingness. |
| MAF | Minor allele frequency in the samples used for the estimate. |
| LD | Linkage disequilibrium: association between alleles at different loci. |
| LD pruning | Selecting an approximately independent variant subset. |
| Heterozygosity | Two different alleles at a diploid locus. |
| HWE | Hardy–Weinberg equilibrium: a population-genetic expectation for genotype proportions. |
| Kinship | A measure of genetic relationship; KING's scale differs from PI_HAT. |
| PCA / PC | Principal component analysis / a component summarising genetic variation. |
| Population stratification | Genetic structure that can confound association when related to outcome. |
| A1 | The counted allele in the output; do not assume it is always minor. |
| OR | Odds ratio per additional copy of the tested allele in an additive model. |
| CI | Confidence interval expressing uncertainty under model assumptions. |
| p-value | Under the null model, probability of a statistic at least as extreme as observed. |
| Firth regression | Penalised logistic regression useful for some fitting/separation problems. |
| Manhattan plot | Genomic position against negative log10 association p-value. |
| QQ plot | Observed versus null-expected p-value quantiles. |
| Lambda GC | Summary of test-statistic inflation/deflation, not proof of a valid model. |
| Imputation | Estimating unobserved genotypes using observed data and a reference panel. |
| Replication | Testing an association in independent data. |
