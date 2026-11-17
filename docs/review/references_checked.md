# References checked

Written for the course author. Every reference below was opened on 17 November 2026 before it was used. Method A means that the DOI resolves in the Crossref record (`api.crossref.org/works/<DOI>`) and that title, first author, journal, year and volume match the citation. Method B means that PubMed has the record (PMID) and the abstract supports the sentence in which the reference is used. No reference was written from memory.

| Reference | DOI | Used in | How it was verified |
| --- | --- | --- | --- |
| Price AL et al. 2008. Long-range LD can confound genome scans in admixed populations. Am J Hum Genet 83:132-135 | [10.1016/j.ajhg.2008.06.005](https://doi.org/10.1016/j.ajhg.2008.06.005) | Step 3.4 (long-range LD regions) | A: title, journal and year match |
| Anderson CA et al. 2010. Data quality control in genetic case-control association studies. Nat Protoc 5:1564-1573 | [10.1038/nprot.2010.116](https://doi.org/10.1038/nprot.2010.116) | Step 3.4, 3.x thresholds | A |
| Privé F et al. 2020. Efficient toolkit implementing best practices for principal component analysis of population genetic data. Bioinformatics 36:4449-4457 | [10.1093/bioinformatics/btaa520](https://doi.org/10.1093/bioinformatics/btaa520) | Steps 3.4, 5.6 | A. The abstract names LD structure captured by PCA, shrinkage of projected PCs and the detection of sample outliers |
| Price AL et al. 2006. Principal components analysis corrects for stratification in genome-wide association studies. Nat Genet 38:904-909 | [10.1038/ng1847](https://doi.org/10.1038/ng1847) | Step 5.6 (outlier rule in standard deviations) | A: title, journal and year match |
| Rousseeuw PJ, Van Driessen K 1999. A fast algorithm for the minimum covariance determinant estimator. Technometrics 41:212-223 | [10.1080/00401706.1999.10485670](https://doi.org/10.1080/00401706.1999.10485670) | Step 5.6 (robust Mahalanobis distance) | A |
| Privé F et al. 2022. Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort. Am J Hum Genet 109:12-23 | [10.1016/j.ajhg.2021.11.008](https://doi.org/10.1016/j.ajhg.2021.11.008) | Step 5.6 (assigning people to ancestry groups with a reference) | A and B (PMID 34995502). The abstract says that the nine ancestry groups are defined "based on a simple, robust, and effective method that we introduce here". The course only cites it for the idea of assigning people to a group from a reference |
| Patterson N, Price AL, Reich D 2006. Population structure and eigenanalysis. PLoS Genet 2:e190 | [10.1371/journal.pgen.0020190](https://doi.org/10.1371/journal.pgen.0020190) | Step 5.7 (Tracy-Widom test, mentioned only) | A |
| Wakefield J 2009. Bayes factors for genome-wide association studies: comparison with P-values. Genet Epidemiol 33:79-86 | [10.1002/gepi.20359](https://doi.org/10.1002/gepi.20359) | Step 7.6 (approximate Bayes factor) | A. The abstract describes an approximate Bayes factor for large samples with a prior on the effect size. Crossref lists the online date as 2008 and the volume as 2009 |
| Maller JB et al. 2012. Bayesian refinement of association signals for 14 loci in 3 common diseases. Nat Genet 44:1294-1301 | [10.1038/ng.2435](https://doi.org/10.1038/ng.2435) | Step 7.6 (credible sets) | A |
| Wang G et al. 2020. A simple new approach to variable selection in regression, with application to genetic fine mapping. J R Stat Soc B 82:1273-1300 | [10.1111/rssb.12388](https://doi.org/10.1111/rssb.12388) | Step 7.6 (SuSiE, mentioned only) | A |
| Manichaikul A et al. 2010. Robust relationship inference in genome-wide association studies. Bioinformatics 26:2867-2873 | [10.1093/bioinformatics/btq559](https://doi.org/10.1093/bioinformatics/btq559) | Step 3.6 (KING cutoffs and relationship degrees) | A |

## Not used, because not verified

- Grinde KE et al. 2019 (repository GrindeLab/PCA). It was named in the review notes without a DOI. The repository has no declared licence, and no DOI could be checked, so it is not cited in the course. The long-range LD list in the course data comes from the file `highLD_b38.bed` supplied for the review. Its coordinates are factual and its sources are Price 2008, Anderson 2010 and Privé 2020, which are verified above.

## Software pages read

- PLINK 2 filters, https://www.cog-genomics.org/plink/2.0/filter, for `--mind`, `--geno`, `--maf` and `--hwe`. Read on 17 November 2026.
- PLINK 2 distance, https://www.cog-genomics.org/plink/2.0/distance, for `--king-cutoff`, `--make-king-table` and `--king-table-filter`. Read on 17 November 2026.
- Oxford Nanopore Dorado documentation 1.2.0, PacBio file formats 12.0 and the CRAM v3 specification, for step 1.9. Read on 17 November 2026.
