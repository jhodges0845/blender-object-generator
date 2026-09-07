# Target verification record

## Basic manual checks recorded September 2026

These are initial import checks, not production certification. Destination observations
were reported by the user; the Cura result also has a user-supplied layer-preview
photo. No automated destination-engine test was run for these observations.

| Target | Application/version evidence | Asset and result | Still to verify |
| --- | --- | --- | --- |
| Godot | Portable 4.0.3 was found and its version verified; the earlier import session version was not recorded | Earlier user-confirmed generated humanoid GLB import showed model hierarchy, rig and animation | Repeat with recorded version; playback, skinning, materials/textures, orientation, scale and scene editing |
| Unity | 2020.3.31f1 installed on the test machine; import-session version not independently captured | Unity-target humanoid FBX; user confirmed model/idle test worked after receiving Generic-rig preview instructions | Confirm importer settings/version; inspect hierarchy, skinning, scale, axes and materials; Humanoid avatar mapping/retargeting not tested |
| Unreal Engine | 5.8.2 verified from installed build and editor initialization log | Unreal-target humanoid FBX; user confirmed model and animation worked | Detailed skeleton, deformation, materials/textures, axes, scale and broader FBX compatibility; editor performance was poor on the test machine |
| Cura | 4.10.0 and 4.11.0 installed; version used in photo not established | Box STL imported and sliced; photo shows continuous walls and a filled top in layer preview | Confirm Cura version and displayed 20 x 30 x 40 mm dimensions, orientation, full layer review and any warnings; no physical print performed |

The Unity and Unreal samples were generated with Blender 2.92 using the repository's
respective target adapters, with a basic humanoid rig, generated idle and neutral
materials. Export validation passed. Image textures were not included, so these
checks provide no texture-fidelity evidence. The humanoid remains a multipart
blockout; this result does not establish production character deformation quality.

The Cura sample was generated with Blender 2.92 using the Box provider at 2 x 3 x
4 cm and the Cura adapter. Export validation passed. Reading the binary STL
confirmed 12 triangles and extents of exactly 20 x 30 x 40 mm. This verifies the
file's coordinates, not Cura's displayed dimensions or physical print accuracy.
The disconnected humanoid was not used as a printable sample.

Local sample scripts, source blend files, exports and export reports were stored
under ignored `artifacts/unity-import-check`, `artifacts/unreal-import-check` and
`artifacts/cura-import-check`. They are not distributed with this documentation PR.
Use the procedure below to generate fresh samples from the current add-on.

## Repeatable review checklist

Record the repository commit, add-on version, Blender version, destination version,
asset parameters, exporter/importer settings and results for each run. Mark each
check as pass, fail or not tested; attach relevant screenshots or error messages.

1. Follow [the Blender export steps](targets.md#blender-steps). For game targets,
   generate a humanoid, add its basic rig and idle, prepare missing materials and
   select Animated Asset. Export with that destination's adapter. For Cura, use
   a Box with width 2 cm, depth 3 cm and height 4 cm; export as STL.
2. Confirm validation has no unresolved errors/warnings and record the export result.
3. Import through the destination's normal UI into a clean test project or scene.
   Record all importer warnings and any nondefault settings.
4. For game targets, inspect the hierarchy and all mesh parts, upright orientation,
   measured scale, skeleton and skin weights. Play and scrub the idle throughout
   its range; check for detached parts or unexpected motion. Record material
   appearance separately. Use a textured sample for texture/UV verification.
5. In Unity, first test Generic animation with the imported skeleton. Record
   Humanoid avatar mapping and retargeting as separate checks if attempted.
6. In Cura, confirm displayed dimensions of 20 x 30 x 40 mm, bed placement and
   orientation. Record printer/profile settings, slice, inspect layers throughout
   the height and record warnings. Keep physical printing separate from slicing.
7. Save the destination project and record any editing/reimport checks performed.
   Convert reproducible exporter defects into regression tests where practical.

Basic import success does not complete all target-review checks. Modern Blender
add-on compatibility, detailed visual review, texture transfer and physical printing
remain separate work. Installing and launching newer Blender alone does not verify
this add-on on it.
