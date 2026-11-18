"""Extract the protein-coding genes near the three regional plots of step 7.6 from a GENCODE GTF.

Author tool. The large GTF is read from a path on this machine. It is never copied to the repository or to the
course data. Only the small extract is kept (columns chr, start, end, gene_name, strand), and the course data carries it
as annotation/genes_gencode_v50_regions.tsv. The windows are the 1 Mb regions of step 7.6 (lead variant plus and minus
500,000 bases) with 50,000 bases more on each side.

Usage:
    python scripts/author/extract_region_genes.py GTF.gz OUTPUT_FOLDER --release 50 --ensembl 116
"""
import argparse
import gzip
import hashlib
import re
from pathlib import Path

REGIONS = (("3", 163224115), ("9", 96426973), ("12", 120965921))
HALF_WINDOW = 500_000
EXTRA = 50_000
NAME = re.compile(r'gene_name "([^"]+)"')
TYPE = re.compile(r'gene_type "([^"]+)"')


def extract(gtf: Path) -> list[tuple[str, int, int, str, str]]:
    rows = []
    with gzip.open(gtf, "rt", encoding="utf-8") as stream:
        for line in stream:
            if line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 9 or fields[2] != "gene":
                continue
            chrom = fields[0][3:] if fields[0].startswith("chr") else fields[0]
            start, end, strand = int(fields[3]), int(fields[4]), fields[6]
            kind, name = TYPE.search(fields[8]), NAME.search(fields[8])
            if not kind or kind.group(1) != "protein_coding" or not name:
                continue
            for region_chrom, position in REGIONS:
                low, high = position - HALF_WINDOW - EXTRA, position + HALF_WINDOW + EXTRA
                if chrom == region_chrom and end >= low and start <= high:
                    rows.append((chrom, start, end, name.group(1), strand))
                    break
    order = {chrom: index for index, (chrom, _) in enumerate(REGIONS)}
    return sorted(set(rows), key=lambda row: (order[row[0]], row[1], row[2], row[3]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("gtf", type=Path)
    parser.add_argument("destination", type=Path, help="Folder that will hold the annotation files.")
    parser.add_argument("--release", required=True, help="GENCODE human release number, for example 50.")
    parser.add_argument("--ensembl", required=True, help="Ensembl version named in the GTF header, for example 116.")
    args = parser.parse_args()
    rows = extract(args.gtf)
    args.destination.mkdir(parents=True, exist_ok=True)
    table = args.destination / f"genes_gencode_v{args.release}_regions.tsv"
    table.write_text("chr\tstart\tend\tgene_name\tstrand\n" + "".join("\t".join(map(str, row)) + "\n" for row in rows),
                     encoding="utf-8", newline="\n")
    digest = hashlib.sha256(args.gtf.read_bytes()).hexdigest()
    readme = args.destination / "README_genes.txt"
    readme.write_text(
        f"Protein-coding genes near the three regional plots of step 7.6 (GRCh38).\n"
        f"Source: GENCODE human release {args.release} (Ensembl {args.ensembl}), basic gene annotation, file\n"
        f"gencode.v{args.release}.basic.annotation.gtf.gz, https://www.gencodegenes.org/human/ .\n"
        f"SHA-256 of the GTF that was read: {digest}\n"
        f"Windows: lead variant plus and minus {HALF_WINDOW:,} bases, with {EXTRA:,} bases more on each side.\n"
        f"Columns: chr, start, end (1-based, both included), gene_name, strand.\n"
        f"Gene positions are real. The association signals of the course are simulated, so these genes are not causal.\n"
        f"UCSC Genome Browser, GENCODE track: \"GENCODE data are available for use without restrictions.\"\n",
        encoding="utf-8", newline="\n")
    for chrom, position in REGIONS:
        print(chrom, position, sum(1 for row in rows if row[0] == chrom))
    print("wrote", table, "and", readme)


if __name__ == "__main__":
    main()
