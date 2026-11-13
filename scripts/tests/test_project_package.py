"""Project ZIP boundary, link and integrity checks without classroom payloads."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("project_package", ROOT / "scripts/package_project.py")
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class ProjectPackageTests(unittest.TestCase):
    def test_allowlist_and_project_name(self):
        files = package.inventory()
        self.assertIn("GWAS_course.Rproj", files)
        self.assertNotIn("GWAS_training_session.Rproj", files)
        self.assertEqual(sum(k.startswith("lessons/") for k in files), 8)
        for name in files:
            self.assertTrue(name in package.FILES or any(name.startswith(folder + "/") for folder in package.FOLDERS), name)
            self.assertFalse(name.startswith(("legacy/", "site_content/", "tutorial", "scripts/author/", "data/", "results/", "build/")))
        self.assertEqual({k for k in files if k.startswith("scripts/")},
                         {k for k in package.FILES if k.startswith("scripts/")})

    def test_local_links_and_anchors(self):
        files = {"README.md": b"# Home\n[Guide](docs/setup.md#ready)\n",
                 "docs/setup.md": b"# Ready\n[Home](../README.md)\n"}
        self.assertEqual(package.check_links(files)["local_links_checked"], 2)
        for target in ("../outside.md", "missing.md", "docs/setup.md#missing", "/absolute"):
            with self.subTest(target=target), self.assertRaises(ValueError):
                package.check_links({**files, "README.md": ("[Bad](" + target + ")").encode()})
        self.assertIn("chosen", package.anchors("## Heading {#chosen}"))
        self.assertIn("a-heading", package.anchors("## A heading"))

    def test_external_destination_and_explicit_version(self):
        with self.assertRaises(ValueError):
            package.external_folder(ROOT / "build", ROOT)
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                package.build(Path(temp) / "bad", "latest")

    def test_real_allowlist_links_and_reproducible_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            first, report = package.build(Path(temp) / "one")
            second, again = package.build(Path(temp) / "two")
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(report["sha256"], again["sha256"])
            self.assertGreater(report["links"]["local_links_checked"], 100)
            files = package.inventory()
            package.verify_archive(first, files)
            with zipfile.ZipFile(first, "a") as zipped:
                zipped.writestr("GWAS_course/../unsafe.txt", "not allowed")
            with self.assertRaises(ValueError):
                package.verify_archive(first, files)


if __name__ == "__main__":
    unittest.main()
