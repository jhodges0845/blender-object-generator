# Target verification record

## Basic manual checks recorded September 2026

These are initial import checks, not production certification. Destination observations were reported by the user; the Cura result also has a user-supplied layer-preview photo. Automated Blender tests complement these observations but do not replace destination review.

| Target | Application/version evidence | Asset and result | Still to verify |
| --- | --- | --- | --- |
| Godot | Portable 4.0.3 was found and its version verified; exact version for the latest import session was not recorded | Earlier generated humanoid GLB showed hierarchy, rig and animation. A later interactive Blender 5.2.1 run completed the Asset Assistant workflow, exported GLB successfully, imported into Godot, and animation playback was confirmed | Record exact Godot version for a formal pass; inspect Human 1.0 skinning, materials/textures, orientation, measured scale, active clip and scene/edit workflow |
| Unity | 2020.3.31f1 installed on the test machine; import-session version not independently captured | Unity-target humanoid FBX from Blender 2.92; user confirmed model/idle test worked after Generic-rig preview instructions | Re-run with completed Human 1.0; confirm importer settings/version, hierarchy, skinning, scale, axes, materials/textures and active clip; Humanoid avatar mapping/retargeting remains separate |
| Unreal Engine | 5.8.2 verified from installed build and editor initialization log | Unreal-target humanoid FBX from Blender 2.92; user confirmed model and animation worked | Re-run with completed Human 1.0; inspect skeleton/deformation, materials/textures, axes, scale, active clip and broader FBX compatibility; editor performance was poor on the test machine |
| Cura | 4.10.0 and 4.11.0 installed; version used in photo not established | Box STL from Blender 2.92 imported and sliced; photo shows continuous walls and a filled top in layer preview | Confirm Cura version and displayed 20 x 30 x 40 mm dimensions, orientation, full layer review and warnings; no physical print performed |

## Modern Blender verification

Blender 5.2.1 LTS is the primary modern runtime target. Automated integration coverage and an isolated ZIP smoke workflow exercise generation, rigging, animation, validation and the four export paths. Remote GitHub Actions has also completed successfully with the modern/legacy Blender matrix.

An interactive Blender 5.2.1 session has now additionally confirmed the user-facing workflow through successful GLB export. That GLB was imported into Godot and its animation was confirmed working. This closes the previous gap where modern Blender had only headless/package evidence, but it does not establish full Human 1.0 visual, scale, material or deformation certification.

The older Unity and Unreal samples were generated with Blender 2.92 using the repository's respective target adapters, with a basic humanoid rig, generated idle and neutral materials. Export validation passed. Image textures were not included, so those checks provide no texture-fidelity evidence. Those historical results are useful smoke evidence but do not certify the completed connected/deforming Human 1.0 provider.

The Cura sample was generated with Blender 2.92 using the Box provider at 2 x 3 x 4 cm and the Cura adapter. Export validation passed. Reading the binary STL confirmed 12 triangles and extents of exactly 20 x 30 x 40 mm. This verifies the file coordinates, not Cura's displayed dimensions or physical print accuracy. Human 1.0 print certification is not part of the current game-character milestone.

## Human 1.0 game-target review

Keep the visual/deformation pass as a separate open gate until it can be performed interactively in Blender. The engine verification should use the completed Human 1.0 provider rather than the legacy multipart humanoid path.

For each game target, use the connected/deforming Human provider with representative default parameters, generate the model, add the deforming rig, prepare the generated material/texture, generate both Idle and Walk, and explicitly select the clip being exported. Record which clip was active. Export one clip at a time; inactive generated actions should remain editable in the `.blend` file without silently joining the destination export.

Godot is the first formal Human 1.0 destination pass because GLB is the portable primary path. After Godot succeeds, repeat the corresponding FBX verification in Unity and Unreal. Unreal should be tested last because it places the heaviest load on the available test machine.

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

Basic import success does not complete all target-review checks. Detailed visual review, texture transfer, deformation quality and physical printing remain separate work.
