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
- Blender armature/vertex-group application for the connected Human surface; and
- automated pose/deformation smoke coverage.

This establishes that the mesh can be skinned and deformed. It does **not** establish that every joint already deforms at production quality.

### Current quality boundary

Shoulders, elbows, wrists, hips, knees, ankles, and the neck still need representative visual pose review and refinement. In particular, the root is intentionally non-deforming, while the upper legs are children of that root. The current connected-neighborhood weighting therefore does not by itself provide a deliberate torso-to-upper-leg blend across the hip junction. Hip/root weighting is a specific next refinement rather than something the documentation should claim is solved.

Automated smoke tests answer questions such as “does deformation occur?”, “are weights normalized and deterministic?”, and “are influences kept anatomically local?” They are not a substitute for inspecting silhouette, volume preservation, collapsing, pinching, and twisting in representative poses.

## Core contracts

The core rigging models contain no Blender data. `Bone` stores its name, head/tail coordinates, parent name, and optional rigid bound-part name. `Skeleton` validates hierarchy and bone data.

The legacy path uses rigid part bindings. The Human 1.0 deforming skeleton deliberately does not depend on those bindings; skinning is represented by generated vertex influences instead.

Human anatomy-specific bone placement and weighting behavior stays in the Human deformation implementation. Shared workflow/provider infrastructure should not learn Human bone names as a consequence of this work.

## Blender behavior

The Blender adapter translates the core skeleton into an editable armature and applies the appropriate weighting strategy. Provider-aware rigging UI selects the correct behavior for the generated asset instead of assuming every riggable provider is the legacy humanoid.

Removing the add-on leaves generated Blender armatures, modifiers, vertex groups, and meshes as ordinary editable scene data. Generation measurements remain generation inputs rather than live procedural controls.

## Validation and tests

Current automated coverage includes legacy skeleton hierarchy/motion checks plus Human 1.0 deformation tests for skeleton structure, normalized bounded weights, determinism, side isolation, connected-joint influence neighborhoods, Blender deformation application, and pose smoke behavior.

The remaining Human 1.0 deformation milestone is quality validation: representative joint poses must be inspected/refined and useful regressions converted into automated tests where practical. See [the roadmap](roadmap.md) for the current order of work.
