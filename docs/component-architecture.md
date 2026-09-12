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

## Physics boundary

Physics intent is descriptive, not executable. A component may request an intent such as `secondary_motion`, but host/engine adapters decide whether that intent is supported and how it maps to native behavior. Unsupported intent must remain explicit rather than silently becoming a different simulation.

## Ownership and Modify

Components must remain preservation boundaries. Future executable component work must add:

1. persistent component records on generated assets;
2. host-side inspection that proves owned geometry/material/rig state;
3. attachment validation against the parent asset;
4. safe transactional add/remove/replace operations;
5. Modify inspection/request transport for component state;
6. adapter-specific physics preparation only after ownership is known.

Artist-created or artist-edited component data must not be overwritten unless ownership is explicit and the operation is safe.

## What this first foundation does not do

This milestone does not generate hair, clothing, or accessories, does not add Blender UI, and does not advertise component operations as executable. It only establishes the host-independent contract and validation rules required before those features can be implemented safely.

## Intended layering

`Body provider -> attachment context -> component provider/record -> Blender adapter -> optional host physics -> target adapter -> engine-specific result`

Human remains responsible for body/facial geometry, skin/material foundation, skeleton/weights, and attachment context. Component providers remain responsible for their own geometry and semantics. Shared workflow code should only coordinate through explicit capabilities and records.
