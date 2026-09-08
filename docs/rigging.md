# Rigging

Asset Assistant currently has two Human rigging paths: the established rigid blockout path and the Human 1.0 deformation-oriented path. The rigid path remains useful for compatibility and pipeline smoke testing; Human 1.0 is the path toward an editable game character that bends as one skinned surface.

## Legacy rigid rig

The legacy generated humanoid uses a 16-bone skeleton: one root control and 15 bones corresponding to the separate mesh parts. Parent relationships let hands follow forearms/upper arms and feet follow lower/upper legs. It uses forward kinematics.

Each mesh part receives an Armature modifier and a single full-weight vertex group. Each part therefore moves as a solid piece, so gaps or overlaps can appear at joints when posing. This behavior is intentional for the legacy blockout and should not be confused with Human 1.0 deformation.

## Human 1.0 deforming rig

Human 1.0 adds a separate deformation-oriented skeleton and skin-weight pipeline for the connected Human mesh.

The current core path provides:

- a 16-bone hierarchy with a non-deforming root and 15 deform bones;
- bone locations derived from the same Human proportions/landmarks as the geometry;
- generated per-vertex skin weights;
- normalized deterministic weights with a configurable maximum influence count;
- left/right limb isolation;
- connected-joint localization based on the nearest deform bone plus its structural neighborhood;
- a Human-specific same-side torso/upper-leg hip bridge across the non-deforming root;
- softer torso/neck and torso/shoulder weighting to improve those transition regions;
- Blender armature/vertex-group application for the connected Human surface; and
- automated representative deformation coverage.

Human anatomy-specific placement and weighting remain local to the Human deformation implementation. Shared provider/workflow infrastructure should not learn Human bone names as a consequence of this work.

## Current quality boundary

Representative Blender regressions now cover shoulder, elbow/forearm, wrist, hip, knee, ankle, and neck behavior. Additional bend tests guard the spread of all seven representative transition regions against obvious collapse.

These tests answer structural questions such as:

- does the intended surface move when a representative bone bends;
- do side-specific poses avoid dragging the opposite side;
- are weights normalized, deterministic, bounded, and anatomically local; and
- does the joint transition retain a reasonable fraction of its neutral spread.

They are not a substitute for visual inspection of silhouette, pinching, bunching, twisting, or final anatomical quality. The manual Blender inspection harness is therefore kept as a milestone-level quality check rather than a per-PR requirement.

## Core contracts

The core rigging models contain no Blender data. `Bone` stores its name, head/tail coordinates, parent name, and optional rigid bound-part name. `Skeleton` validates hierarchy and bone data.

The legacy path uses rigid part bindings. The Human 1.0 deforming skeleton deliberately does not depend on those bindings; skinning is represented by generated vertex influences instead.

## Blender behavior

The Blender adapter translates the core skeleton into an editable armature and applies the provider-appropriate weighting strategy. Provider-aware rigging UI selects the correct behavior for the generated asset instead of assuming every riggable provider is the legacy humanoid.

Removing the add-on leaves generated Blender armatures, modifiers, vertex groups, and meshes as ordinary editable scene data. Generation measurements remain inputs rather than live procedural controls.

## Validation and tests

Current automated coverage includes legacy hierarchy/motion checks plus Human 1.0 tests for skeleton structure, normalized bounded weights, determinism, side isolation, connected-joint neighborhoods, explicit hip bridging, neck/shoulder shared weighting, Blender skinning, representative joint movement, and transition-spread retention.

See [deformation-quality.md](deformation-quality.md) for the manual/automated review boundary and [the roadmap](roadmap.md) for the remaining Human 1.0 work.
