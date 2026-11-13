"""Check the actual invented bytes, metadata and offline PLINK round trips."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("format_examples", ROOT / "scripts/author/make_format_examples.py")
examples = importlib.util.module_from_spec(spec)
spec.loader.exec_module(examples)


def example_path(kind):
    return examples.EXAMPLES / examples.FILES[kind]


class FormatExamplesTests(unittest.TestCase):
    def test_native_comments_keep_readable_label(self):
        for kind in (".vcf", "dosages.vcf", ".fasta", ".fastq", ".sam", ".g.vcf",
                     "final_report.txt", "intervals.bed", "summary.tsv", ".pvar"):
            with self.subTest(format=kind):
                self.assertIn("invented example", example_path(kind).read_text(encoding="utf-8"))

    def test_export_rejects_an_unlisted_file_before_copying(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "examples") as folder:
            source = Path(folder) / "source"
            source.mkdir()
            (source / "unexpected.txt").write_text("invented example\n", encoding="utf-8")
            destination = Path(folder) / "export"
            with patch.object(examples, "EXAMPLES", source), self.assertRaisesRegex(ValueError, "complete set"):
                examples.export_formats(destination)
            self.assertFalse(destination.exists())

    def test_reproducible_generation_and_all_genotype_round_trips(self):
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in examples.EXAMPLES.iterdir()}
        report = examples.generate(Path(os.environ.get("PLINK2_BIN", ROOT / "bin/plink2.exe")).resolve())
        after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in examples.EXAMPLES.iterdir()}
        self.assertEqual(before, after)
        self.assertEqual(set(report["round_trips"]), {"vcf", "bed", "pgen", "ped", "tped", "bgen"})
        self.assertLess(report["total_bytes"], 100000)

    def test_labels_no_vendor_binaries_and_actual_headers(self):
        self.assertEqual({p.name for p in examples.EXAMPLES.iterdir()}, set(examples.FILES.values()))
        for p in examples.EXAMPLES.iterdir():
            self.assertTrue(p.name.startswith("invented_example"))
            self.assertNotRegex(p.name, r"\s")
            self.assertNotIn(p.suffix.lower(), {".idat", ".gtc", ".cel", ".bam", ".cram", ".pod5"})
        self.assertEqual(example_path(".bed").read_bytes()[:3], bytes.fromhex("6c 1b 01"))
        self.assertEqual(example_path(".pgen").read_bytes()[:2], bytes.fromhex("6c 1b"))
        bgen = example_path(".bgen").read_bytes()
        self.assertEqual(bgen[16:20], b"bgen")
        self.assertEqual(struct.unpack_from("<II", bgen, 8), (5, 4))
        header_length = struct.unpack_from("<I", bgen, 4)[0]
        flags = struct.unpack_from("<I", bgen, header_length)[0]
        self.assertEqual((flags >> 2) & 15, 2)
        for extension in ("bed", "pgen", "bgen"):
            raw = example_path("." + extension).read_bytes()
            self.assertIn(raw[:32].hex(" "), example_path("." + extension + ".hex.txt").read_text(encoding="utf-8"))

    def test_reference_reads_sex_and_dosage_consistency(self):
        fasta = example_path(".fasta").read_bytes()
        name, length, offset, bases, width = example_path(".fasta.fai").read_text(encoding="utf-8").strip().split("\t")
        self.assertEqual((name, length, bases, width), ("toy1", "60", "60", "61"))
        self.assertEqual(fasta[int(offset):int(offset) + 60], b"ACGT" * 15)
        reads = example_path(".fastq").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(reads), 8)
        for i in (0, 4):
            self.assertEqual(len(reads[i+1]), len(reads[i+3]))
        fam = [line.split() for line in example_path(".fam").read_text(encoding="utf-8").splitlines()]
        self.assertEqual([row[4] for row in fam], ["1", "2", "0", "2"])
        for line in example_path("dosages.vcf").read_text(encoding="utf-8").splitlines():
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
        committed_dir = ROOT / "site_content/formats"
        self.assertEqual({p.name for p in (committed_dir / "examples").iterdir()}, set(examples.FILES.values()))
        description_names = {name + ".json" for name in examples.FILES.values()} | {
            name + ".json" for name in ("idat", "gtc", "cel", "bam", "cram", "pod5")}
        self.assertEqual({p.name for p in committed_dir.glob("*.json")}, description_names)
        with tempfile.TemporaryDirectory(dir=ROOT / "examples") as folder:
            entries = examples.export_formats(Path(folder))
            concrete = [e for e in entries if e["asset"]]
            self.assertEqual(len(concrete), 25)
            for entry in concrete:
                source = examples.EXAMPLES / entry["file_name"]
                self.assertEqual(source.read_bytes(), (Path(folder) / entry["asset"]).read_bytes())
                self.assertTrue(entry["columns_or_fields"])
                self.assertEqual(entry["label"], "invented example")
                self.assertEqual(entry["header_notes"][0], "Invented example; no real individuals.")
                for note in entry["header_notes"]:
                    self.assertNotIn("not reference-validated", note)
                    self.assertNotIn("label is", note)
                committed = ROOT / "site_content/formats" / (source.name + ".json")
                self.assertEqual(json.loads(committed.read_text(encoding="utf-8")), entry)
            self.assertEqual({e["format"] for e in entries if not e["asset"]}, {"IDAT", "GTC", "CEL", "BAM", "CRAM", "POD5"})


if __name__ == "__main__":
    unittest.main()
