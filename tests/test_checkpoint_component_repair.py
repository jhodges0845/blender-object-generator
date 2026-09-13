import json
from types import SimpleNamespace

from blender_adapter import checkpoint_component_repair


class _Object(dict):
    def __init__(self, name, children=(), **metadata):
        super().__init__(metadata)
        self.name = name
        self.children = list(children)


class _Scene(dict):
    def __init__(self, objects=()):
        super().__init__()
        self.objects = list(objects)


def _registry(*component_ids):
    return json.dumps([{"component_id": component_id} for component_id in component_ids])


def test_repair_removes_only_missing_component_registry_rows():
    valid_root = _Object(
        "Hair",
        asset_assistant_component_id="generated-hair-valid",
        asset_assistant_component_record="{}",
    )
    asset = _Object(
        "Human",
        children=(valid_root,),
        generator="object_generator",
        asset_assistant_components=_registry("generated-hair-valid", "generated-hair-missing"),
    )

    removed = checkpoint_component_repair.repair_missing_component_records(asset)

    assert removed == ("generated-hair-missing",)
    remaining = json.loads(asset["asset_assistant_components"])
    assert remaining == [{"component_id": "generated-hair-valid"}]


def test_repair_refuses_ambiguous_component_roots():
    duplicate_a = _Object(
        "Hair A",
        asset_assistant_component_id="generated-hair-duplicate",
        asset_assistant_component_record="{}",
    )
    duplicate_b = _Object(
        "Hair B",
        asset_assistant_component_id="generated-hair-duplicate",
        asset_assistant_component_record="{}",
    )
    asset = _Object(
        "Human",
        children=(duplicate_a, duplicate_b),
        generator="object_generator",
        asset_assistant_components=_registry("generated-hair-duplicate"),
    )

    try:
        checkpoint_component_repair.repair_missing_component_records(asset)
    except ValueError as error:
        assert "ambiguous" in str(error)
        assert "generated-hair-duplicate" in str(error)
    else:
        raise AssertionError("ambiguous roots must not be repaired automatically")


def test_checkpoint_save_retries_once_after_missing_registry_repair(monkeypatch):
    asset = _Object(
        "Human",
        generator="object_generator",
        asset_assistant_components=_registry("generated-hair-missing"),
    )
    scene = _Scene((asset,))
    calls = []

    def original(filepath, save_operator, scene_arg=None):
        calls.append(filepath)
        if len(calls) == 1:
            raise ValueError("persisted component root is missing: generated-hair-missing")
        return filepath

    working_asset_ui = SimpleNamespace(
        save_editable_checkpoint=original,
        _CHECKPOINT_MESSAGE_KEY="asset_assistant_working_state_message",
    )
    monkeypatch.setattr(checkpoint_component_repair, "is_generated", lambda obj: obj.get("generator") == "object_generator")

    checkpoint_component_repair.install(working_asset_ui)
    result = working_asset_ui.save_editable_checkpoint("hero.blend", object(), scene)

    assert result == "hero.blend"
    assert calls == ["hero.blend", "hero.blend"]
    assert json.loads(asset["asset_assistant_components"]) == []
    assert "generated-hair-missing" in scene["asset_assistant_working_state_message"]
