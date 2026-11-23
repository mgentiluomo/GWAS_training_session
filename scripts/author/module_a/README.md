# Module A author scripts

Author-side checks for module A (genotype imputation). Students never run these scripts. They read local
files that are not in the repository: the course data, the simulated build and the 1000 Genomes callset.
Every path is an argument. Run each script with `--help` for the details.

Run them with `python -I` (Python 3.10 or later, standard library only). They call PLINK 2 where needed.

| Script | What it does |
| --- | --- |
| `make_upload.py` | Writes one imputation input VCF per chromosome from a PLINK 2 state: REF set to the GRCh38 plus-strand allele of the array annotation, VCF 4.2, `chr` prefix, IID only, LF line ends, BGZF. |
| `check_vcf.py` | Checks such a VCF without bcftools: BGZF, header, sorting, genotypes, A/T and C/G sites, REF against the annotation and a reference `.pvar`. Exit code 1 on a failure. |
| `ld_compare.py` | Compares unphased r2 between nearby SNPs in the study and in reference samples of one superpopulation, on the same SNPs, by distance. |
| `panel_count.py` | Builds the reference panel sample list (callset minus donors minus related samples) and counts its variants by type and frequency in given regions. |
| `imp_summary.py` | Compares imputed dosages with true genotypes: median R2, median true r2, R2 below 0.3 and at least 0.8, correlation and bias, by frequency class, for SNVs and indels. |

Two traps that these scripts handle:

- PLINK 2 on Windows writes VCF lines with CRLF line ends. Imputation tools expect LF.
- The IDs of the 1000 Genomes `.pvar` are rsIDs or `.`, so they are not unique. Variants are matched by
  position, REF and ALT.

See `docs/review/night_2026-11-23.md` for how they were used.
