"""Project ZIP boundary, link and integrity checks without classroom payloads."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock
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

    def test_only_the_nine_notebooks_ship(self):
        files = package.inventory()
        notebooks = sorted(k for k in files if k.startswith("notebooks/"))
        self.assertEqual(len(notebooks), 9)
        self.assertIn("notebooks/gwas_course_complete.Rmd", notebooks)
        self.assertTrue(all(package.NOTEBOOK_NAME.fullmatch(k) for k in notebooks))
        for allowed in ("notebooks/module_03_sample_quality_control.Rmd", "notebooks/gwas_course_complete.Rmd"):
            self.assertTrue(package.NOTEBOOK_NAME.fullmatch(allowed))
        for refused in ("notebooks/module_03_sample_quality_control.qmd", "notebooks/experiment_html/a.html",
                        "notebooks/render_check/module_03.html", "notebooks/module_08_extra.Rmd",
                        "notebooks/notes.md", "notebooks_qmd/module_03.qmd"):
            self.assertIsNone(package.NOTEBOOK_NAME.fullmatch(refused), refused)

    def test_untracked_experiments_stay_out_of_the_inventory(self):
        files = package.inventory()
        self.assertFalse([k for k in files if k.endswith((".qmd", ".html")) or "render_check" in k or "experiment" in k])

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

class PlinkBundleTests(unittest.TestCase):
    """Fake archives only. No network, no real PLINK program."""

    @staticmethod
    def make_archive(folder: Path, members: dict[str, bytes], name: str = "fake.zip") -> Path:
        path = folder / name
        with zipfile.ZipFile(path, "w") as zipped:
            for member, data in members.items():
                zipped.writestr(member, data)
        return path

    def pins(self, archive: Path, program: bytes = b"fake program", member: str = "plink2", platform: str = "linux-x86_64"):
        data = archive.read_bytes()
        return [{"platform": platform, "archive_url": "https://example.invalid/" + archive.name,
                 "archive_sha256": package.digest(data), "archive_bytes": str(len(data)), "member": member,
                 "executable_sha256": package.digest(program), "executable_bytes": str(len(program))}]

    def downloader(self, archive: Path):
        def download(url, destination):
            destination.write_bytes(archive.read_bytes())
        return download

    def test_pinned_program_is_extracted_after_both_hash_checks(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            source = temp / "source"
            source.mkdir()
            archive = self.make_archive(source, {"plink2": b"fake program", "ldsc": b"another program"})
            programs = package.fetch_programs(self.pins(archive), temp / "cache", self.downloader(archive))
            self.assertEqual(programs, {"third_party/plink2/programs/linux-x86_64/plink2": b"fake program"})
            self.assertEqual(package.member_mode("third_party/plink2/programs/linux-x86_64/plink2"), 0o100755)
            self.assertEqual(package.member_mode("R/course.R"), 0o100644)

    def test_wrong_archive_hash_stops_before_extraction(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            source = temp / "source"
            source.mkdir()
            archive = self.make_archive(source, {"plink2": b"fake program"})
            pins = self.pins(archive)
            pins[0]["archive_sha256"] = "0" * 64
            with mock.patch.object(package.zipfile, "ZipFile", side_effect=AssertionError("opened before the hash check")):
                with self.assertRaisesRegex(ValueError, "does not match its pin"):
                    package.fetch_programs(pins, temp / "cache", self.downloader(archive))

    def test_wrong_program_hash_and_wrong_size_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            source = temp / "source"
            source.mkdir()
            archive = self.make_archive(source, {"plink2": b"fake program"})
            for column, value in (("executable_sha256", "1" * 64), ("executable_bytes", "99")):
                pins = self.pins(archive)
                pins[0][column] = value
                with self.subTest(column=column), self.assertRaisesRegex(ValueError, "program for linux-x86_64 does not match"):
                    package.fetch_programs(pins, temp / ("cache-" + column), self.downloader(archive))

    def test_unsafe_missing_and_duplicate_members_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            source = temp / "source"
            source.mkdir()
            cases = {"traversal": {"plink2": b"fake program", "../escape.txt": b"x"},
                     "absolute": {"plink2": b"fake program", "/etc/escape": b"x"},
                     "missing": {"other": b"fake program"}}
            for label, members in cases.items():
                archive = self.make_archive(source, members, label + ".zip")
                with self.subTest(label=label), self.assertRaises(ValueError):
                    package.fetch_programs(self.pins(archive), temp / ("cache-" + label), self.downloader(archive))
            duplicate = source / "duplicate.zip"
            with zipfile.ZipFile(duplicate, "w") as zipped:
                zipped.writestr("plink2", b"fake program")
                with self.assertWarns(UserWarning):
                    zipped.writestr("plink2", b"fake program")
            with self.assertRaisesRegex(ValueError, "exactly one"):
                package.fetch_programs(self.pins(duplicate), temp / "cache-duplicate", self.downloader(duplicate))
            archive = self.make_archive(source, {"plink2": b"fake program"}, "member.zip")
            for member in ("../plink2", "dir/plink2"):
                with self.subTest(member=member), self.assertRaisesRegex(ValueError, "unsafe program path"):
                    package.fetch_programs(self.pins(archive, member=member), temp / ("cache-" + member.replace("/", "_")), self.downloader(archive))

    def test_unsafe_archive_names(self):
        for name in ("../x", "a/../b", "/abs", "a\\b", "C:/x", "C:x", ""):
            with self.subTest(name=name):
                self.assertTrue(package.unsafe_archive_name(name))
        for name in ("plink2", "plink2.exe", "dir/file.txt"):
            with self.subTest(name=name):
                self.assertFalse(package.unsafe_archive_name(name))

    def test_cache_must_be_outside_the_repository(self):
        with self.assertRaises(ValueError):
            package.fetch_programs([], ROOT / "build" / "plink-cache")

    def test_a_cached_archive_with_a_wrong_hash_is_never_trusted(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            source = temp / "source"
            source.mkdir()
            archive = self.make_archive(source, {"plink2": b"fake program"})
            cache = temp / "cache"
            cache.mkdir()
            (cache / archive.name).write_bytes(b"tampered earlier download")
            with self.assertRaisesRegex(ValueError, "does not match its pin"):
                package.fetch_programs(self.pins(archive), cache, self.downloader(archive))

    def test_build_with_programs_keeps_permissions_and_reproduces(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            source = temp / "source"
            source.mkdir()
            archive = self.make_archive(source, {"plink2": b"fake program"})
            pins = self.pins(archive)
            with mock.patch.object(package, "read_pins", return_value=pins):
                first, report = package.build(temp / "one", plink_cache=temp / "cache", download=self.downloader(archive))
                second, _ = package.build(temp / "two", plink_cache=temp / "cache", download=self.downloader(archive))
            self.assertEqual(first.read_bytes(), second.read_bytes())
            name = "GWAS_course/third_party/plink2/programs/linux-x86_64/plink2"
            with zipfile.ZipFile(first) as zipped:
                info = zipped.getinfo(name)
                self.assertEqual(info.create_system, 3)
                self.assertEqual(info.external_attr >> 16, 0o100755)
                self.assertEqual(zipped.read(name), b"fake program")
                self.assertEqual(zipped.getinfo("GWAS_course/config.R").external_attr >> 16, 0o100644)
                self.assertIn("GWAS_course/third_party/plink2/COPYING", zipped.namelist())
                self.assertIn("GWAS_course/third_party/plink2/releases.tsv", zipped.namelist())
            self.assertEqual([p["path"] for p in report["plink_programs"]],
                             ["third_party/plink2/programs/linux-x86_64/plink2"])
            package.verify_archive(first, {**package.inventory(), "third_party/plink2/programs/linux-x86_64/plink2": b"fake program"})
            # A ZIP whose program lost its permission bits is refused.
            broken = temp / "broken.zip"
            with zipfile.ZipFile(first) as source_zip, zipfile.ZipFile(broken, "w") as target:
                for entry in source_zip.infolist():
                    clone = zipfile.ZipInfo(entry.filename, date_time=entry.date_time)
                    clone.create_system = 3
                    clone.external_attr = 0o100644 << 16
                    target.writestr(clone, source_zip.read(entry.filename))
            with self.assertRaisesRegex(ValueError, "file permission"):
                package.verify_archive(broken, {**package.inventory(), "third_party/plink2/programs/linux-x86_64/plink2": b"fake program"})

    def test_default_build_adds_no_program(self):
        with tempfile.TemporaryDirectory() as temp:
            _, report = package.build(Path(temp) / "plain")
            self.assertEqual(report["plink_programs"], [])
            self.assertFalse([f for f in report["files"] if "/programs/" in f["path"]])

    def test_tracked_programs_and_archives_are_refused_by_name(self):
        for name in ("bin/plink2", "bin/plink2.exe", "third_party/plink2/plink2_win64_20261107.zip",
                     "R/helper.dll", "x/ldsc", "x/mtag.exe", "data.tar", "library.so"):
            with self.subTest(name=name):
                self.assertTrue(package.PROGRAM_NAME.search(name) or name.lower().endswith(package.ARCHIVE_SUFFIXES), name)
        for name in ("third_party/plink2/releases.tsv", "examples/formats/invented_example_plink2.pgen",
                     "R/plink_setup.R", "bin/README.md"):
            with self.subTest(name=name):
                self.assertFalse(package.PROGRAM_NAME.search(name) or name.lower().endswith(package.ARCHIVE_SUFFIXES), name)
        self.assertIsNotNone(package.THIRD_PARTY_NAME.fullmatch("third_party/plink2/notices/zstd-LICENSE"))
        self.assertIsNone(package.THIRD_PARTY_NAME.fullmatch("third_party/plink2/programs/linux-x86_64/plink2"))
        self.assertIsNone(package.THIRD_PARTY_NAME.fullmatch("third_party/other/COPYING"))

    def test_real_pin_list_is_valid(self):
        pins = package.read_pins()
        self.assertEqual(len(pins), 4)
        bad = ROOT / "does-not-exist"
        with self.assertRaises(OSError):
            package.read_pins(bad)


if __name__ == "__main__":
    unittest.main()
