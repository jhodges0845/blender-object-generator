# Target verification record

## Basic manual checks recorded September 2026

These are destination observations reported by the user and complemented by automated Blender tests; they do not imply broad production certification beyond the checks recorded here.

| Target | Application/version evidence | Asset and result | Broader follow-up |
| --- | --- | --- | --- |
| Godot | Current Human 1.0 verification screenshots show Godot 4.0.3 stable in the editor; earlier portable 4.0.3 installation was also verified | Completed Human 1.0 GLB imported with connected hierarchy, Skeleton3D, mesh, generated Human Base Texture and AnimationPlayer. Idle and Walk were validated through the generated animation library workflow, with working motion observed in destination. Upright orientation and gross skinning integrity were confirmed visually. | Exact destination scale and broader save/edit/reimport behavior remain useful certification work, not Human 1.0 blockers. |
| Unity | 2020.3.31f1 installed on the test machine; import-session version not independently captured | Completed Human 1.0 FBX import was exercised after the multi-clip export fix. The model/rig imported and Unity exposed both generated Idle and Walk clips from the exported animation library. | Humanoid avatar mapping/retargeting, exact measured scale and broader save/edit/reimport behavior remain useful certification follow-ups. |
| Unreal Engine | 5.8.2 verified from installed build and editor initialization log | Completed Human 1.0 Unreal workflow passed after the Interchange and clip-isolation fixes. The base skeletal model imported correctly; Idle and Walk sidecars imported against its skeleton and both animations played without the earlier cross-clip pose contamination. | Broader retargeting, measured scale and edit/reimport behavior remain certification follow-ups rather than Human 1.0 blockers. |
| Cura | 4.10.0 and 4.11.0 installed; version used in the original photo not established | Box STL from Blender 2.92 imported and sliced. Human Cura validation/repair and selectable print-scale behavior now have Blender regression coverage, including representative Human scaling. | Detailed representative Human slicing/dimension review and any physical print remain broader print-certification work. |

## Modern Blender verification

Blender 5.2.1 LTS is the primary modern runtime target. Automated integration coverage and an isolated ZIP smoke workflow exercise generation, rigging, animation, validation and the four export paths. CI also exercises Blender 2.92.0 and standalone Python 3.9-3.12.

Interactive Blender 5.2.1 testing confirmed the user-facing Human workflow through generation, deforming rig setup, generated UV/material/texture preparation, Idle/Walk creation and selection, validation and engine export. Destination testing exposed workflow gaps that were fixed before Human 1.0 closeout: generated Human textures are packed automatically, generated clips can be created from evaluated generated poses without tripping artist-pose protection, Godot/Unity can carry the generated clip library together, Unreal uses a destination-specific one-model-plus-animation-sidecars strategy, and generated clip actions are self-contained to prevent cross-clip pose contamination.

The Human 1.0 visual/deformation milestone was reviewed interactively in Blender 5.2.1 with the deformation inspection harness. Representative neck, shoulder, elbow, wrist, hip, knee, and ankle poses remained connected without obvious separation or catastrophic collapse. Shoulder/armpit and other low-poly joint transitions remain angular and are recorded as non-blocking foundation-quality limitations for 1.0.

## Human 1.0 Godot checkpoint — passed

A fresh completed Human generated with the current add-on was rigged, surfaced/textured, animated, validated and exported through the Godot GLB path in Blender 5.2.1.

Godot imported the connected hierarchy with `Skeleton3D`, the skinned mesh, generated Human Base Texture and `AnimationPlayer`. The Human remained upright and visually intact without obvious detached or collapsed geometry. Idle and Walk were both observed working in destination through the generated animation-library workflow.

This is sufficient to close the Human 1.0 Godot game-character gate. Exact measured destination scale and save/edit/reimport behavior remain broader certification checks.

## Human 1.0 Unity checkpoint — passed

The completed Human 1.0 passed the Unity animation-library gate after the exporter was changed to stage generated clips together for FBX export.

