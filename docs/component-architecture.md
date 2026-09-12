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

Portable component documents now round-trip through `component_document()` and `component_from_document()` so host adapters can persist and revalidate the same contract instead of inventing host-only metadata shapes.

## Physics boundary

Physics intent is descriptive, not executable. A component may request an intent such as `secondary_motion`, but host/engine adapters decide whether that intent is supported and how it maps to native behavior. Unsupported intent must remain explicit rather than silently becoming a different simulation.

## Ownership and Modify

Components must remain preservation boundaries. The first Blender execution slice now provides:

1. persistent component records on generated asset roots;
2. matching persisted metadata on each Blender component root;
3. host-side inspection that verifies registry/object metadata agreement;
4. owned-geometry presence checks;
5. duplicate component-id rejection;
6. transactional creation rollback when attachment fails.

Still required before broader component Modify is executable:

1. bone/socket attachment validation;
2. skinned component ownership and rig/weight inspection;
3. safe transactional remove/replace operations;
4. Modify inspection/request transport for component state;
5. adapter-specific physics preparation only after ownership is known.

Artist-created or artist-edited component data must not be overwritten unless ownership is explicit and the operation is safe.

## First Blender execution slice

`blender_adapter.components.attach_rigid_component()` accepts a portable `ObjectMesh` and validated `ComponentRecord`, creates a dedicated component root under the owning generated asset, creates owned mesh-part children, persists the portable record, and immediately re-inspects the result.

This slice intentionally supports only:

- `AttachmentMode.RIGID`;
- `attachment_target="asset_root"`;
- generated component geometry that remains owned by Asset Assistant.

It does not yet provide artist-facing Blender UI or a public accessory catalog/provider. Tests use a simple portable mesh only to prove the persistence and attachment architecture. Bone-attached accessories, hair, clothing, skinned components, and dynamics remain later slices.

## Intended layering

`Body provider -> attachment context -> component provider/record -> Blender adapter -> optional host physics -> target adapter -> engine-specific result`

Human remains responsible for body/facial geometry, skin/material foundation, skeleton/weights, and attachment context. Component providers remain responsible for their own geometry and semantics. Shared workflow code should only coordinate through explicit capabilities and records.
