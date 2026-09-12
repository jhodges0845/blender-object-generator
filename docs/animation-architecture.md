# Animation architecture

Animations are first-class reusable assets in Asset Assistant. Their portable identity and ownership contract lives in `object_core`; Blender Actions, NLA data, keyframes, and target-export details remain adapter concerns.

## Portable animation record

`AnimationRecord` establishes the host-independent metadata needed to inspect and safely manage a clip:

- stable `animation_id` independent of the host action/datablock name;
- artist-facing `display_name` and destination-facing `export_name`;
- `AnimationSource` provenance: generated, imported, or artist-authored;
- portable `rig_signature` compatibility identity;
- finite frame start/end and FPS;
- loop intent;
- `RootMotionIntent` (`none`, `in_place`, or `root`);
- explicit `owns_curves` ownership boundary;
- optional source reference, provider key, and capability identity.

The record intentionally contains no Blender Action name, slot, FCurve, NLA, object pointer, or engine-specific field.

Generated records must own their generated curves. Imported or artist-authored records may remain unowned so later lifecycle/Modify work cannot silently overwrite artist animation.

## Serialization boundary

`animation_document()` produces strict JSON-safe portable state. `animation_from_document()` rejects missing and unknown fields instead of silently accepting host-specific metadata or schema drift.

## Blender persistence and inspection

New Asset Assistant-generated Blender Actions persist the portable record as Action metadata while retaining the existing generated clip, rig ownership, and export-name properties used by current UI/export code.

The adapter assigns a stable animation ID, records provider/capability provenance, and computes a deterministic rig signature from the generated armature's bone names, parent relationships, and deform flags. Inspection rejects mismatched IDs, incompatible rig signatures, generated records attached to non-generated Actions, and export-name drift.

The existing animation export-name workflow updates the portable record and the legacy Action property together. Legacy generated Actions from older `.blend` files that do not yet carry animation-record metadata remain usable and renameable; malformed new record metadata is not silently ignored.

Current generated Idle/Walk-or-locomotion/Flight/Run clips are recorded as looping, in-place animations because the current provider generators create cyclic rotational motion without root translation.

## Next adapter slice

With generated Action persistence/inspection established, the next lifecycle slice can register imported/artist-authored Actions and add preservation-aware add/remove/replace operations without regenerating the base asset.

After lifecycle work is proven, animation inspection/request transport can expose preservation-aware Modify planning and narrowly scoped executable tuning semantics.
