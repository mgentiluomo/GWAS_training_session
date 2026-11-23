"""Build imputation input VCFs (one per chromosome) from a course PLINK 2 state.

Author side only. Used for module A (genotype imputation).

Steps for each chromosome:
1. Write a REF list: variant ID -> GRCh38 plus-strand allele (Ref_Plus) of the array annotation, matched by
   chromosome and position.
2. PLINK 2 export: --ref-allele with that list, VCF 4.2, bgzip, chromosome names with the chr prefix, sample
   ID = IID only. Optional --keep to restrict the samples.
3. PLINK 2 on Windows ends lines with CRLF. The file is rewritten with LF and compressed again as BGZF.
4. PLINK marks every REF as provisional (INFO flag PR) when the .pvar has no INFO column, and --ref-allele
   does not clear the flag when no allele changes. The flag is removed only after checking that every REF
   equals the GRCh38 Ref_Plus.

Example:
    python -I make_upload.py --state <prefix of .pgen/.pvar/.psam> --annotation <array annotation .tsv>
        --plink <plink2 executable> --out <output folder> --chromosomes 9 22
"""

from __future__ import annotations

import argparse
import gzip
import struct
import subprocess
import sys
import zlib
from pathlib import Path

EOF_BLOCK = bytes.fromhex("1f8b08040000000000ff0600424302001b0003000000000000000000")


def bgzf_write(path: Path, payload: bytes, level: int = 6) -> None:
    """Write `payload` as BGZF: gzip members of at most 65,280 input bytes with the BC extra field, then EOF."""
    with open(path, "wb") as f:
        for i in range(0, len(payload), 65280):
            chunk = payload[i:i + 65280]
            c = zlib.compressobj(level, zlib.DEFLATED, -15)
            deflated = c.compress(chunk) + c.flush()
            bsize = 12 + 6 + len(deflated) + 8
            f.write(b"\x1f\x8b\x08\x04\x00\x00\x00\x00\x00\xff\x06\x00BC\x02\x00")
            f.write(struct.pack("<H", bsize - 1))
            f.write(deflated)
            f.write(struct.pack("<II", zlib.crc32(chunk) & 0xFFFFFFFF, len(chunk)))
        f.write(EOF_BLOCK)


def ref_list(state: str, annotation: Path, chromosomes: list[str], out: Path) -> dict[str, str]:
    """Write `out` (ID <tab> REF) for the variants of `state` on `chromosomes`; return the same mapping."""
    ref_by_pos: dict[tuple[str, str], set[str]] = {}
    with open(annotation, encoding="utf-8") as f:
        head = f.readline().rstrip("\n").split("\t")
        ci, pi, ri = head.index("Chr"), head.index("Position_GRCh38"), head.index("Ref_Plus")
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[ci] in chromosomes:
                ref_by_pos.setdefault((p[ci], p[pi]), set()).add(p[ri])
    refs: dict[str, str] = {}
    with open(state + ".pvar", encoding="utf-8") as f, open(out, "w", encoding="utf-8", newline="\n") as w:
        for line in f:
            if line.startswith("#"):
                continue
            chrom, pos, vid = line.split("\t")[:3]
            got = ref_by_pos.get((chrom, pos))
            if got and len(got) == 1:
                refs[vid] = next(iter(got))
                w.write(f"{vid}\t{refs[vid]}\n")
    return refs


def clean_vcf(raw: bytes, refs: dict[str, str]) -> tuple[bytes, int]:
    """CRLF -> LF; drop the PR header and flag after checking every REF against `refs`."""
    lf = raw.replace(b"\r\n", b"\n")
    if b"\r" in lf:
        raise ValueError("a carriage return is left after the CRLF rewrite")
    kept, n = [], 0
    for line in lf.split(b"\n"):
        if line.startswith(b"##INFO=<ID=PR,"):
            continue
        if line and not line.startswith(b"#"):
            p = line.split(b"\t", 9)
            vid, ref = p[2].decode(), p[3].decode()
            if refs.get(vid) != ref:
                raise ValueError(f"REF of {vid} is {ref}, the annotation says {refs.get(vid)}")
            if p[7] in (b"PR", b"."):
                p[7] = b"."
            else:
                p[7] = b";".join(x for x in p[7].split(b";") if x != b"PR") or b"."
            line = b"\t".join(p)
            n += 1
        kept.append(line)
    return b"\n".join(kept), n


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--state", required=True, help="PLINK 2 fileset prefix (.pgen/.pvar/.psam)")
    ap.add_argument("--annotation", required=True, type=Path, help="array annotation with Chr, Position_GRCh38, Ref_Plus")
    ap.add_argument("--plink", required=True, help="PLINK 2 executable")
    ap.add_argument("--out", required=True, type=Path, help="output folder for chr<N>.vcf.gz")
    ap.add_argument("--chromosomes", nargs="+", default=["9", "22"])
    ap.add_argument("--keep", help="optional PLINK --keep file")
    ap.add_argument("--extract-range", help="optional PLINK --extract range file (bed1)")
    ap.add_argument("--exclude", help="optional PLINK --exclude ID list")
    ap.add_argument("--suffix", default="", help="text added to the output names, for example _masked")
    a = ap.parse_args(argv)

    a.out.mkdir(parents=True, exist_ok=True)
    side = a.out.parent / f"make_upload{a.suffix}"
    side.mkdir(exist_ok=True)
    refs = ref_list(a.state, a.annotation, a.chromosomes, side / "ref_alleles_grch38.tsv")
    print(f"REF list rows: {len(refs)}")
    for chrom in a.chromosomes:
        prefix = a.out / f"chr{chrom}{a.suffix}"
        cmd = [a.plink, "--pfile", a.state, "--chr", chrom, "--ref-allele", str(side / "ref_alleles_grch38.tsv"),
               "2", "1", "--output-chr", "chrM", "--export", "vcf-4.2", "bgz", "id-paste=iid", "--threads", "2",
               "--out", str(prefix)]
        for flag, value in (("--keep", a.keep), ("--extract", a.extract_range), ("--exclude", a.exclude)):
            if value:
                cmd[3:3] = [flag] + (["bed1", value] if flag == "--extract" else [value])
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            sys.stderr.write(r.stdout + r.stderr)
            return 1
        log = Path(str(prefix) + ".log").replace(side / f"chr{chrom}.log")
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("--ref-allele:") or line.startswith("Warning"):
                print(f"chr{chrom} PLINK: {line.strip()}")
        vcf = Path(str(prefix) + ".vcf.gz")
        lf, n = clean_vcf(gzip.open(vcf, "rb").read(), refs)
        bgzf_write(vcf, lf)
        if gzip.open(vcf, "rb").read() != lf:
            raise RuntimeError(f"{vcf}: BGZF round trip failed")
        print(f"chr{chrom}: {n} variants, REF = GRCh38 Ref_Plus at every site, LF line ends, BGZF -> {vcf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
