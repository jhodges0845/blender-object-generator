# Human geometry

Asset Assistant currently keeps two Human geometry paths: the original multipart blockout and the Human 1.0 deformation-oriented surface. The legacy path remains useful for compatibility and pipeline smoke tests while Human 1.0 is the path toward a connected deformable game character.

## Coordinates and core data

`ObjectMesh` contains immutable `MeshPart` data with XYZ vertices and polygon faces. Core coordinates are centimeters in a right-handed system: Z is up, positive Y is forward, and positive X is the character's left. Adapters are responsible for host unit/axis conversion.

Mesh contracts validate finite coordinates, face indices, non-empty data, and unique part names. They do not by themselves prove arbitrary geometry is manifold, intersection-free, or production ready.

## Legacy multipart blockout

The original generator creates 15 separate closed parts: head, neck, torso, and paired upper arms, forearms, hands, upper legs, lower legs, and feet. It remains useful for proportion review, compatibility, rigid-rig behavior, and pipeline smoke tests.

That path is intentionally a blockout. Its pieces may overlap at joints and are not a welded character surface.

## Human 1.0 deformation-oriented surface

`generate_deformable_mesh` provides the Human 1.0 geometry foundation as one connected `human` mesh part.

The current surface:

- builds the torso, neck, and head as a continuous central loft;
- opens the torso at both shoulders and hips instead of overlapping separate limbs;
- stitches arm and leg branches into those openings so they share topology with the torso;
- integrates the feet into the leg chains;
- adds local support geometry around shoulders, elbows, wrists, hips, knees, ankles, foot bends, and the neck transition;
- gives each hand a simple palm -> knuckle -> tapered fingertip blockout;
- gives each foot a heel -> midfoot -> ball -> tapered toe blockout; and
- derives dimensions and landmarks from the existing Human proportion system.

This is still deliberately low-detail generated geometry. Hands do not have individual fingers, feet do not have individual toes, and the head has no facial features. The goal is a useful editable artist starting point rather than finished anatomy.

## Structural coverage

Current core tests protect:

- one connected Human surface and closed/manifold topology;
- deterministic generation and preserved height/symmetry;
- identical topology across all five body-type presets;
- hand and foot blockout sections at the supported 120 cm and 240 cm height extremes;
- hand palm volume relative to the fingertip taper;
- forefoot/ball volume relative to the toe taper; and
- retained joint-support geometry.

The connected mesh is also exercised through Blender skinning/deformation tests on both supported Blender runtimes.

## Deformation status

The mesh is paired with a deforming skeleton, generated skin weights, Blender skinning, connected-joint influence localization, explicit torso-to-upper-leg hip bridging, and softened torso/neck and torso/shoulder transitions.

Automated Blender regressions exercise shoulder, elbow, wrist, hip, knee, ankle, and neck motion. Separate structural checks guard those representative transition regions against excessive collapse during deliberate bends. See [rigging.md](rigging.md) and [deformation-quality.md](deformation-quality.md).

These tests establish regression protection, not final aesthetic quality. The manual inspection harness remains the milestone-level check for silhouette, pinching, bunching, and other artist-facing issues.

## Surfacing limits

Human 1.0 does not yet generate UVs or a complete portable material/texture setup. Those are the next feature steps after the current test/documentation/architecture cleanup gate.

## Parameters and editability

The deformation-oriented geometry consumes `HumanoidProportions`, preserving the existing supported Human measurements and body presets. Generated Blender output remains ordinary editable mesh data rather than a locked procedural object.

See [the roadmap](roadmap.md) for the remaining Human Provider 1.0 sequence.
