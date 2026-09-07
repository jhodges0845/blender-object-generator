# SPDX-License-Identifier: GPL-3.0-or-later
"""Blender adapter entry point. Importing this package does not require Blender."""

import sys

from . import core_gateway as core

# Preserve the historical ``.core`` import path while the source file uses the
# clearer ``core_gateway.py`` name. This keeps internal/third-party imports
# working without keeping a misleading core.py file in the source tree.
sys.modules[__name__ + ".core"] = core

bl_info = {
    "name": "Asset Assistant",
    "author": "Asset Assistant contributors",
    "version": (0, 9, 0),
    "blender": (2, 92, 0),
    "location": "3D View > Sidebar > Generator",
    "description": "Generate, prepare, validate, and export editable 3D assets",
    "category": "3D View",
}


def register():
    from . import ui
    # Keep stable class/operator IDs for compatibility while presenting the new
    # product name to artists in Blender.
    ui.HUMANOID_PT_panel.bl_label = "Asset Assistant"
    ui.register()


def unregister():
    from . import ui
    ui.unregister()
