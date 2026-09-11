# Workflow and asset readiness

Asset Assistant exposes five vertical sidebar tabs: Generator, Rigging, Animations, Validation and Export. Generation, rigging, animation, and validation are separate actions on one chosen asset.

| Tab | Current behavior |
| --- | --- |
| Generator | Choose Human, Quadruped, or Box and generate an editable starting asset. |
| Rigging | Add the selected provider's supported rig without replacing an existing rig. |
| Animations | Generate/select supported clips such as Idle, Walk, and Run. See [animation](animation.md). |
| Validation | Run target-specific checks for the selected intended use and texture requirements. |
| Export | Choose the destination, prepare missing materials where appropriate, resolve the checklist and export through the file browser. |

The Object field identifies which generated asset Rigging, Animations and Validation operate on. It is set automatically after generation. Choose another generated root in that field to work on an older asset. When the field is empty, a selected part or rig can identify its generated parent. New Generator measurements affect only the next generated asset; later workflow stages use the asset's saved generation parameters.

Rigging preserves mesh objects and existing edits where the automatic workflow remains valid. Automatic rigging refuses to overwrite an existing rig, conflicting bone groups, missing/renamed generated parts, or incompatible edited per-part transforms. Moving the common generated parent is supported.

## What an asset needs

A static prop does not need bones or animation. A poseable deforming asset needs a skeleton and skin weights. An animated asset also needs animation clips. All need suitable geometry, scale, appearance, and a tested export for the intended destination. No single checklist guarantees quality across every engine.

A material defines surface appearance. Image textures supply details such as color or roughness; UV maps place those images on the surface. A simple flat-color material can be sufficient for a stylized model, so image textures are optional. Blender procedural materials may need baking for portable export.

Add Missing Materials creates conservative Principled materials only for missing assignments. Existing artist materials are preserved. Providers with generated material intent may supply their own editable base material/texture foundation. Cura STL does not require materials, UVs, rigs or animation.

## Validation options and scope

Choose Static Asset, Rigged Asset, or Animated Asset. Enable Image Textures Expected only when the intended appearance requires image maps.

- Geometry checks mesh presence, finite coordinates, nonzero face area, and important target-specific topology requirements. It does not detect every self-intersection, shading problem, or artistic topology issue.
- Rigging checks armature/bone presence, enabled armature modifiers, and deform-weight coverage. It does not certify anatomy or final deformation quality.
- Animation checks changing unmuted curves, missing targets, non-finite values, Rest Position and zero action influence. It does not certify final motion quality, arbitrary constraint/NLA combinations, or destination playback.
- Materials checks required assignments and portable shader limitations.
- Textures checks image references and missing/external data where applicable.
- UVs checks active finite UV data when textures require it; it does not judge overlap, seams, or texel density.
- Transforms flags target-relevant transform conditions for review.

Validation-tab results are explicit snapshots. Redrawing the UI consumes the latest snapshot rather than repeatedly running expensive inspection. Export execution always performs a fresh safety preflight, so a stale green snapshot cannot authorize an invalid current scene.

## Provider behavior

Shared workflow code is capability-driven rather than anatomy-driven. Human and Quadruped both exercise connected deforming paths through the same Blender workflow, while Box demonstrates a static provider that skips rigging and animation. The next provider milestone is Avian and should use the same generic workflow wherever its actual capabilities fit.

Older saved generated assets may be migrated from historical provider identifiers when they are resolved. New assets always store their canonical provider identity.

[Export workflow](targets.md) explains formats and destination preparation. [Roadmap](roadmap.md) is the source of truth for active milestone work.
