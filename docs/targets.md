# Export files from Blender

No console commands are needed. In **Export** in the 3D Viewport sidebar (N), choose the model and its destination. Export Asset opens Blender's standard file browser when the latest explicit validation snapshot has no unresolved errors or warnings. Detailed results and Add Missing Materials live in the Validation sidebar tab. Export shows only a compact readiness indicator, export controls and the last saved path.

Panel headers show an attention icon for unresolved problems or a checkmark when the applicable checks pass. Rigging and Animations show problems relevant to their stage; Validation and Export summarize target requirements. Redraw-time status uses the cached validation snapshot so opening or redrawing the UI does not repeatedly rescan expensive geometry/animation state. Export execution still performs a fresh validation preflight before writing any file.

| Destination | Output | Included |
| --- | --- | --- |
| Godot | `.glb` by default; `.gltf` also allowed | Meshes, supported materials/textures, rig and generated animation library |
| Unity | `.fbx` | Meshes, basic materials, saved image textures, rig and generated animation stacks |
| Unreal Engine | main `.fbx` plus one `.fbx` sidecar per generated clip | Main skeletal model/material data plus destination-specific animation sidecars imported against the model skeleton |
| Cura | `.stl` | Evaluated current-pose printable geometry in millimetres; no rig, animation or materials |

## Blender steps

1. Build the current add-on with `python -m scripts.build_blender_addon`, install `dist/asset_assistant.zip`, and restart Blender if an older build was loaded.
2. Generate or choose the model. Add only the rigging/animation stages supported by that provider and asset use.
3. Open Export and choose the destination. For game assets, open Validation and click **Add Missing Materials** or assign your own. The helper adds neutral Principled materials only to missing assignments and supports Undo; it does not replace existing art.
4. Run **Validation** explicitly after target or asset changes. Resolve reported errors/warnings. Missing textures need actual image data; textured models need UVs. Generated Human textures are packed for self-contained export. Procedural shader/mapping graphs may still require baking for portable target use.
5. When **Export Asset** enables, click it, choose an existing directory and filename, then confirm. Export performs another fresh preflight after the file browser closes before writing.
6. Import through the destination application's normal UI. There is no custom destination connector to install.

Changing target, provider settings, geometry, material, rig, animation, or print-scale controls invalidates the stored readiness snapshot through supported Asset Assistant UI paths. Low-level direct Blender edits can make the snapshot stale, which is why actual export always revalidates current scene state. Existing output files are preserved; use a new filename when iterating. Separate glTF requires an appropriate directory for its binary/texture sidecars. An exporter failure can leave partial files for review.

## What happened to the warnings?

- **Materials** is actionable for game targets until every used face has an exportable material assignment.
- **Blockout** is an informational design note, not a claim of production anatomy quality.
- **Export Review** and destination review are reminders that successful serialization is not destination certification.
- Actual errors and warnings block export. They are never automatically converted to PASS.
- Validation stores a snapshot only when explicit validation runs; redraw-time UI readiness consumes that snapshot instead of performing expensive full inspection repeatedly.

## Target-specific preparation

Godot currently requires the supported scene/unit behavior described by its profile. The exporter does not silently reinterpret artistic dimensions beyond the target adapter's explicit conversion rules. Check physical dimensions in destination when scale matters.

Game export accepts the supported Principled/image-texture subset and preserves source meshes, rigs, animation and scene state where practical. Procedural shader graphs and advanced target-specific PBR behavior may require manual preparation. Existing artist NLA tracks, drivers, constraints and manual poses remain preservation boundaries rather than being silently rewritten.

### Godot

Godot uses GLB by default. Generated Idle/Walk clips can be packaged together through the generated animation-library workflow. Current Blender versions use Actions-based glTF animation export while legacy Blender uses the compatible temporary NLA organization. Verify Skeleton3D, skinning, texture and clip playback in destination.

### Unity

Unity uses FBX and can carry generated Idle/Walk together as separate animation stacks. The exporter stages only the intended generated actions and restores temporary action/NLA state afterward. Verify imported model/rig and clip availability; Humanoid retargeting is a separate certification dimension.

### Unreal Engine

Unreal uses a destination-specific bundle. Exporting `Human_Unreal.fbx` produces the main skeletal model file plus sidecars such as `Human_Unreal_Idle.fbx` and `Human_Unreal_Walk.fbx`.

Unreal Engine 5.8 Interchange did not reliably classify armature-only animation FBXs, so current sidecars retain the recognizable skinned mesh + armature hierarchy with exactly one active generated clip. Texture embedding is disabled for sidecars. Import the main FBX first, then import each sidecar with **Import Only Animations** against the skeleton created by the model import. This workflow has been manually verified with working Idle and Walk playback after generated clip-pose isolation.

### Cura

Cura export evaluates the current pose and runs print-specific preparation/validation before writing STL. Human 1.0 now has an automated print-preparation path rather than requiring artists to manually bridge the generated character solely to pass validation.

Cura print scale is explicit and affects only the STL derivative, not the Blender/game asset. Available presets include 1:1, 1:2, 1:5, 1:10, 1:20, 1:50 and 1:100. For example, a 180 cm Human exported at 1:10 is approximately 180 mm tall in the STL.

Validation checks the prepared printable result for important geometry conditions such as closed/oriented surfaces and print-path requirements. Cura still needs the user's printer, material, supports and slicing settings. Wall thickness, printer fit, support placement, all possible self-intersections and physical-print success are not certified by Asset Assistant.

## Verification scope

Automated integration tests run in Blender 2.92.0 and 5.2.1 LTS, plus standalone Python 3.9-3.12. Coverage exercises UI operators, snapshot-based export gating, fresh export preflight, material preparation, scene scoping, FBX/GLB animation packaging, texture behavior, Cura Human preparation/scale behavior and isolated packaged-add-on export paths.

Human 1.0 has completed manual destination evidence for Godot, Unity and Unreal. Cura has earlier Box slicing evidence plus automated Human preparation and scaling coverage; broader representative Human slicing/physical-print review remains separate certification work. See [Target verification](target-verification.md).

A nonempty exported file is not a guarantee of production readiness.

Destination references: [Godot scene import](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/index.html), [Unreal FBX pipeline](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-content-pipeline), and [Cura model formats](https://ultimaker.com/learn/ultimaker-cura-5-7-stable-release-notes/).
