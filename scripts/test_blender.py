# SPDX-License-Identifier: GPL-3.0-or-later
"""Run Blender-only integration tests in a Blender background process."""

from pathlib import Path
import sys
import unittest

import bpy  # Fail immediately if this runner is launched outside Blender.

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
suite = unittest.defaultTestLoader.discover(str(root / "tests" / "blender"))
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():
    raise RuntimeError("Blender test suite failed")
