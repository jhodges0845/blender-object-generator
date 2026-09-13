from blender_adapter import asset_inspection_ui


class _Object:
    def __init__(self, name, type="EMPTY", parent=None, **metadata):
        self.name = name
        self.type = type
        self.parent = parent
        self.children = []
        self.modifiers = []
        self.material_slots = []
        self.animation_data = None
        self._metadata = metadata
        if parent is not None:
            parent.children.append(self)

    def get(self, key, default=None):
        return self._metadata.get(key, default)


class _Modifier:
    type = "ARMATURE"

    def __init__(self, obj):
        self.object = obj


class _Slot:
    def __init__(self, material):
        self.material = material


class _AnimationData:
    def __init__(self, action=None, tracks=()):
        self.action = action
        self.nla_tracks = tuple(tracks)


def test_generated_asset_is_reported_ready_without_using_display_name_as_identity():
    root = _Object("Maxine", generator="object_generator", object_type="human_experimental")
    _Object("Body", type="MESH", parent=root)

    report = asset_inspection_ui.inspect_selected_asset(root.children[0])

    assert report["root"] is root
    assert report["name"] == "Maxine"
    assert report["status"] == "READY"
    assert report["metrics"]["meshes"] == 1
    assert "Recognized Asset Assistant metadata." in report["notes"]


def test_artist_mesh_inspection_detects_external_rig_materials_and_animation_read_only():
    mesh = _Object("ArtistCharacter", type="MESH")
    rig = _Object("ArtistRig", type="ARMATURE")
    rig.animation_data = _AnimationData(action=object(), tracks=(object(),))
    mesh.modifiers.append(_Modifier(rig))
    mesh.material_slots.extend((_Slot(object()), _Slot(object())))

    report = asset_inspection_ui.inspect_selected_asset(mesh)

    assert report["status"] == "REVIEW"
    assert report["metrics"] == {"meshes": 1, "armatures": 1, "materials": 2, "animations": 2}
    assert any("no Asset Assistant ownership was added" in note for note in report["notes"])
    assert any("Adoption remains optional" in note for note in report["notes"])


def test_import_group_inspection_uses_whole_file_when_child_is_selected(monkeypatch):
    group = "import-123"
    root = _Object("ImportedRoot", asset_assistant_import_group=group, asset_assistant_import_root=True)
    mesh = _Object("Body", type="MESH", parent=root, asset_assistant_import_group=group)
    sibling_mesh = _Object("Eyes", type="MESH", asset_assistant_import_group=group)
    rig = _Object("Rig", type="ARMATURE", asset_assistant_import_group=group)
    rig.animation_data = _AnimationData(action=object(), tracks=(object(),))
    mesh.modifiers.append(_Modifier(rig))
    material = object()
    mesh.material_slots.append(_Slot(material))
    sibling_mesh.material_slots.append(_Slot(material))
    monkeypatch.setattr(asset_inspection_ui.bpy.data, "objects", (root, mesh, sibling_mesh, rig))

    report = asset_inspection_ui.inspect_selected_asset(mesh)

    assert report["root"] is root
    assert report["name"] == "ImportedRoot"
    assert report["metrics"] == {"meshes": 2, "armatures": 1, "materials": 1, "animations": 2}
    assert any("complete imported file hierarchy" in note for note in report["notes"])


def test_import_group_inspection_is_stable_when_rig_is_selected(monkeypatch):
    group = "import-456"
    root = _Object("FBXRoot", asset_assistant_import_group=group, asset_assistant_import_root=True)
    mesh = _Object("Body", type="MESH", asset_assistant_import_group=group)
    rig = _Object("Rig", type="ARMATURE", asset_assistant_import_group=group)
    rig.animation_data = _AnimationData(action=object(), tracks=(object(),))
    mesh.modifiers.append(_Modifier(rig))
    monkeypatch.setattr(asset_inspection_ui.bpy.data, "objects", (root, mesh, rig))

    from_mesh = asset_inspection_ui.inspect_selected_asset(mesh)
    from_rig = asset_inspection_ui.inspect_selected_asset(rig)

    assert from_mesh["root"] is root
    assert from_rig["root"] is root
    assert from_mesh["metrics"] == from_rig["metrics"]
    assert from_rig["metrics"]["animations"] == 2


def test_non_mesh_selection_reports_needs_setup():
    root = _Object("Empty")

    report = asset_inspection_ui.inspect_selected_asset(root)

    assert report["status"] == "NEEDS_SETUP"
    assert report["metrics"]["meshes"] == 0
    assert any("No mesh geometry" in note for note in report["notes"])
