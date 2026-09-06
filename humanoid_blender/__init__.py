# SPDX-License-Identifier: GPL-3.0-or-later
"""Blender add-on entry point. Importing this package does not require Blender."""

bl_info = {
    "name": "Object Generator",
    "author": "Humanoid Blockout contributors",
    "version": (0, 8, 1),
    "blender": (2, 92, 0),
    "location": "3D View > Sidebar > Generator",
    "description": "Generate editable humanoid blockouts from height, weight, and body type",
    "category": "Add Mesh",
}


def register():
    from . import ui
    ui.register()


def unregister():
    from . import ui
    ui.unregister()
