"""Packaging regression checks. All fixtures stay outside the repository."""
import csv
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("package_release", Path(__file__).parents[1] / "package_release.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class PackagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not release.WORK.is_dir():
            raise unittest.SkipTest(f"Release work folder not found: {release.WORK}. "
                                    "Create it or set COURSE_RELEASE_WORK to run the packaging tests.")
        cls.root = Path(tempfile.mkdtemp(prefix="package-tests-", dir=release.WORK))
        cls.source = cls.root / "student"
        (cls.source / "lab_export").mkdir(parents=True)
        (cls.source / "lab_export" / "small.txt").write_text("Synthetic fixture.\n", encoding="ascii")

    def test_restricted_names(self):
        for word in release.FORBIDDEN:
            with self.assertRaises(ValueError):
                release.safe_path(self.root / ("nested_" + word.upper()) / "file")

    def test_unknown_file(self):
        source = self.root / "unknown"
        source.mkdir()
        (source / "unexpected.txt").write_text("fixture", encoding="utf-8")
        with self.assertRaises(ValueError):
            release.inventory(source)

    def test_module_a_rule(self):
        source = self.root / "stage-module-a-test"
        for folder in sorted(release.MODULE_A_DIRECTORIES):
            (source / folder).mkdir(parents=True)
            (source / folder / "small.txt").write_text("Synthetic fixture.\n", encoding="ascii")
        (source / "README_simulated.txt").write_text("fixture\n", encoding="ascii")
        (source / "panel_samples.tsv").write_text("fixture\n", encoding="ascii")
        (source / "R").mkdir()
        (source / "R" / "imputation.R").write_text("# helpers\n", encoding="ascii")
        (source / "imputed" / "run.log").write_text("author path\n", encoding="ascii")
        names = [name for _, name in release.inventory(source, "module-a")]
        self.assertEqual(sorted(names), sorted([f"{d}/small.txt" for d in release.MODULE_A_DIRECTORIES]
                                               + ["README_simulated.txt", "panel_samples.tsv", "R/imputation.R"]))
        # Each package accepts only its own top folders and files.
        with self.assertRaises(ValueError):
            release.inventory(source, "main")
        with self.assertRaises(ValueError):
            release.inventory(self.source, "module-a")
        # R/imputation.R is the only R file module A may carry.
        (source / "R" / "guided.R").write_text("# not part of module A\n", encoding="ascii")
        with self.assertRaises(ValueError):
            release.inventory(source, "module-a")
        (source / "R" / "guided.R").unlink()
        # FORBIDDEN still applies to module A.
        (source / "truth").mkdir()
        (source / "truth" / "x.txt").write_text("fixture", encoding="ascii")
        with self.assertRaises(ValueError):
            release.inventory(source, "module-a")
        self.assertNotIn("truth", " ".join(release.MODULE_A_DIRECTORIES))

    def test_main_rule_unchanged(self):
        # The main package keeps its folders and README, and still refuses module A material.
        self.assertEqual(release.PACKAGES["main"]["stage_prefix"], "classroom-stage-")
        self.assertEqual(release.PACKAGES["main"]["files"], set())
        source = self.root / "main-rule"
        (source / "lab_export").mkdir(parents=True)
        (source / "lab_export" / "small.txt").write_text("fixture\n", encoding="ascii")
        (source / "README_simulated.txt").write_text("fixture\n", encoding="ascii")
        self.assertEqual(sorted(n for _, n in release.inventory(source)), ["README_simulated.txt", "lab_export/small.txt"])
        (source / "R").mkdir()
        (source / "R" / "imputation.R").write_text("# helpers\n", encoding="ascii")
        with self.assertRaises(ValueError):
            release.inventory(source)

    def test_dry_run_needs_no_password(self):
        previous = os.environ.pop("COURSE_RELEASE_PASSWORD", None)
        try:
            output = self.root / "dry-run"
            result = release.dry_run(self.source, output)
        finally:
            if previous is not None:
                os.environ["COURSE_RELEASE_PASSWORD"] = previous
        self.assertEqual(result["files"], 1)
        self.assertEqual(sorted(p.name for p in output.iterdir()), ["MANIFEST.tsv", "members.txt"])
        with (output / "MANIFEST.tsv").open(encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream, delimiter="\t"))
        fixture = self.source / "lab_export" / "small.txt"
        self.assertEqual(rows, [{"path": "lab_export/small.txt", "bytes": str(fixture.stat().st_size),
                                 "sha256": release.sha256(fixture)}])
        with self.assertRaises(ValueError):
            release.dry_run(self.source, output)

    def test_missing_password(self):
        previous = os.environ.pop("COURSE_RELEASE_PASSWORD", None)
        try:
            with self.assertRaises(ValueError):
                release.build(self.source, self.root / "no-password", Path("7z"))
        finally:
            if previous is not None:
                os.environ["COURSE_RELEASE_PASSWORD"] = previous

    def test_output_inside_repository(self):
        with self.assertRaises(ValueError):
            release.build(self.source, release.REPO / "forbidden-output", Path("7z"))

    def test_encrypted_round_trip(self):
        # The caller supplies a throwaway password. No password is stored here.
        password = os.environ.get("COURSE_RELEASE_PASSWORD")
        if not password:
            self.skipTest("COURSE_RELEASE_PASSWORD is not set. Set a throwaway password to run the encrypted round trip.")
        sevenzip = Path(r"C:\Program Files\7-Zip\7z.exe")
        if not sevenzip.is_file():
            self.skipTest(f"7-Zip not found at {sevenzip}. The encrypted round trip needs it.")
        output = self.root / "release"
        result = release.build(self.source, output, sevenzip)
        self.assertEqual(result["files"], 1)
        archive = Path(result["archive"])
        with (output / "MANIFEST.tsv").open(encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream, delimiter="\t"))
        self.assertEqual(rows[0]["sha256"], release.sha256(self.source / rows[0]["path"]))
        sums = (output / "SHA256SUMS.txt").read_text(encoding="ascii").splitlines()
        self.assertEqual(sums, [f"{result['archive_sha256']}  {archive.name}",
                                f"{result['manifest_sha256']}  MANIFEST.tsv"])
        self.assertEqual(release.aes256_members(archive), [rows[0]["path"]])
        good = subprocess.run([str(sevenzip), "t", str(archive)], input=password + "\n",
                              text=True, capture_output=True)
        bad = subprocess.run([str(sevenzip), "t", str(archive)], input="incorrect\n",
                             text=True, capture_output=True)
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
        self.assertNotEqual(bad.returncode, 0)
        with self.assertRaises(ValueError):
            release.build(self.source, output, sevenzip)


if __name__ == "__main__":
    unittest.main()
