# Component persistence checkpoint

This checkpoint proves the first executable Blender slice of the attachable-component architecture.

Implemented:

- portable component documents can be parsed back into validated `ComponentRecord` values;
- the Blender core gateway exposes the component contract in both checkout and packaged-ZIP layouts;
- a rigid component can be attached transactionally to a generated asset root;
- the parent asset stores the component registry as portable JSON;
- the component root stores the same portable record for cross-checking;
- inspection rejects duplicate component ids, missing/ambiguous component roots, invalid metadata, parent detachment, and missing owned geometry;
- failed attachment restores the prior registry and removes created Blender objects/meshes.

Current execution boundary:

- attachment mode: rigid only;
- attachment target: `asset_root` only;
- component geometry: caller-supplied portable `ObjectMesh`;
- no artist-facing component UI yet;
- no component catalog/provider yet;
- no bone/socket attachment yet;
- no skinned component path yet;
- no physics execution yet;
- no remove/replace operation yet.

The next safe slice should add explicit attachment points/bone sockets and inspection rules before introducing a user-facing accessory provider. Hair and clothing should wait until skinned ownership and optional-physics boundaries are proven.
