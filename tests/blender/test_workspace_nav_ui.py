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


def test_workspace_tabs_are_large_stacked_cards_with_distinct_icons():
    layout = _Layout()
    workspace_nav_ui._draw_workspace_nav(layout, _Settings())

    cards = layout.children[0]
    assert len(cards.children) == 4

    expected = [
        ("CREATE", "Create", "USER"),
        ("ANIMATE", "Animate", "ACTION"),
        ("COMPONENTS", "Components", "CUBE"),
        ("EXPORT", "Export", "EXPORT"),
    ]

    for card, (key, label, icon) in zip(cards.children, expected):
        assert card.scale_x == 1.12
        icon_row, label_row = card.children
        assert icon_row.scale_y == 1.9
        assert label_row.scale_y == 1.2
        assert icon_row.calls == [("asset_assistant_workspace", key, {"text": "", "icon": icon})]
        assert label_row.calls == [("asset_assistant_workspace", key, {"text": label})]
