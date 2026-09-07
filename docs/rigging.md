# Rigging

Asset Assistant currently has two Human rigging paths: the established rigid blockout path and the Human 1.0 deformation-oriented path. The rigid path remains useful for compatibility and pipeline smoke testing; Human 1.0 is the path toward an editable game character that bends as one skinned surface.

## Legacy rigid rig

The legacy generated humanoid uses a 16-bone skeleton: one root control and 15 bones corresponding to the separate mesh parts. Parent relationships let hands follow forearms/upper arms and feet follow lower/upper legs. It uses forward kinematics.

Each mesh part receives an Armature modifier and a single full-weight vertex group. That means each part moves as a solid piece. Gaps or overlaps can therefore appear at joints when posing. This behavior is intentional for the legacy blockout and should not be confused with Human 1.0 deformation.

The existing idle animation and export pipeline continue to use this proven path where appropriate.

## Human 1.0 deforming rig

Human 1.0 adds a separate deformation-oriented skeleton and skin-weight pipeline for the connected Human mesh.

The core deformation path currently provides:

- a 16-bone hierarchy with a non-deforming root and 15 deform bones;
- bone locations derived from the same Human proportions/landmarks as the geometry;
- generated per-vertex skin weights;
- normalized deterministic weights with a configurable maximum influence count;
- left/right limb isolation so a vertex on one side does not accidentally receive the opposite-side limb bones;
- connected-joint localization: weights are selected from the nearest deform bone and its structural parent/children rather than simply choosing unrelated geometrically nearby bones;
- a Human-specific hip bridge that deliberately blends torso and same-side upper leg across the non-deforming root while preserving side isolation;
- Blender armature/vertex-group application for the connected Human surface; and
- automated representative pose/deformation coverage.

This establishes that the mesh can be skinned and deformed through representative joints. It does **not** establish that every joint already deforms at production quality.

### Current quality boundary

The hip/root relationship is now deliberate rather than an accidental consequence of hierarchy proximity: vertices near each hip junction can blend between `torso` and the same-side `upper_leg`, while the opposite leg remains excluded.

Representative Blender pose regressions now cover shoulder, elbow/forearm, hip, knee, and neck behavior. These tests answer questions such as “does deformation occur?”, “are weights normalized and deterministic?”, “are influences kept anatomically local?”, and, for side-specific limb poses, “does posing one side avoid dragging the opposite side?”

They are not a substitute for visual inspection of silhouette, volume preservation, collapsing, pinching, and twisting. Wrists and ankles also remain part of the visual quality pass even though their topology/weighting path is covered structurally.

## Core contracts

The core rigging models contain no Blender data. `Bone` stores its name, head/tail coordinates, parent name, and optional rigid bound-part name. `Skeleton` validates hierarchy and bone data.

The legacy path uses rigid part bindings. The Human 1.0 deforming skeleton deliberately does not depend on those bindings; skinning is represented by generated vertex influences instead.

Human anatomy-specific bone placement and weighting behavior stays in the Human deformation implementation. Shared workflow/provider infrastructure should not learn Human bone names as a consequence of this work.

## Blender behavior

The Blender adapter translates the core skeleton into an editable armature and applies the appropriate weighting strategy. Provider-aware rigging UI selects the correct behavior for the generated asset instead of assuming every riggable provider is the legacy humanoid.

Removing the add-on leaves generated Blender armatures, modifiers, vertex groups, and meshes as ordinary editable scene data. Generation measurements remain generation inputs rather than live procedural controls.

## Validation and tests

Current automated coverage includes legacy skeleton hierarchy/motion checks plus Human 1.0 deformation tests for skeleton structure, normalized bounded weights, determinism, side isolation, connected-joint influence neighborhoods, explicit hip bridging, Blender deformation application, and representative shoulder, elbow/forearm, hip, knee, and neck poses.

The remaining Human 1.0 deformation milestone is visual quality refinement: representative poses must be inspected and improved, with reproducible failures converted into focused automated tests where practical. See [the roadmap](roadmap.md) for the current order of work.
