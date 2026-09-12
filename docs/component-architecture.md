# Attachable component architecture

Hair, clothing, and accessories are first-class components rather than ordinary Human body semantics. They may own geometry, materials, rig data, parameters, and optional physics intent independently of the body provider.

## Core boundary

`object_core.components` defines only portable data contracts:

- component identity;
- kind: hair, clothing, or accessory;
- provider key;
- attachment target;
- rigid or skinned attachment mode;
- component parameters;
- ownership flags for geometry, materials, and rig data;
- optional physics intent expressed as portable metadata.

The core does not know how Blender cloth, Blender hair dynamics, Godot physics, Unity physics, or Unreal physics are implemented.

Portable component documents round-trip through `component_document()` and `component_from_document()` so host adapters can persist and revalidate the same contract instead of inventing host-only metadata shapes.

## Attachment target convention

Portable rigid attachment targets currently use one of two forms:

- `asset_root` for an attachment that follows the generated asset as a whole;
- `bone:<bone-name>` for an attachment that follows a named generated bone, for example `bone:hand.right`.

The core stores the target but does not resolve host objects. Blender validates that the generated asset contains exactly one armature, verifies that the named bone exists, and then binds the component root to that bone. Other host/engine adapters may translate the same portable target into their native attachment mechanism.

## Physics boundary

Physics intent is descriptive, not executable. A component may request an intent such as `secondary_motion`, but host/engine adapters decide whether that intent is supported and how it maps to native behavior. Unsupported intent must remain explicit rather than silently becoming a different simulation.

## Ownership and Modify

Components must remain preservation boundaries. The Blender execution slices now provide:

1. persistent component records on generated asset roots;
2. matching persisted metadata on each Blender component root;
3. host-side inspection that verifies registry/object metadata agreement;
4. owned-geometry presence checks;
5. duplicate component-id rejection;
6. transactional creation rollback when attachment fails;
7. rigid `asset_root` and `bone:<bone-name>` attachment validation;
8. inspection that detects missing bones, armature detachment, or bone retargeting.

Still required before broader component Modify is executable:

1. skinned component ownership and rig/weight inspection;
2. safe transactional remove/replace operations;
3. Modify inspection/request transport for component state;
4. adapter-specific physics preparation only after ownership is known;
5. artist-facing component creation/selection UI and real component providers.

Artist-created or artist-edited component data must not be overwritten unless ownership is explicit and the operation is safe.

## Current Blender execution slice

`blender_adapter.components.attach_rigid_component()` accepts a portable `ObjectMesh` and validated `ComponentRecord`, creates a dedicated component root, creates owned mesh-part children, persists the portable record, and immediately re-inspects the result.

For `attachment_target="asset_root"`, the component root is parented directly to the generated asset root. For `attachment_target="bone:<bone-name>"`, the component root is parented to the generated armature using Blender bone parenting after the target bone is validated.

This slice intentionally supports only rigid generated components that own their geometry. It does not yet provide artist-facing Blender UI or a public accessory catalog/provider. Tests use a simple portable mesh only to prove persistence and attachment behavior. Hair, clothing, skinned components, remove/replace operations, and dynamics remain later slices.

## Intended layering

`Body provider -> attachment context -> component provider/record -> Blender adapter -> optional host physics -> target adapter -> engine-specific result`

Human remains responsible for body/facial geometry, skin/material foundation, skeleton/weights, and attachment context. Component providers remain responsible for their own geometry and semantics. Shared workflow code should only coordinate through explicit capabilities and records.
