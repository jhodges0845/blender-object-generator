# Workflow and asset readiness

Version 0.8 provides five tabs within the Generator sidebar panel. Generation,
rigging, animation, and validation are separate actions on one chosen character.

| Tab | Current behavior |
| --- | --- |
| Model | Choose Humanoid for a character or Box for a static prop; each has its own inputs. |
| Rigging | Add the 16-bone rigid rig to that character, then use Enter Pose Mode. Existing rigs are preserved. |
| Animation | Generate an editable looping idle on a fresh rig and preview playback. See [animation](animation.md). |
| Validation | Run target-specific checks for the selected intended use and texture requirements. |
| Export | Choose the destination, prepare missing materials, resolve the live checklist and export through the file browser. |

The Object field identifies which generated object Rigging, Animation and Validation
will operate on. It is set automatically after generation. Choose another root
in that field to work on an older character. When the field is empty, a selected
part or rig can identify its generated parent. New measurements affect only the
next generated model; rigging uses the character's saved generation dimensions.

Rigging preserves the mesh objects and existing edits. Its joint locations are
based on the original proportions, so substantial artist edits may require
manual bone adjustment. Automatic rigging refuses to overwrite an existing rig,
conflicting bone groups, missing/renamed parts, or edited per-part transforms.
Moving the common parent is supported. Version 0.5 records the original unit
conversion; older unrigged characters without that metadata use the current
scene unit scale. Restore the original scale before rigging those older files.

## What an asset needs

A static prop does not need bones or animation. A poseable character needs a
skeleton and skin weights. An animated character also needs animation clips.
All need suitable geometry, scale, appearance, and a tested export for the
intended game engine. No single checklist guarantees quality across every engine.

A material defines surface appearance. Image textures supply details such as
color or roughness; UV maps place those images on the surface. A simple flat-color
material can be sufficient for a stylized model, so image textures are optional.
For a textured character, plan UV unwrapping, image creation or baking, and
packing/copying the images for delivery. Normal, roughness, metallic, and other
maps are used as the art style and engine require; every model does not need
every type of map. Blender procedural materials may need baking for export.

Add Missing Materials creates neutral Principled materials for faces without assignments.
Existing materials are preserved. UV maps and image texture authoring/baking are
still manual. Cura STL does not require materials, UVs, rigs or animation.

## Validation options and scope

Choose Static Asset, Rigged Asset, or Animated Asset. Enable Image Textures
Expected only when your intended appearance requires image maps.

- Geometry: checks mesh presence, finite coordinates, nonzero face area, and
  edge usage consistent with closed individual parts. It does not detect all
  self-intersections, flipped normals, bad shading, or poor topology.
- Rigging: checks armature/bone presence, enabled armature modifiers, and
  vertices with positive weights in deform-bone groups. It does not certify
  weight normalization, joint anatomy, or deformation quality.
- Animation: checks changing unmuted curves in actions or unmuted NLA strips,
  missing targets, non-finite values, Rest Position and zero action influence.
  It does not certify evaluated motion under arbitrary constraints, NLA blending,
  loop quality, or export. Static props do not require animation or a rig.
- Materials: missing game-material assignments are errors. Use Add Missing Materials
  or author suitable materials before export. Procedural shaders require baking.
- Textures: checks connected image nodes in assigned materials and linked node
  groups. Missing image assignments or external files are errors. Packed images
  are accepted. Generated, unpacked images and movie/sequence images need review.
  UDIM filenames using the <UDIM> token are checked against listed tiles.
- UVs: checks for an active layer with finite coordinates when image textures
  are expected or found. It does not judge UV overlap, island area, seams, or
  texel density. Non-UV projection workflows still need an export-specific review.
- Transforms: flags unapplied per-mesh scale for review.

Connected image-node detection is conservative: it is not a full shader graph
evaluation, and connected nodes on unused shader branches may also be reported.
Actual multipart blockouts and target import review have informational notes.
These notes are separate from actionable warnings and do not claim verification. Separate closed parts are expected in this prototype; they do not mean
the character is a single welded surface suitable for smooth skinning.

Validation-tab results are snapshots. The Export tab evaluates current readiness
and blocks export on unresolved errors or warnings; the operator rechecks at execution.
[Export workflow](targets.md) explains formats and preparation. Validation snapshots
are not permission to export after later edits. Changing the target or requirements clears them; rerun
validation after geometry, rig, material, image, or animation edits. The validator
does not silently repair files or label the current blockout production-ready.

## Remaining roadmap

1. UV authoring and optional image textures/baking beyond neutral materials.
2. Mesh topology and blended weights for smoother joints where needed.
3. Destination-application import testing and project-specific art-budget checks.

Polygon budgets, texture resolution/color space, bone conventions, and clip
requirements must be decided for the target project rather than guessed globally.
