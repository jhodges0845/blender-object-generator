# Target verification record

## Basic manual checks recorded September 2026

These are destination observations reported by the user and complemented by automated Blender tests; they do not imply broad production certification beyond the checks recorded here.

| Target | Application/version evidence | Asset and result | Still to verify |
| --- | --- | --- | --- |
| Godot | Current Human 1.0 verification screenshots show Godot 4.0.3 stable in the editor; earlier portable 4.0.3 installation was also verified | Completed Human 1.0 GLB imported with connected hierarchy, Skeleton3D, mesh, generated Human Base Texture and AnimationPlayer. Idle and Walk were both validated through the generated animation library workflow, with working motion observed in destination. Upright orientation and gross skinning integrity were confirmed visually. | Broader certification can still measure exact destination scale and exercise save/edit/reimport behavior; these are not blockers for the Human 1.0 game-character milestone. |
| Unity | 2020.3.31f1 installed on the test machine; import-session version not independently captured | Completed Human 1.0 FBX import was exercised after the multi-clip export fix. The model/rig imported and Unity exposed both generated Idle and Walk clips from the exported animation library. | Humanoid avatar mapping/retargeting, exact measured scale and broader save/edit/reimport behavior remain useful certification follow-ups rather than Human 1.0 blockers. |
| Unreal Engine | 5.8.2 verified from installed build and editor initialization log | Unreal export now produces one model/skeleton/material FBX plus one armature-only FBX per generated clip. Automated Blender coverage verifies the sidecars contain FBX animation structures and exclude mesh/material/texture payloads. | Run one final destination import: import the model first, then Idle and Walk sidecars against the created skeleton and confirm both sequences play correctly. |
| Cura | 4.10.0 and 4.11.0 installed; version used in photo not established | Box STL from Blender 2.92 imported and sliced; photo shows continuous walls and a filled top in layer preview | Confirm Cura version and displayed 20 x 30 x 40 mm dimensions, orientation, full layer review and warnings; no physical print performed |

## Modern Blender verification

Blender 5.2.1 LTS is the primary modern runtime target. Automated integration coverage and an isolated ZIP smoke workflow exercise generation, rigging, animation, validation and the four export paths. Remote GitHub Actions has also completed successfully with the modern/legacy Blender matrix.

Interactive Blender 5.2.1 testing confirmed the user-facing Human workflow through generation, deforming rig setup, generated UV/material/texture preparation, Idle/Walk creation and selection, validation and engine export. Destination testing exposed workflow gaps that were fixed before continuing: generated Human textures are packed automatically, generated clips can be created from evaluated generated poses without tripping artist-pose protection, Godot/Unity can carry the generated clip library together, and Unreal uses a destination-specific one-model-plus-animation-sidecars packaging strategy. The safety boundary for artist actions, NLA, drivers, constraints and manual poses remains intact.

The Human 1.0 visual/deformation milestone was reviewed interactively in Blender 5.2.1 with the deformation inspection harness. Representative neck, shoulder, elbow, wrist, hip, knee, and ankle poses remained connected without obvious separation or catastrophic collapse. Shoulder/armpit and other low-poly joint transitions remain angular and are recorded as non-blocking foundation-quality limitations for 1.0.

The older Unity and Unreal samples were generated with Blender 2.92 using the repository's respective target adapters, with a basic humanoid rig, generated idle and neutral materials. Those historical checks remain useful smoke evidence, but the current Human 1.0 evidence is now based on the completed connected/deforming provider and the newer animation-export architecture described below.

The Cura sample was generated with Blender 2.92 using the Box provider at 2 x 3 x 4 cm and the Cura adapter. Export validation passed. Reading the binary STL confirmed 12 triangles and extents of exactly 20 x 30 x 40 mm. This verifies the file coordinates, not Cura's displayed dimensions or physical print accuracy. Human 1.0 print certification is not part of the current game-character milestone.

## Human 1.0 Godot checkpoint

The completed Human 1.0 has passed the current Godot destination gate. A fresh Human generated with the current add-on was rigged, surfaced/textured, animated, validated and exported through the Godot GLB path in Blender 5.2.1.

Godot imported the connected hierarchy with `Skeleton3D`, the skinned mesh, generated Human Base Texture and `AnimationPlayer`. The Human remained upright and visually intact without obvious detached or collapsed geometry. The generated texture asset was present in the Godot project.

Idle and Walk were both observed and validated in destination during the animation-export debugging sequence. The current exporter can package the generated clip library together rather than relying on a one-active-clip limitation. The earlier separate-export checks remain useful motion evidence: Idle was about 4 seconds, Walk about 1.2 seconds, and the viewport showed the expected opposing-leg in-place walk pose.

