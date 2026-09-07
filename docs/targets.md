# Export files from Blender

No console commands are needed. In **Export** in the 3D Viewport sidebar (N), choose the model and
its destination. Export Asset opens Blender's standard file browser when the
background checks have no unresolved errors or warnings. Detailed results and
Add Missing Materials live in the Validation sidebar tab. Export shows only a
compact readiness indicator, export controls and the last saved path.

Panel headers show an attention icon for unresolved problems or a checkmark when
the applicable checks pass. Rigging and Animations show problems relevant to their
stage; Validation and Export summarize all target requirements. These icons are
in the panel headers, not on Blender's vertical category labels.

| Destination | Output | Included |
| --- | --- | --- |
| Godot | `.glb` by default; `.gltf` also allowed | Meshes, supported materials/textures, rig and animation |
| Unity | `.fbx` | Meshes, basic materials, saved image textures embedded in the file, rig and animation |
| Unreal Engine | `.fbx` | Meshes, basic materials, saved image textures embedded in the file, rig and animation |
| Cura | `.stl` | Evaluated current-pose triangles in millimetres; no rig, animation or materials |

## Blender steps

1. Install the rebuilt `dist/object_generator.zip` (version 0.8.2) and restart
   Blender if an older version was loaded.
2. Generate or choose the model. For game assets, choose Static Asset, Rigged
   Asset or Animated Asset. Add a rig/idle from the corresponding stages when
   needed. Cura automatically validates the evaluated static pose.
3. Open Export and choose the destination. For game assets, open Validation and click **Add Missing
   Materials** or assign your own. The button adds neutral Principled materials
   only to missing assignments and supports Undo. It does not replace your art.
4. Resolve the checklist in Validation. Missing textures need actual files; textured models
   need UVs. Save/pack generated images for Godot; FBX requires saved PNG/JPEG
   files before export. Bake procedural shaders/mapping to images, and apply
   non-armature modifiers on an export copy if using a game target.
5. When **Export Asset** enables, click it, choose an existing directory and a
   new filename, then confirm. A successful export reports the saved path.
6. Import that file with the destination application's normal model importer.
   There is no custom import script or connector to install.

Export rechecks the current model after the file browser closes. Changing target,
geometry, material, rig or animation data can disable Export again. Old validation
snapshots never authorize an export. Existing output files are preserved; use a
new filename when iterating. Separate glTF requires an empty directory for its
binary/texture sidecars. An exporter failure can leave partial files for review.

## What happened to the warnings?

- **Materials** is an actionable error for game targets until every used face has
  a material. Add Missing Materials resolves it with a neutral exportable material.
- **Blockout** is an informational design note for actual multipart blockouts,
  not a warning attached to every model. It does not certify smooth joints.
- **Export Review** and destination review are informational reminders about
  checks in the importing application, not permanently unresolved warnings.
- Actual errors and warnings still block Export. They are never automatically
  converted to PASS. Export shows a compact live readiness status; Validation
  stores a snapshot when Run Validation is pressed.

## Target-specific preparation

Godot currently requires scene unit scale 1.0. The exporter does not silently
rescale your model. Check physical dimensions before changing units. FBX carries
Blender's unit scale; Unity uses Y-up export axes and Unreal uses Z-up. FBX exports
the scene playback range as one baked take containing the scoped objects' active
animation/NLA evaluation; it does not export every action in the blend file.
Set the playback range to your intended clip before export. Leaf bones are off.

Game export currently accepts plain Principled materials and direct image
textures, with optional normal-map nodes. Procedural shader/mapping graphs need
manual baking. FBX's basic material translation cannot recreate every Blender
PBR feature; verify imported appearance in the engine. Muted/solo/multi-strip
NLA tracks and problematic transforms need manual preparation. Source meshes,
rigs, animation and scene units are preserved by export. Selection, active object
and frame are restored even after an exporter error.

Cura checks evaluated geometry for closed consistently oriented surfaces,
positive volume, one connected component and non-adjacent face intersections.
The current humanoid's separate parts are not a connected printable solid:
prepare a copy, bridge gaps and join/remesh it before exporting. Joining objects
alone does not weld or union their surfaces. Export remains disabled until those
checks pass. A closed Box can export immediately without materials.

STL coordinates are written in millimetres using scene unit scale. For example,
a 30 cm Box is 300 mm tall, not automatically miniature-sized. Resize the model
for your intended print. Cura still needs your printer, material, support and
slicing settings. Wall thickness, printer fit, support placement and all possible
self-intersection cases are not certified by this mesh check.

## Verification scope

Automated integration tests run in Blender 2.92.0 and 5.2.1 LTS. They
exercise UI operators, live export gating, material preparation, scene scoping,
FBX skin/animation/embedded texture data, GLB/glTF contents and STL dimensions.
Initial destination import results and remaining manual checks are recorded in
[Target verification](target-verification.md). The recorded manual Unity, Unreal and Cura checks used Blender 2.92 exports.
Modern Blender exports pass automated checks but still need destination review.
A nonempty exported file is not a guarantee of production readiness.

Destination references: [Godot scene import](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/index.html),
[Unreal FBX pipeline](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-content-pipeline),
and [Cura model formats](https://ultimaker.com/learn/ultimaker-cura-5-7-stable-release-notes/).
Unreal documents an FBX 2020.2 import pipeline; Blender 2.92 writes an older FBX
version. The recorded Unreal 5.8.2 basic import/playback succeeded, but broader
FBX compatibility and detailed target review remain release checks.
