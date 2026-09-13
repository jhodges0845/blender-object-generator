from contextlib import contextmanager
from pathlib import Path

from blender_adapter import asset_file_import_ui


def test_external_exchange_files_are_preflighted_without_import(tmp_path):
    filepath = tmp_path / "maxine.glb"
    filepath.write_bytes(b"placeholder")

    report = asset_file_import_ui.preflight_asset_file(filepath)

    assert report["status"] == "EXTERNAL_ASSET"
    assert report["candidate"] == "maxine"
    assert report["extension"] == ".glb"
    assert any("ownership" in line.lower() for line in report["notes"])


def test_unsupported_file_type_is_rejected(tmp_path):
    filepath = tmp_path / "asset.obj"
    filepath.write_text("placeholder")

    try:
        asset_file_import_ui.preflight_asset_file(filepath)
    except ValueError as error:
        assert ".blend" in str(error)
        assert ".fbx" in str(error)
    else:
        raise AssertionError("unsupported file type should be rejected")


def test_blend_with_one_collection_and_no_scene_signals_is_asset_candidate(monkeypatch, tmp_path):
    filepath = tmp_path / "character.blend"
    filepath.write_bytes(b"placeholder")

    class _DataFrom:
        collections = ["Maxine"]
        scenes = ["Scene"]
        objects = ["Maxine", "Body", "Rig"]
        meshes = ["BodyMesh"]
        armatures = ["RigData"]
        actions = ["Idle", "Walk"]
        cameras = []
        lights = []

    @contextmanager
    def _load(_filepath, link=False):
        assert link is False
        yield _DataFrom(), object()

    monkeypatch.setattr(asset_file_import_ui.bpy.data.libraries, "load", _load)

    report = asset_file_import_ui.preflight_asset_file(filepath)

    assert report["status"] == "ASSET_CANDIDATE"
    assert report["candidate"] == "Maxine"
    assert report["candidates"] == ("Maxine",)
    assert any("Nothing has been appended" in line for line in report["notes"])


def test_blend_with_multiple_collections_returns_explicit_choices(monkeypatch, tmp_path):
    filepath = tmp_path / "project.blend"
    filepath.write_bytes(b"placeholder")

    class _DataFrom:
        collections = ["Maxine", "Sword", "Environment"]
        scenes = ["Scene"]
        objects = ["Maxine", "Sword", "Ground"]
        meshes = ["Body", "Blade", "GroundMesh"]
        armatures = ["Rig"]
        actions = []
        cameras = ["Camera"]
        lights = ["Key"]

    @contextmanager
    def _load(_filepath, link=False):
        yield _DataFrom(), object()

    monkeypatch.setattr(asset_file_import_ui.bpy.data.libraries, "load", _load)

    report = asset_file_import_ui.preflight_asset_file(filepath)

    assert report["status"] == "MULTIPLE_CANDIDATES"
    assert report["candidate"] == ""
    assert report["candidates"] == ("Maxine", "Sword", "Environment")
    assert any("choose" in line.lower() for line in report["notes"])
    assert any("project-level" in line.lower() for line in report["notes"])


def test_choose_blend_candidate_only_selects_preflighted_collection():
    scene = {
        asset_file_import_ui._STATUS_KEY: "MULTIPLE_CANDIDATES",
        asset_file_import_ui._CANDIDATE_KEY: "",
        asset_file_import_ui._CANDIDATES_KEY: "Maxine\nSword\nEnvironment",
        asset_file_import_ui._SUMMARY_KEY: "old summary",
    }

    selected = asset_file_import_ui.choose_blend_candidate(scene, "Sword")

    assert selected == "Sword"
    assert scene[asset_file_import_ui._STATUS_KEY] == "ASSET_CANDIDATE"
    assert scene[asset_file_import_ui._CANDIDATE_KEY] == "Sword"
    assert "Selected collection: Sword" in scene[asset_file_import_ui._SUMMARY_KEY]


def test_choose_blend_candidate_rejects_uninspected_collection():
    scene = {
        asset_file_import_ui._STATUS_KEY: "MULTIPLE_CANDIDATES",
        asset_file_import_ui._CANDIDATES_KEY: "Maxine\nSword",
    }

    try:
        asset_file_import_ui.choose_blend_candidate(scene, "Camera")
    except ValueError as error:
        assert "collection candidates" in str(error)
    else:
        raise AssertionError("uninspected collection should be rejected")
