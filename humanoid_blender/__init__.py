# SPDX-License-Identifier: GPL-3.0-or-later
"""Compatibility package for the historical source import name."""
from importlib import import_module
import sys

_canonical = import_module("blender_adapter")
bl_info = _canonical.bl_info
register = _canonical.register
unregister = _canonical.unregister

# Let historical humanoid_blender.<module> imports resolve modules from the
# canonical blender_adapter source directory without duplicating those files.
__path__ = _canonical.__path__
sys.modules[__name__ + ".core"] = import_module("blender_adapter.core_gateway")
