# Human geometry

Asset Assistant currently keeps two Human geometry paths: the original multipart blockout and the Human 1.0 deformation-oriented surface. The legacy path remains useful for compatibility and pipeline smoke tests while Human 1.0 is the path toward a connected deformable game character.

## Coordinates and core data

`ObjectMesh` contains immutable `MeshPart` data with XYZ vertices, polygon faces, and optional face-corner UV coordinates. Core coordinates are centimeters in a right-handed system: Z is up, positive Y is forward, and positive X is the character's left. Adapters are responsible for host unit/axis conversion.

Mesh contracts validate finite coordinates, face indices, optional UV shape/finite values, non-empty data, and unique part names. They do not by themselves prove arbitrary geometry is manifold, intersection-free, UV-overlap-free, or production ready.

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
- gives each foot a heel -> midfoot -> ball -> tapered toe blockout;
- uses a denser head profile than the original blockout, with additional rings from chin through jaw, cheek, temple, and crown;
- applies a neutral facial shaping pass to the forward head surface so chin, mouth/lips, nose bridge/tip, eye recess, brow, cheeks, jaw, and forehead read as different broad landmarks;
- generates deterministic face-corner UVs packed into the 0-1 UV square; and
- derives dimensions and landmarks from the existing Human proportion system.

This remains generated low-detail geometry rather than finished anatomy. Hands do not have individual fingers, feet do not have individual toes, and the facial foundation does not yet model realistic eyes, nostrils, detailed eyelids, or finished lips. The goal is a useful editable and semantically shapeable artist starting point.

## Facial structure and semantic resolution

The first Human semantic Modify round trip exposed that semantic vocabulary alone cannot compensate for insufficient base topology. The mesh therefore received three quality passes after the first semantic executor landed:

1. additional head rings to smooth the jaw -> cheek -> temple -> crown silhouette;
2. a neutral forward-face shaping pass that established broad chin, mouth, nose, eye, brow, and forehead planes;
3. a stronger reusable landmark pass that increased visible separation between nose, eye recess, brow, mouth/lips, chin, jaw taper, and cheek breadth while keeping the face character-neutral.

Manual Blender front/side review confirmed the first two passes improved the base. The third pass is now merged and needs the next visual checkpoint before deciding whether more base-face work is justified.

Human semantic targets currently include body, torso, shoulders, head, face, jaw, cheeks, left/right arms, and left/right legs. The mesh work is intentionally generic so external Modify requests can use those regions to describe a particular character without embedding that character in the provider.

## Structural coverage

Current core tests protect:

- one connected Human surface and closed/manifold topology;
- deterministic generation and preserved height/symmetry;
- identical topology across all five body-type presets;
- hand and foot blockout sections at the supported 120 cm and 240 cm height extremes;
- hand palm volume relative to the fingertip taper;
- forefoot/ball volume relative to the toe taper;
- retained joint-support geometry;
- increased head profile resolution and taper behavior;
- neutral facial landmark relationships such as nose projection, eye-recess/brow distinction, visible profile separation, and mouth/chin distinction; and
- complete deterministic UV coverage across body presets and supported height extremes.

The connected mesh is also exercised through Blender skinning/deformation tests on both supported Blender runtimes. Blender integration additionally verifies that generated Human UV data becomes an ordinary editable `UVMap` layer.

## Deformation status

The mesh is paired with a deforming skeleton, generated skin weights, Blender skinning, connected-joint influence localization, explicit torso-to-upper-leg hip bridging, and softened torso/neck and torso/shoulder transitions.

Automated Blender regressions exercise shoulder, elbow, wrist, hip, knee, ankle, and neck motion. Separate structural checks guard those representative transition regions against excessive collapse during deliberate bends. See [rigging.md](rigging.md) and [deformation-quality.md](deformation-quality.md).

These tests establish regression protection, not final aesthetic quality. Manual Blender inspection remains the milestone-level check for silhouette, facial readability, pinching, bunching, and other artist-facing issues.

## UV and surfacing status

Human 1.0 has a deterministic portable UV foundation plus a generated base material/texture starting point. The first layout intentionally favors complete, non-overlapping face islands and a stable core/Blender contract over artist-optimized continuous islands. It remains editable in Blender and can be refined later without changing the mesh UV contract.

## Parameters and editability

The deformation-oriented geometry consumes `HumanoidProportions`, preserving the existing supported Human measurements and body presets. Generated Blender output remains ordinary editable mesh and UV data rather than a locked procedural object.

Topology-preserving semantic Modify operations are stored as replayable patch recipes on the generated asset. Parameter regeneration reapplies those patches to the new procedural base so a later parameter change does not silently erase semantic shaping.

Hair, clothing, and accessories are intentionally not part of Human body geometry. They remain planned as separate attachable component types because their geometry, materials, rigging, collision, and optional physics requirements differ from body shaping.

See [semantic Modify](semantic-modify.md), [the performance/test audit](performance-test-audit.md), and [the roadmap](roadmap.md) for current priorities.
