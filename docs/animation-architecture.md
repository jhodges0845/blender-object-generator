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

Generated records must own their generated curves. Imported or artist-authored records remain unowned so lifecycle and later Modify work cannot silently overwrite artist animation.

## Serialization boundary

`animation_document()` produces strict JSON-safe portable state. `animation_from_document()` rejects missing and unknown fields instead of silently accepting host-specific metadata or schema drift.

## Blender persistence and inspection

New Asset Assistant-generated Blender Actions persist the portable record as Action metadata while retaining the existing generated clip, rig ownership, and export-name properties used by current UI/export code.

The adapter assigns a stable animation ID, records provider/capability provenance, and computes a deterministic rig signature from the generated armature's bone names, parent relationships, and deform flags. Inspection rejects mismatched IDs, incompatible rig signatures, generated records attached to non-generated Actions, and export-name drift.

The existing animation export-name workflow updates the portable record and the legacy Action property together. Legacy generated Actions from older `.blend` files that do not yet carry animation-record metadata remain usable and renameable; malformed new record metadata is not silently ignored.

Current generated Idle/Walk-or-locomotion/Flight/Run clips are recorded as looping, in-place animations because the current provider generators create cyclic rotational motion without root translation.

## Action registration and lifecycle

Existing Blender Actions can now be explicitly registered as `artist` or `imported` animation assets for one Asset Assistant rig. Registration adds stable portable identity, current-rig compatibility, frame/FPS metadata, loop/root-motion intent, and an engine-facing export name without changing the Action's curves or claiming curve ownership.

Registration refuses generated Actions, Actions already carrying Asset Assistant animation identity, and Actions actively assigned to another Blender object. This keeps adoption explicit and prevents a shared or unrelated Action from being silently claimed.

Lifecycle operations preserve ownership:

- removing an artist/imported registration removes Asset Assistant identity but leaves the Action and its curves intact;
- removing a generated record may delete the generated Action because Asset Assistant owns those curves;
- replacing a managed animation preserves its stable `animation_id` while moving that identity to the replacement Action;
- replacing an artist/imported clip leaves the prior Action intact and merely stops managing it;
- an active replaced clip moves the rig's active Action to the validated replacement.

`managed_actions()` discovers first-class records compatible with the current rig. `exportable_actions()` additionally retains legacy generated Actions so old editable checkpoints remain discoverable while export staging is migrated to the first-class lifecycle.

## Next adapter slice

With registration/add/remove/replace semantics established, the next slice should connect managed animation state to the Modify exchange and expose narrowly scoped animation operations without weakening artist ownership boundaries.

After Modify transport is proven, the first executable tuning semantics can be added for generated clips, followed by the save -> reopen -> component edit -> animation edit -> save -> engine export checkpoint.
