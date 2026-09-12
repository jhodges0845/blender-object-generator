# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for the primary Asset Assistant workspace navigation identity."""

from blender_adapter import workspace_nav_ui


class _Settings:
    asset_assistant_workspace = "ANIMATE"


class _Node:
    def __init__(self):
        self.scale_y = 1.0
        self.scale_x = 1.0
        self.calls = []
        self.children = []

    def row(self, align=False):
        assert align is True
        child = _Node()
        self.children.append(child)
        return child

    def column(self, align=False):
        assert align is True
        child = _Node()
        self.children.append(child)
        return child

    def prop_enum(self, settings, prop, key, **kwargs):
        self.calls.append((prop, key, kwargs))


class _Layout(_Node):
    pass


def test_workspace_tabs_use_one_icon_and_label_button_each():
    layout = _Layout()
    workspace_nav_ui._draw_workspace_nav(layout, _Settings())

    row = layout.children[0]
    assert row.scale_y == 1.65
    assert row.children == []
    assert row.calls == [
        ("asset_assistant_workspace", "CREATE", {"text": "Create", "icon": "USER"}),
        ("asset_assistant_workspace", "ANIMATE", {"text": "Animate", "icon": "ACTION"}),
        ("asset_assistant_workspace", "COMPONENTS", {"text": "Components", "icon": "CUBE"}),
        ("asset_assistant_workspace", "EXPORT", {"text": "Export", "icon": "EXPORT"}),
    ]
