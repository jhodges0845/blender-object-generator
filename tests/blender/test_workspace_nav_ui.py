# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for the primary Asset Assistant workspace navigation identity."""

from blender_adapter import workspace_nav_ui


class _Settings:
    asset_assistant_workspace = "ANIMATE"


class _Row:
    def __init__(self):
        self.scale_y = 1.0
        self.calls = []

    def prop_enum(self, settings, prop, key, **kwargs):
        self.calls.append((prop, key, kwargs))


class _Layout:
    def __init__(self):
        self.created_row = None

    def row(self, align=False):
        assert align is True
        self.created_row = _Row()
        return self.created_row


def test_workspace_tabs_have_distinct_icons_and_strong_height():
    layout = _Layout()
    workspace_nav_ui._draw_workspace_nav(layout, _Settings())

    row = layout.created_row
    assert row.scale_y == 1.55
    assert [call[1] for call in row.calls] == ["CREATE", "ANIMATE", "COMPONENTS", "EXPORT"]
    assert [call[2]["icon"] for call in row.calls] == ["USER", "ACTION", "CUBE", "EXPORT"]
    assert row.calls[1][2]["text"].strip() == "Animate"
