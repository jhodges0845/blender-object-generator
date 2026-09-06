# SPDX-License-Identifier: GPL-3.0-or-later
"""Test the release ZIP in a fresh Blender process and save a preview."""

from pathlib import Path
import sys
import tempfile
from zipfile import ZipFile

import bpy
from mathutils import Vector

root = Path(__file__).resolve().parents[1]
output = root / "artifacts"
output.mkdir(exist_ok=True)
sys.path[:] = [entry for entry in sys.path
               if Path(entry or ".").resolve() not in (root, root / "scripts")]
assert "humanoid_core" not in sys.modules
assert "humanoid_blender" not in sys.modules

with tempfile.TemporaryDirectory() as directory:
    with ZipFile(root / "dist" / "humanoid_blockout.zip") as archive:
        assert b"GNU GENERAL PUBLIC LICENSE" in archive.read("humanoid_blender/LICENSE")
        assert b"GPL-3.0-or-later" in archive.read("humanoid_blender/NOTICE")
        archive.extractall(directory)
    sys.path.insert(0, directory)
    import humanoid_blender
    from humanoid_blender import core
    Path(core._core.__file__).resolve().relative_to(Path(directory).resolve())
    assert core._core.__name__ == "humanoid_blender.humanoid_core"
    humanoid_blender.register()
    try:
        scene = bpy.data.scenes.new("Humanoid Preview")
        bpy.context.window.scene = scene
        scene.unit_settings.system = "METRIC"
        scene.humanoid_settings.body_type = "average"
        assert bpy.ops.humanoid.generate_blockout() == {"FINISHED"}
        assert bpy.context.view_layer.objects.active.type == "EMPTY"
        scene.humanoid_settings.workflow_tab = "RIGGING"
        assert bpy.ops.humanoid.add_basic_rig() == {"FINISHED"}
        rig = bpy.context.view_layer.objects.active
        assert rig.type == "ARMATURE"
        assert len(rig.data.bones) == 16
        character = rig.parent
        meshes = [obj for obj in character.children if obj.type == "MESH"]
        assert len(meshes) == 15
        assert sum(len(obj.data.vertices) for obj in meshes) == 272
        bpy.context.view_layer.update()
        heights = [(obj.matrix_world @ vertex.co).z
                   for obj in meshes for vertex in obj.data.vertices]
        assert abs(max(heights) - min(heights) - 1.8) < 1e-5
        assert all(not obj.data.validate() for obj in meshes)
        scene.humanoid_settings.workflow_tab = "VALIDATION"
        assert bpy.ops.humanoid.validate_character() == {"FINISHED"}
        assert not any(row.status == "ERROR" for row in scene.humanoid_settings.validation_results)
        camera_data = bpy.data.cameras.new("Preview Camera")
        camera = bpy.data.objects.new("Preview Camera", camera_data)
        scene.collection.objects.link(camera)
        camera.location = (3, 6, 2.4)
        camera.rotation_euler = (Vector((0, 0, 0.9)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
        camera_data.type = "ORTHO"
        camera_data.ortho_scale = 2.5
        scene.camera = camera
        scene.render.engine = "BLENDER_WORKBENCH"
        scene.display.shading.light = "STUDIO"
        scene.display.shading.color_type = "SINGLE"
        scene.display.shading.single_color = (0.23, 0.55, 0.7)
        scene.display.shading.show_shadows = True
        scene.display.shading.show_cavity = True
        scene.display.shading.cavity_type = "BOTH"
        scene.render.resolution_x = 480
        scene.render.resolution_y = 640
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = str(output / "blockout-preview.png")
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type == "VIEW_3D":
                    area.spaces.active.region_3d.view_location = (0, 0, 0.9)
                    area.spaces.active.region_3d.view_distance = 3.5
                    area.spaces.active.region_3d.view_rotation = camera.rotation_euler.to_quaternion()
        bpy.ops.wm.save_as_mainfile(filepath=str(output / "blockout-preview.blend"))
        bpy.ops.render.render(write_still=True)
        print("PACKAGED_ADDON_OK: isolated ZIP registered and generated 15 editable parts and a 16-bone rig")
    finally:
        humanoid_blender.unregister()
