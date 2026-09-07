# Human geometry

Asset Assistant currently keeps two Human geometry paths: the original multipart blockout and the Human 1.0 deformation-oriented surface. Keeping the legacy path available lets existing tests/workflows remain stable while the newer character foundation is refined.

## Coordinates and core data

`ObjectMesh` contains immutable `MeshPart` data with XYZ vertices and polygon faces. Core coordinates are centimeters in a right-handed system: Z is up, positive Y is forward, and positive X is the character's left. Adapters are responsible for host unit/axis conversion.

The mesh contracts validate finite coordinates, face indices, non-empty data, and unique part names. They do not by themselves prove arbitrary geometry is manifold, intersection-free, or production ready.

## Legacy multipart blockout

The original generator creates 15 separate closed parts: head, neck, torso, and paired upper arms, forearms, hands, upper legs, lower legs, and feet. It remains useful for proportion review, compatibility, rigid-rig behavior, and pipeline smoke tests.

That path is intentionally a blockout. Its pieces may overlap at joints and are not a welded character surface.

## Human 1.0 deformation-oriented surface

`generate_deformable_mesh` provides the newer Human 1.0 geometry foundation as one connected `human` mesh part.

The current surface:

- builds the torso, neck, and head as a continuous central loft;
- opens the torso at both shoulders and hips instead of overlapping separate limbs;
- stitches arm and leg branches into those openings so they share topology with the torso;
- integrates the feet into the leg chains;
- adds support rings immediately before/at/after internal limb joints;
- keeps support around elbows, wrists, knees, ankles, and foot bends; and
- derives dimensions and landmarks from the existing Human proportion system.

This is a meaningful topology/deformation foundation, but it is still generated low-detail character geometry. Hands remain simplified, there are no fingers/facial features, and joint quality still requires pose-based refinement.

## Deformation status

The connected mesh is now paired with a deforming skeleton, generated skin weights, Blender skinning, and automated pose smoke coverage. See [rigging.md](rigging.md) for the current weighting behavior and quality boundary.

The presence of support loops and successful deformation tests should not be read as “finished production topology.” Representative poses still need to be reviewed for silhouette, pinching, collapsing, twisting, and volume preservation, especially around shoulders and hips.

## Surfacing limits

Human 1.0 does not yet provide the complete release milestone. UV generation and the portable material/texture workflow remain open. Hands/feet and other blockout-level details also need further refinement before the first usable character milestone is complete.

## Parameters and editability

The deformation-oriented geometry continues to consume `HumanoidProportions`, preserving the existing supported Human measurements/presets as its input foundation. Generated Blender output remains ordinary editable mesh data rather than being locked to the add-on.

## Validation direction

Current automated geometry coverage establishes structural properties of the connected deformation-oriented surface and protects the topology foundation from regressions. Future quality work should turn reproducible deformation failures into focused geometry, weighting, or validation tests where practical.

See [the roadmap](roadmap.md) for the remaining Human Provider 1.0 sequence.
