"""Convert Illumina Final Reports (one per sample) to PLINK .lgen/.map/.fam.

Usage:
    python final_report_to_lgen.py <final_report_dir> <sample_sheet.csv> <out_prefix> [gc_threshold]

- Uses the Plus-strand alleles ("Allele1 - Plus", "Allele2 - Plus").
- No calls ("-") and calls with GC Score below the threshold (default 0.15) become 0 0.
- Sex and case/control status come from the sample sheet (columns Sample_ID, Sex, Status).
Licence: MIT.
"""
import csv, glob, os, sys


def read_final_report(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip() == "[Data]":
                break
        reader = csv.DictReader(f, delimiter="\t")
        yield from reader


def main(fr_dir, sheet, out, gc_min=0.15):
    samples = {}
    with open(sheet, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sex = {"M": "1", "F": "2"}.get(row["Sex"], "0")
            status = {"control": "1", "case": "2"}.get(row["Status"], "-9")
            samples[row["Sample_ID"]] = (sex, status)

    variants = {}           # name -> (chr, pos), in first-seen order
    lgen_lines = []
    seen_samples = []
    for path in sorted(glob.glob(os.path.join(fr_dir, "FinalReport_S*.txt"))):
        for row in read_final_report(path):
            sid, snp = row["Sample ID"], row["SNP Name"]
            if sid not in seen_samples:
                seen_samples.append(sid)
            variants.setdefault(snp, (row["Chr"], row["Position"]))
            a1, a2 = row["Allele1 - Plus"], row["Allele2 - Plus"]
            if a1 == "-" or a2 == "-" or float(row["GC Score"]) < gc_min:
                a1, a2 = "0", "0"
            lgen_lines.append(f"{sid} {sid} {snp} {a1} {a2}")

    with open(out + ".lgen", "w", newline="\n") as f:
        f.write("\n".join(lgen_lines) + "\n")
    with open(out + ".map", "w", newline="\n") as f:
        f.writelines(f"{c}\t{n}\t0\t{p}\n" for n, (c, p) in variants.items())
    with open(out + ".fam", "w", newline="\n") as f:
        for sid in seen_samples:
            sex, status = samples.get(sid, ("0", "-9"))
            f.write(f"{sid} {sid} 0 0 {sex} {status}\n")
    print(f"{len(seen_samples)} samples, {len(variants)} variants -> {out}.lgen/.map/.fam")


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], a[3], float(a[4]) if len(a) > 4 else 0.15)
