# .lgen + .map + .fam: PLINK long format

**Produced by:** a script, from the Final Reports and the sample sheet.
**Type:** text, no header line, whitespace-separated.

The long format has the same shape as a Final Report (one line per sample per SNP), which is why it is the easiest bridge from a Final Report to PLINK.

## .lgen (genotypes)

| Column | Example | From the Final Report |
|---|---|---|
| 1 Family ID | `S01` | `Sample ID` (we use the same value as the individual ID) |
| 2 Individual ID | `S01` | `Sample ID` |
| 3 Variant ID | `1:1000123` | `SNP Name` |
| 4 Allele 1 | `A` | `Allele1 - Plus` |
| 5 Allele 2 | `G` | `Allele2 - Plus` |

A no call (`-`) becomes `0 0` (missing).

## .map (variants)

| Column | Example | Source |
|---|---|---|
| 1 Chromosome | `1` | `Chr` (Final Report or manifest) |
| 2 Variant ID | `1:1000123` | `SNP Name` |
| 3 Genetic distance (cM) | `0` | not available: `0` is accepted |
| 4 Base-pair position | `1000123` | `Position` |

## .fam (samples)

| Column | Example | Source |
|---|---|---|
| 1 Family ID | `S01` | sample sheet |
| 2 Individual ID | `S01` | sample sheet |
| 3 Father | `0` | `0` = not in the dataset |
| 4 Mother | `0` | `0` = not in the dataset |
| 5 Sex | `2` | sample sheet: `1` male, `2` female, `0` unknown |
| 6 Phenotype | `2` | sample sheet: `1` control, `2` case, `-9` missing |

## Next step

```
plink2 --lfile example --make-bed --out example
```
reads `example.lgen`, `example.map` and `example.fam` and writes `example.bed`, `example.bim`, `example.fam` (`07_plink_bed`).
