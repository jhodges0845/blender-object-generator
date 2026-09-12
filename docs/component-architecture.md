# Attachable component architecture

Hair, clothing, and accessories are first-class components rather than ordinary Human body semantics. They may own geometry, materials, rig data, parameters, and optional physics intent independently of the body provider.

## Core boundary

`object_core.components` defines only portable data contracts:

- component identity;
- kind: hair, clothing, or accessory;
- provider key;
- attachment target;
- rigid or skinned attachment mode;
- rig binding: `none`, `parent`, or `owned`;
- component parameters;
- ownership flags for geometry, materials, and rig data;
- optional physics intent expressed as portable metadata.

The core does not know how Blender cloth, Blender hair dynamics, Godot physics, Unity physics, or Unreal physics are implemented.

Portable component documents round-trip through `component_document()` and `component_from_document()` so host adapters can persist and revalidate the same contract instead of inventing host-only metadata shapes.

## Attachment target convention

Portable rigid attachment targets currently use one of two forms:

- `asset_root` for an attachment that follows the generated asset as a whole;
- `bone:<bone-name>` for an attachment that follows a named generated bone, for example `bone:hand.right`.

The first skinned parent-rig execution path uses `attachment_target="body"`. The component root remains owned by the generated asset while its mesh objects deform through the owning asset armature.

The core stores the target but does not resolve host objects. Blender resolves and validates host attachment/rig state. Other host/engine adapters may translate the same portable intent into their native attachment mechanism.

## Rig binding contract

Skinned components separate rig ownership from deformation binding through `RigBinding`:

- `none`: no rig binding; required for rigid components;
- `parent`: the component deforms using the owning asset's rig and does not own rig data;
- `owned`: the component deforms using rig data that belongs to the component itself.

This distinction is important for clothing and many hair systems. A coat can be skinned to the Human rig with `rig_binding="parent"` and `owns_rig=False`; it should not claim ownership of the Human skeleton. A component that truly carries an independent rig uses `rig_binding="owned"` and must set `owns_rig=True`.

Persisted documents written before this field existed remain readable. A legacy valid skinned record with `ownership.rig=true` is interpreted as `rig_binding="owned"`; rigid records remain `none`.

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
8. inspection that detects missing bones, armature detachment, or bone retargeting;
9. validated removal of owned rigid component trees and registry entries;
10. stable-id rigid replacement with rollback;
11. parent-rig skinned component creation for generated owned geometry;
12. exact persisted skin-weight validation against Blender vertex groups;
13. armature-modifier validation against the owning generated rig;
14. transactional rollback when skinned binding validation fails;
15. validated skinned removal that deletes only the owned component tree and registry entry while preserving the parent armature;
16. stable-id skinned replacement that keeps the previous weighted component intact until the replacement is created and re-inspected;
17. failed skinned replacement rollback that restores the previous registry/object metadata and leaves the original weighted component usable;
18. Modify inspection v3 exports validated attached component records;
19. Modify request v3 parses portable add/remove/replace component operations;
20. Blender capability planning makes exactly one validated component removal executable through the external Modify apply path;
21. base geometry/rig regeneration is blocked while components are attached so component bindings cannot be invalidated silently;
22. add/replace remain explicit blockers until a real component provider can reproduce geometry and, where required, skin weights.

Still required before the first real component-provider workflow is complete:

1. implement a real component provider capable of reproducing geometry and optional skin weights from portable parameters;
2. route validated Modify add/replace through that provider and the existing rigid/skinned lifecycle functions;
3. add artist-facing component creation/selection UI;
4. run a component regression/documentation checkpoint;
5. add adapter-specific physics preparation only after the first provider proves the ownership flow;
6. add component-owned rig execution for `rig_binding="owned"` only if a provider actually requires it.

Artist-created or artist-edited component data must not be overwritten unless ownership is explicit and the operation is safe.

## Modify exchange

Modify inspection and request schemas are version 3. Inspection JSON includes `attached_components`, each serialized with the same portable `ComponentRecord` document used for Blender persistence. The request template includes `component_operations` for `add`, `remove`, and `replace` intent.

Legacy request v1 and v2 payloads remain readable. Component operations are validated against the inspected component identities by the host-independent planner. The portable core still treats component mutation as transport intent; Blender then refines that plan according to capabilities it can prove safe.

Blender currently enables exactly one `remove` operation per imported request. The requested component is re-inspected before deletion and dispatched through the rigid or parent-rig-skinned lifecycle path as appropriate. Multiple removals are intentionally separated into individual requests so rollback boundaries remain explicit. Requests that mix component removal with other Modify changes are also blocked.

`add` and `replace` remain blocked because a `ComponentRecord` contains identity, attachment, ownership, parameters, and physics intent but not executable geometry or skin weights. Those operations become safe only after a component provider can deterministically reproduce the requested component from its portable record.

The Blender planner also blocks provider geometry/rig regeneration while any component remains attached. This prevents a parameter or semantic body change from replacing the parent rig underneath skinned clothing or bone-attached accessories before rebinding/preservation behavior exists.

The artist-facing Blender Modify workflow enriches its base asset snapshot with revalidated rigid/skinned component state before exporting inspection JSON or validating an imported request. Invalid/tampered component state therefore blocks transport rather than being silently described as healthy.

## Current Blender execution slices

`blender_adapter.components.attach_rigid_component()` accepts a portable `ObjectMesh` and validated `ComponentRecord`, creates a dedicated component root, creates owned mesh-part children, persists the portable record, and immediately re-inspects the result.

For `attachment_target="asset_root"`, the component root is parented directly to the generated asset root. For `attachment_target="bone:<bone-name>"`, the component root is parented to the generated armature using Blender bone parenting after the target bone is validated.

`remove_component()` first requires a clean rigid inspection result, then removes only the component-owned hierarchy and its registry entry. `replace_rigid_component()` preserves the stable component ID, temporarily keeps the previous component as the rollback source, creates and validates the replacement, and deletes the previous owned tree only after the new component is known-good.

`blender_adapter.skinned_components.attach_skinned_component()` requires `AttachmentMode.SKINNED`, `RigBinding.PARENT`, `owns_rig=False`, and `attachment_target="body"`. The caller supplies portable component geometry plus portable `SkinWeights`; Blender validates every referenced bone against the owning armature, creates exact vertex groups, adds an armature modifier targeting that armature, persists generated weight metadata, and re-inspects the component before committing the registry entry.

`inspect_skinned_component()` detects modifier retargeting, missing or changed mesh parts, vertex-count drift, and exact generated weight changes.

`remove_skinned_component()` requires a clean skinned inspection result before deleting the component-owned hierarchy and registry entry. It does not delete or mutate the owning asset armature.

`replace_skinned_component()` preserves the stable component ID and uses the previous weighted component as the rollback source. The old tree remains intact while the replacement is created and fully re-inspected; only then is the old component deleted. If replacement creation or validation fails, the previous registry and component-root metadata are restored.

`blender_adapter.component_modify_apply` layers Blender capability checks over the portable planner. It enables a single validated remove request, dispatches rigid/skinned removal through their proven lifecycle functions, preserves the owning asset and armature, and leaves add/replace blocked until executable providers exist.

These slices still do not provide artist-facing component creation UI, a public clothing/hair catalog, component-owned rigs, or physics execution.

## Intended layering

`Body provider -> attachment context -> component provider/record -> Blender adapter -> optional host physics -> target adapter -> engine-specific result`

Human remains responsible for body/facial geometry, skin/material foundation, skeleton/weights, and attachment context. Component providers remain responsible for their own geometry and semantics. Shared workflow code should only coordinate through explicit capabilities and records.
