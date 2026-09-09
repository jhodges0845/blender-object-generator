# Target verification record

## Basic manual checks recorded September 2026

These are destination observations reported by the user and complemented by automated Blender tests; they do not imply broad production certification beyond the checks recorded here.

| Target | Application/version evidence | Asset and result | Still to verify |
| --- | --- | --- | --- |
| Godot | Current Human 1.0 verification screenshots show Godot 4.0.3 stable in the editor; earlier portable 4.0.3 installation was also verified | Completed Human 1.0 GLB imported with connected hierarchy, Skeleton3D, mesh, generated Human Base Texture and AnimationPlayer. Idle exported/imported as the sole active clip at about 4.0 s. Walk exported/imported separately as the sole active clip at about 1.2 s and visibly produced the expected in-place walking pose. Upright orientation and gross skinning integrity were confirmed visually. | Broader certification can still measure exact destination scale and exercise save/edit/reimport behavior; these are not blockers for the Human 1.0 game-character milestone. |
| Unity | 2020.3.31f1 installed on the test machine; import-session version not independently captured | Unity-target humanoid FBX from Blender 2.92; user confirmed model/idle test worked after Generic-rig preview instructions | Re-run with completed Human 1.0; confirm importer settings/version, hierarchy, skinning, scale, axes, materials/textures and active clip; Humanoid avatar mapping/retargeting remains separate |
| Unreal Engine | 5.8.2 verified from installed build and editor initialization log | Unreal-target humanoid FBX from Blender 2.92; user confirmed model and animation worked | Re-run with completed Human 1.0; inspect skeleton/deformation, materials/textures, axes, scale, active clip and broader FBX compatibility; editor performance was poor on the test machine |
| Cura | 4.10.0 and 4.11.0 installed; version used in photo not established | Box STL from Blender 2.92 imported and sliced; photo shows continuous walls and a filled top in layer preview | Confirm Cura version and displayed 20 x 30 x 40 mm dimensions, orientation, full layer review and warnings; no physical print performed |

## Modern Blender verification

Blender 5.2.1 LTS is the primary modern runtime target. Automated integration coverage and an isolated ZIP smoke workflow exercise generation, rigging, animation, validation and the four export paths. Remote GitHub Actions has also completed successfully with the modern/legacy Blender matrix.

Interactive Blender 5.2.1 testing confirmed the user-facing Human workflow through generation, deforming rig setup, generated UV/material/texture preparation, Idle/Walk creation and selection, validation and GLB export. Destination testing exposed two workflow gaps that were fixed before continuing: generated Human textures are now packed automatically for self-contained export, and an evaluated Asset Assistant-generated clip no longer causes the artist-pose safety check to reject creation of another generated clip. The safety boundary for artist actions, NLA, drivers, constraints and manual poses remains intact.

The Human 1.0 visual/deformation milestone was reviewed interactively in Blender 5.2.1 with the deformation inspection harness. Representative neck, shoulder, elbow, wrist, hip, knee, and ankle poses remained connected without obvious separation or catastrophic collapse. Shoulder/armpit and other low-poly joint transitions remain angular and are recorded as non-blocking foundation-quality limitations for 1.0.

The older Unity and Unreal samples were generated with Blender 2.92 using the repository's respective target adapters, with a basic humanoid rig, generated idle and neutral materials. Export validation passed. Image textures were not included, so those checks provide no texture-fidelity evidence. Those historical results are useful smoke evidence but do not certify the completed connected/deforming Human 1.0 provider.

The Cura sample was generated with Blender 2.92 using the Box provider at 2 x 3 x 4 cm and the Cura adapter. Export validation passed. Reading the binary STL confirmed 12 triangles and extents of exactly 20 x 30 x 40 mm. This verifies the file coordinates, not Cura's displayed dimensions or physical print accuracy. Human 1.0 print certification is not part of the current game-character milestone.

## Human 1.0 Godot checkpoint

The completed Human 1.0 has now passed the current Godot destination gate. A fresh Human generated with the current add-on was rigged, surfaced/textured, animated, validated and exported through the Godot GLB path in Blender 5.2.1.

Godot imported the connected hierarchy with `Skeleton3D`, the skinned mesh, generated Human Base Texture and `AnimationPlayer`. The Human remained upright and visually intact without obvious detached or collapsed geometry. The generated texture asset was present in the Godot project.

Clip-selection behavior was verified explicitly rather than inferred from animation names. With Idle active, the imported GLB contained one animation of about 4 seconds with bone tracks. With Walk active, a separate GLB contained one animation of about 1.2 seconds; the viewport showed the expected opposing-leg in-place walk pose and corresponding torso/arm/leg tracks. This matches the intentional design: Blender retains separate editable generated actions, while each destination export carries only the selected active clip.

This checkpoint is sufficient to close the Human 1.0 Godot game-character gate. Exact measured destination scale and save/edit/reimport behavior remain useful broader certification checks but are not treated as blockers for this milestone. Unity and Unreal remain the outstanding Human 1.0 destinations.

## Human 1.0 game-target review

The Blender visual/deformation gate and Godot destination gate are complete. Unity and Unreal verification should use the same completed Human 1.0 provider rather than the legacy multipart humanoid path.

For each remaining game target, use the connected/deforming Human provider with representative default parameters, generate the model, add the deforming rig, prepare the generated material/texture, generate both Idle and Walk, and explicitly select the clip being exported. Record which clip was active. Export one clip at a time; inactive generated actions should remain editable in the `.blend` file without silently joining the destination export.

Unity is next. After Unity succeeds, repeat the corresponding FBX verification in Unreal. Unreal should be tested last because it places the heaviest load on the available test machine.

## Repeatable review checklist

Record the repository commit, add-on version, Blender version, destination version, Human parameters, exporter/importer settings, selected animation clip and results for each run. Mark each check as pass, fail or not tested; attach relevant screenshots or error messages.

1. Follow [the Blender export steps](targets.md#blender-steps). For Human 1.0 game targets, generate the connected/deforming Human, add its rig, prepare the generated material/texture, generate both Idle and Walk, and select the clip intended for export. For Cura regression evidence, continue using a Box with width 2 cm, depth 3 cm and height 4 cm; export as STL.
2. Confirm validation has no unresolved errors/warnings and record the export result. File creation alone is not destination certification.
3. Import through the destination's normal UI into a clean test project or scene. Record all importer warnings and any nondefault settings.
4. For game targets, inspect hierarchy, full connected mesh, upright orientation, measured scale, skeleton, skinning and material/texture appearance. Play and scrub the exported clip throughout its range; check for detached geometry, collapsed joints, unexpected motion or lost texture/UV data.
5. Verify clip selection explicitly: export/import Idle and Walk separately when practical and confirm the destination receives the intended motion rather than every stored generated action. Destination animation naming may differ by exporter/version; verify the actual motion and duration rather than relying only on a label.
6. In Unity, first test Generic animation with the imported skeleton. Record Humanoid avatar mapping and retargeting as separate checks if attempted.
7. In Cura, confirm displayed dimensions of 20 x 30 x 40 mm, bed placement and orientation. Record printer/profile settings, slice, inspect layers throughout the height and record warnings. Keep physical printing separate from slicing.
8. Save the destination project and record any editing/reimport checks performed. Convert reproducible exporter defects into regression tests where practical.

Basic import success does not complete broad target certification. Texture transfer, measured scale, importer behavior, edit/reimport workflow, and destination-specific deformation remain useful review dimensions even when a narrower milestone gate is complete.