Manual destination testing initially exposed the old active-action limitation: Unity would show only whichever generated action was active at export time. After the multi-clip export change, both Idle and Walk were confirmed available in Unity. Automated Blender coverage verifies both generated clip names while preserving Blender action state and leaving no temporary NLA tracks behind.

This is sufficient for the current Human 1.0 game-character milestone. Humanoid-avatar retargeting, exact destination scale, importer-version capture and edit/reimport workflow remain broader certification dimensions.

## Human 1.0 Unreal checkpoint — passed

Unreal uses one animation per sidecar FBX. The current exporter writes a main Human FBX containing the model, skeleton, materials and texture payload, plus adjacent animation sidecars such as `Human_Unreal_Idle.fbx` and `Human_Unreal_Walk.fbx`.

Earlier armature-only sidecars were not recognized reliably by Unreal Engine 5.8 Interchange. The corrected sidecars retain the skinned mesh + armature hierarchy needed for Interchange classification while activating exactly one generated action and disabling texture embedding. They are imported with **Import Only Animations** against the skeleton created by the main model FBX, which avoids creating duplicate destination render assets.

Manual destination verification confirmed that the base skeletal model imports and both Idle and Walk sidecars import and play against its skeleton. A later clip-isolation fix made generated actions self-contained so Idle no longer inherited locomotion pose state from Walk. The corrected workflow was revalidated successfully.

This closes the Unreal gate for Human Provider 1.0.

## Cura checkpoint

The original Box sample was generated with Blender 2.92 at 2 x 3 x 4 cm. Reading the binary STL confirmed 12 triangles and extents of exactly 20 x 30 x 40 mm, and Cura imported/sliced the sample.

Human 1.0 subsequently exposed print-specific geometry validation issues. The current Cura path now performs the required Human print preparation and has automated regression coverage for the generated/evaluated Human path. Print scale is explicitly selectable without changing the source/game asset; for example, a 180 cm Human at 1:10 exports at approximately 180 mm tall.

Detailed representative Human slicing, orientation/warning review and any physical print remain broader Cura certification work. They are not blockers for beginning Dog/quadruped development.

## Human 1.0 game-target review — complete

The Blender visual/deformation gate and the Godot, Unity and Unreal destination gates are complete. This is enough evidence to close Human Provider 1.0 as an editable game-character foundation and move the architecture to its next real provider proof.

A successful Blender file write still does not imply broad production certification. Measured scale, retargeting, destination editing/reimport, physical printing and more exhaustive destination/version coverage remain separate follow-up dimensions.

## Repeatable review checklist

Record the repository commit, add-on version, Blender version, destination version, provider parameters, exporter/importer settings, generated animation set and results for each run. Mark each check as pass, fail or not tested; attach relevant screenshots or error messages.

1. Follow [the Blender export steps](targets.md#blender-steps). Generate the provider, add only provider-supported rigging/animation, prepare required surface data, and run explicit validation before export.
2. Confirm validation has no unresolved errors/warnings and record the export result. File creation alone is not destination certification.
3. Import through the destination's normal UI into a clean test project or scene. Record all importer warnings and any nondefault settings.
4. For game targets, inspect hierarchy, connected mesh, orientation, measured scale, skeleton, skinning and material/texture appearance. Play and scrub exported animations throughout their ranges.
5. Verify animation packaging according to destination: Godot/Unity should expose the generated clip library from their exported asset, while Unreal should import the model first and then one sidecar per generated clip with **Import Only Animations** against the model skeleton.
6. In Unity, record Generic/Humanoid avatar behavior separately if retargeting is attempted.
7. In Unreal, verify sidecars are assigned to the model skeleton and do not create duplicate destination render assets.
8. In Cura, confirm displayed dimensions, bed placement, orientation, full layer review and warnings. Keep physical printing separate from slicing.
9. Save the destination project and record any editing/reimport checks performed. Convert reproducible exporter defects into regression tests where practical.

Basic import success does not complete broad target certification. Texture transfer, measured scale, importer behavior, edit/reimport workflow, retargeting and destination-specific deformation remain useful review dimensions even when a narrower provider milestone gate is complete.