This checkpoint is sufficient to close the Human 1.0 Godot game-character gate. Exact measured destination scale and save/edit/reimport behavior remain useful broader certification checks but are not treated as blockers for this milestone.

## Human 1.0 Unity checkpoint

The completed Human 1.0 has also passed the current Unity animation-library gate after the exporter was changed to stage generated clips together for FBX export.

Manual destination testing initially exposed the old active-action limitation: Unity would show only whichever generated action was active at export time. After the multi-clip export change, the user confirmed that both Idle and Walk were available in Unity. Automated Blender coverage now verifies that a Unity-target FBX contains both generated clip names while preserving the previously active Blender action and leaving no temporary NLA tracks behind.

This is sufficient for the current Human 1.0 game-character milestone. Humanoid-avatar retargeting, exact destination scale, importer-version capture and edit/reimport workflow remain broader certification dimensions rather than blockers.

## Human 1.0 Unreal checkpoint

Unreal uses a different packaging strategy because its skeletal-animation import workflow is more reliable with one animation per FBX. The current exporter writes a main Human FBX containing the model, skeleton, materials and texture payload, plus adjacent animation sidecars such as `Human_Unreal_Idle.fbx` and `Human_Unreal_Walk.fbx`.

Each animation sidecar contains only the shared armature and one generated action. Mesh, material and texture payloads are intentionally excluded so importing additional animations does not duplicate render assets or create `.fbm` texture sidecars. Automated Blender regression coverage verifies that each generated sidecar contains FBX animation structures and excludes the generated mesh/material/texture payload while preserving the original Blender selection, action and playback state.

The remaining Human 1.0 Unreal gate is intentionally narrow: import the main FBX first to create the skeletal mesh and skeleton, then import the Idle and Walk sidecars as animation-only assets against that skeleton and confirm that both animation sequences play correctly. Once that check passes, Unreal no longer blocks Human Provider 1.0 closeout.

## Human 1.0 game-target review

The Blender visual/deformation gate, Godot destination gate and Unity generated-animation gate are complete. Unreal's corrected bundle has automated coverage and needs one final destination playback confirmation.

For the final Unreal run, use the connected/deforming Human provider with representative default parameters, generate the model, add the deforming rig, prepare the generated material/texture, and generate both Idle and Walk. Export once to the Unreal target. The output should include the model FBX plus one sidecar for each generated clip; do not expect Unity/Godot-style multi-clip packaging for Unreal.

## Repeatable review checklist

Record the repository commit, add-on version, Blender version, destination version, Human parameters, exporter/importer settings, generated animation set and results for each run. Mark each check as pass, fail or not tested; attach relevant screenshots or error messages.

1. Follow [the Blender export steps](targets.md#blender-steps). For Human 1.0 game targets, generate the connected/deforming Human, add its rig, prepare the generated material/texture, and generate both Idle and Walk. For Cura regression evidence, continue using a Box with width 2 cm, depth 3 cm and height 4 cm; export as STL.
2. Confirm validation has no unresolved errors/warnings and record the export result. File creation alone is not destination certification.
3. Import through the destination's normal UI into a clean test project or scene. Record all importer warnings and any nondefault settings.
4. For game targets, inspect hierarchy, full connected mesh, upright orientation, measured scale, skeleton, skinning and material/texture appearance. Play and scrub the exported animations throughout their ranges; check for detached geometry, collapsed joints, unexpected motion or lost texture/UV data.
5. Verify animation packaging according to destination: Godot/Unity should expose the generated clip library from their exported asset, while Unreal should import the model first and then one animation-only FBX sidecar per generated clip. Verify actual motion and duration rather than relying only on labels.
6. In Unity, first test Generic animation with the imported skeleton. Record Humanoid avatar mapping and retargeting as separate checks if attempted.
7. In Unreal, verify the Idle and Walk sidecars are assigned to the skeleton created by the model FBX and do not create duplicate skeletal meshes/materials/textures.
8. In Cura, confirm displayed dimensions of 20 x 30 x 40 mm, bed placement and orientation. Record printer/profile settings, slice, inspect layers throughout the height and record warnings. Keep physical printing separate from slicing.
9. Save the destination project and record any editing/reimport checks performed. Convert reproducible exporter defects into regression tests where practical.

Basic import success does not complete broad target certification. Texture transfer, measured scale, importer behavior, edit/reimport workflow, retargeting and destination-specific deformation remain useful review dimensions even when a narrower milestone gate is complete.
