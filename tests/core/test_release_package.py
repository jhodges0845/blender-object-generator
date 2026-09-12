# SPDX-License-Identifier: GPL-3.0-or-later
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from scripts.build_blender_addon import build_addon


class ReleasePackageTests(unittest.TestCase):
    def test_addon_zip_contains_runtime_docs_and_license_only(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "asset_assistant.zip"
            result = build_addon(output)
            self.assertEqual(result, output)
            self.assertTrue(output.is_file())

            with ZipFile(output) as archive:
                names = archive.namelist()

            required = {
                "humanoid_blender/__init__.py",
                "humanoid_blender/object_core/__init__.py",
                "humanoid_blender/README.md",
                "humanoid_blender/rigging.md",
                "humanoid_blender/workflow.md",
                "humanoid_blender/animation.md",
                "humanoid_blender/LICENSE",
                "humanoid_blender/NOTICE",
            }
            self.assertTrue(required.issubset(names))
            self.assertTrue(all(name.startswith("humanoid_blender/") for name in names))
            self.assertFalse(any("__pycache__" in name for name in names))
            self.assertFalse(any(name.endswith((".pyc", ".pyo")) for name in names))
            self.assertFalse(any(name.startswith("tests/") for name in names))
            self.assertFalse(any(name.startswith(".github/") for name in names))

    def test_release_zip_is_byte_for_byte_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.zip"
            second = Path(directory) / "second.zip"
            build_addon(first)
            build_addon(second)
            self.assertEqual(first.read_bytes(), second.read_bytes())

            with ZipFile(first) as archive:
                infos = archive.infolist()
            self.assertEqual([info.filename for info in infos], sorted(info.filename for info in infos))
            self.assertTrue(all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in infos))
            self.assertTrue(all((info.external_attr >> 16) & 0o777 == 0o644 for info in infos))


if __name__ == "__main__":
    unittest.main()
