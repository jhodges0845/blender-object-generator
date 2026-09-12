# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for replace-current generation behavior."""

from blender_adapter import generation_replace_ui


class _Object:
    def __init__(self, name, children=()):
        self.name = name
        self.children = list(children)


def test_descendants_walks_nested_asset_hierarchy():
    leaf = _Object("leaf")
    child = _Object("child", (leaf,))
    root = _Object("root", (child,))

    assert [obj.name for obj in generation_replace_ui._descendants(root)] == ["child", "leaf"]
