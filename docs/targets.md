# Godot target export

The first Blender target adapter is available through Python (no new UI tab).
Use Blender's Python Console, with the generated root assigned to `root`:

```python
import bpy
from humanoid_blender.targets import get_adapter

adapter = get_adapter("GODOT")  # Core profile defaults to ANIMATED.
issues = adapter.prepare(root, bpy.context)  # Read-only; inspect ERROR/WARN issues.
result = adapter.export(root, bpy.context, "C:/exports/character.glb")
print(result.success, result.filepath)
for issue in result.issues:
    print(issue.status, issue.code, issue.message)
```

The directory must already exist and the output file must be new. Omitting the
extension uses `.glb`. `.gltf` exports JSON, binary and texture sidecars and
requires an empty output directory to avoid overwriting existing sidecars.
For static assets use `get_adapter("GODOT", asset_use="STATIC")`; for a rig
without required animation use `asset_use="RIGGED"`. The core default remains
unchanged. A mesh can itself be the root; empty roots include all descendants.

Preparation requires Object Mode, a visible/selectable hierarchy in the current
view layer, supported EMPTY/MESH/ARMATURE objects, usable transforms, and scene
unit scale 1.0. Non-default units are reported, never automatically changed;
check physical dimensions before any manual rescaling. Mirrored transforms and
constraints prompt review. Muted, solo or multi-strip NLA tracks are rejected
because the tested Blender exporter may export or omit them unexpectedly.
Only active actions and supported NLA clips on scoped objects are exported.
The existing core inspection still evaluates closed geometry and rig weights;
this is a conservative generated-asset workflow, not a general scene exporter.

Core errors block export. Materials, UVs, textures, skins and animations use
Blender's glTF exporter; arbitrary shader graphs are not guaranteed to translate.
Modifiers are not applied destructively. Export temporarily changes selection
and active object, then restores them and the frame on success or failure.
Exporter failures return ERROR issues; partial files may remain for inspection.
ExportResult.success means Blender reported FINISHED and produced a nonempty
file. It does not certify engine import or production quality.

Tested with Blender 2.92 using `scripts/test_blender.py` headlessly. Tests read
GLB/glTF data to verify mesh scope, skins, animation channels, materials and
texture sidecars. Newer Blender action APIs/exporter versions remain unverified.
Manually import into Godot and review scale, axes, normals, texture appearance,
rig deformation, clip timing/looping, collision and LODs before shipping.
Unity, Unreal Engine and 3D Print Blender adapters remain planned.
