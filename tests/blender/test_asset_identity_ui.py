from types import SimpleNamespace

from blender_adapter import asset_identity_ui


class _Layout:
    def __init__(self):
        self.boxes = []
        self.calls = []

    def box(self):
        child = _Layout()
        self.boxes.append(child)
        return child

    def label(self, **kwargs):
        self.calls.append(("label", kwargs))

    def prop(self, data, prop, **kwargs):
        self.calls.append(("prop", data, prop, kwargs))


def test_asset_identity_adds_editable_name_for_current_target():
    root = SimpleNamespace(name="Human")
    context = SimpleNamespace(scene=SimpleNamespace(humanoid_settings=SimpleNamespace(target=root)))
    layout = _Layout()
    workflow_ui = SimpleNamespace(_asset_summary=lambda _layout, _context: None)

    asset_identity_ui.install(workflow_ui)
    workflow_ui._asset_summary(layout, context)

    assert len(layout.boxes) == 1
    identity = layout.boxes[0]
    assert ("label", {"text": "ASSET IDENTITY", "icon": "OBJECT_DATA"}) in identity.calls
    assert ("prop", root, "name", {"text": "Name"}) in identity.calls


def test_asset_identity_stays_hidden_without_target():
    context = SimpleNamespace(scene=SimpleNamespace(humanoid_settings=SimpleNamespace(target=None)))
    layout = _Layout()
    workflow_ui = SimpleNamespace(_asset_summary=lambda _layout, _context: None)

    asset_identity_ui.install(workflow_ui)
    workflow_ui._asset_summary(layout, context)

    assert layout.boxes == []
