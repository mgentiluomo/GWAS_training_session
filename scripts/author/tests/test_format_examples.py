"""Check the actual invented bytes, metadata and offline PLINK round trips."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("format_examples", ROOT / "scripts/author/make_format_examples.py")
examples = importlib.util.module_from_spec(spec)
spec.loader.exec_module(examples)


class FormatExamplesTests(unittest.TestCase):
    def test_reproducible_generation_and_all_genotype_round_trips(self):
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in examples.EXAMPLES.iterdir()}
        report = examples.generate(Path(os.environ.get("PLINK2_BIN", ROOT / "bin/plink2.exe")).resolve())
        after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in examples.EXAMPLES.iterdir()}
        self.assertEqual(before, after)
        self.assertEqual(set(report["round_trips"]), {"vcf", "bed", "pgen", "ped", "tped", "bgen"})
        self.assertLess(report["total_bytes"], 100000)

    def test_labels_no_vendor_binaries_and_actual_headers(self):
        for p in examples.EXAMPLES.iterdir():
            self.assertIn("invented example", p.name)
            self.assertNotIn(p.suffix.lower(), {".idat", ".gtc", ".cel", ".bam", ".cram", ".pod5"})
        prefix = examples.EXAMPLES / examples.LABEL
        self.assertEqual(Path(str(prefix) + ".bed").read_bytes()[:3], bytes.fromhex("6c 1b 01"))
        self.assertEqual(Path(str(prefix) + ".pgen").read_bytes()[:2], bytes.fromhex("6c 1b"))
        bgen = Path(str(prefix) + ".bgen").read_bytes()
        self.assertEqual(bgen[16:20], b"bgen")
        self.assertEqual(struct.unpack_from("<II", bgen, 8), (5, 4))
        header_length = struct.unpack_from("<I", bgen, 4)[0]
        flags = struct.unpack_from("<I", bgen, header_length)[0]
        self.assertEqual((flags >> 2) & 15, 2)
        for extension in ("bed", "pgen", "bgen"):
            raw = Path(str(prefix) + "." + extension).read_bytes()
            self.assertIn(raw[:32].hex(" "), Path(str(prefix) + "." + extension + ".hex.txt").read_text())

    def test_reference_reads_sex_and_dosage_consistency(self):
        prefix = examples.EXAMPLES / examples.LABEL
        fasta = Path(str(prefix) + ".fasta").read_bytes()
        name, length, offset, bases, width = Path(str(prefix) + ".fasta.fai").read_text().strip().split("\t")
        self.assertEqual((name, length, bases, width), ("toy1", "60", "60", "61"))
        self.assertEqual(fasta[int(offset):int(offset) + 60], b"ACGT" * 15)
        reads = Path(str(prefix) + ".fastq").read_text().splitlines()
        self.assertEqual(len(reads), 8)
        for i in (0, 4):
            self.assertEqual(len(reads[i+1]), len(reads[i+3]))
        fam = [line.split() for line in Path(str(prefix) + ".fam").read_text().splitlines()]
        self.assertEqual([row[4] for row in fam], ["1", "2", "0", "2"])
        for line in Path(str(prefix) + " imputed.vcf").read_text().splitlines():
            if line.startswith("#"):
                continue
            for field in line.split("\t")[9:]:
                gt, ds, gp = field.split(":")
                if gt == "./.":
                    self.assertEqual(ds, ".")
                    continue
                probabilities = list(map(float, gp.split(",")))
                self.assertAlmostEqual(sum(probabilities), 1)
                self.assertAlmostEqual(float(ds), sum(i * p for i, p in enumerate(probabilities)))

    def test_catalogue_mirrors_every_example_and_describes_binaries_only(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "examples") as folder:
            entries = examples.export_formats(Path(folder))
            concrete = [e for e in entries if e["asset"]]
            self.assertEqual(len(concrete), 25)
            for entry in concrete:
                source = examples.EXAMPLES / entry["file_name"]
                self.assertEqual(source.read_bytes(), (Path(folder) / entry["asset"]).read_bytes())
                self.assertTrue(entry["columns_or_fields"])
                committed = ROOT / "site_content/formats" / (source.name.replace(" ", "-") + ".json")
                self.assertEqual(json.loads(committed.read_text()), entry)
            self.assertEqual({e["format"] for e in entries if not e["asset"]}, {"IDAT", "GTC", "CEL", "BAM", "CRAM", "POD5"})


if __name__ == "__main__":
    unittest.main()
