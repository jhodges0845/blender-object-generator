# Target verification record

## Basic manual checks recorded September 2026

These are initial import checks, not production certification. Destination observations were reported by the user; the Cura result also has a user-supplied layer-preview photo. Automated Blender tests complement these observations but do not replace destination review.

| Target | Application/version evidence | Asset and result | Still to verify |
| --- | --- | --- | --- |
| Godot | Portable 4.0.3 was found and its version verified; exact version for the latest import session was not recorded | Earlier generated humanoid GLB showed hierarchy, rig and animation. A later interactive Blender 5.2.1 run completed the Asset Assistant workflow, exported GLB successfully, imported into Godot, and animation playback was confirmed | Record exact Godot version for a formal pass; inspect skinning, materials/textures, orientation, measured scale and scene/edit workflow |
| Unity | 2020.3.31f1 installed on the test machine; import-session version not independently captured | Unity-target humanoid FBX from Blender 2.92; user confirmed model/idle test worked after Generic-rig preview instructions | Confirm importer settings/version; inspect hierarchy, skinning, scale, axes and materials; Humanoid avatar mapping/retargeting not tested |
| Unreal Engine | 5.8.2 verified from installed build and editor initialization log | Unreal-target humanoid FBX from Blender 2.92; user confirmed model and animation worked | Detailed skeleton, deformation, materials/textures, axes, scale and broader FBX compatibility; editor performance was poor on the test machine |
| Cura | 4.10.0 and 4.11.0 installed; version used in photo not established | Box STL from Blender 2.92 imported and sliced; photo shows continuous walls and a filled top in layer preview | Confirm Cura version and displayed 20 x 30 x 40 mm dimensions, orientation, full layer review and warnings; no physical print performed |

## Modern Blender verification

Blender 5.2.1 LTS is the primary modern runtime target. Automated integration coverage and an isolated ZIP smoke workflow exercise generation, rigging, animation, validation and the four export paths. Remote GitHub Actions has also completed successfully with the modern/legacy Blender matrix.

An interactive Blender 5.2.1 session has now additionally confirmed the user-facing workflow through successful GLB export. That GLB was imported into Godot and its animation was confirmed working. This closes the previous gap where modern Blender had only headless/package evidence, but it does not establish full Godot visual, scale, material or deformation certification.

The older Unity and Unreal samples were generated with Blender 2.92 using the repository's respective target adapters, with a basic humanoid rig, generated idle and neutral materials. Export validation passed. Image textures were not included, so those checks provide no texture-fidelity evidence. The humanoid remains a multipart blockout; these results do not establish production character deformation quality.

The Cura sample was generated with Blender 2.92 using the Box provider at 2 x 3 x 4 cm and the Cura adapter. Export validation passed. Reading the binary STL confirmed 12 triangles and extents of exactly 20 x 30 x 40 mm. This verifies the file coordinates, not Cura's displayed dimensions or physical print accuracy. The disconnected humanoid was not used as a printable sample.

## Repeatable review checklist

Record the repository commit, add-on version, Blender version, destination version, asset parameters, exporter/importer settings and results for each run. Mark each check as pass, fail or not tested; attach relevant screenshots or error messages.

1. Follow [the Blender export steps](targets.md#blender-steps). For game targets, generate a humanoid, add its basic rig and idle, prepare missing materials and select Animated Asset. Export with that destination's adapter. For Cura, use a Box with width 2 cm, depth 3 cm and height 4 cm; export as STL.
2. Confirm validation has no unresolved errors/warnings and record the export result.
3. Import through the destination's normal UI into a clean test project or scene. Record all importer warnings and any nondefault settings.
4. For game targets, inspect the hierarchy and all mesh parts, upright orientation, measured scale, skeleton and skin weights. Play and scrub the idle throughout its range; check for detached parts or unexpected motion. Record material appearance separately. Use a textured sample for texture/UV verification.
5. In Unity, first test Generic animation with the imported skeleton. Record Humanoid avatar mapping and retargeting as separate checks if attempted.
6. In Cura, confirm displayed dimensions of 20 x 30 x 40 mm, bed placement and orientation. Record printer/profile settings, slice, inspect layers throughout the height and record warnings. Keep physical printing separate from slicing.
7. Save the destination project and record any editing/reimport checks performed. Convert reproducible exporter defects into regression tests where practical.

Basic import success does not complete all target-review checks. Detailed visual review, texture transfer, deformation quality and physical printing remain separate work.