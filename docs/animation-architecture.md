# Animation architecture

Animations are first-class reusable assets in Asset Assistant. Their portable identity and ownership contract lives in `object_core`; Blender Actions, NLA data, keyframes, and target-export details remain adapter concerns.

## Portable animation record

`AnimationRecord` establishes the host-independent metadata needed to inspect and safely manage a clip:

- stable `animation_id` independent of the host action/datablock name;
- artist-facing `display_name` and destination-facing `export_name`;
- `AnimationSource` provenance: generated, imported, or artist-authored;
- portable `rig_signature` compatibility identity;
- frame start/end and FPS;
- loop intent;
- `RootMotionIntent` (`none`, `in_place`, or `root`);
- explicit `owns_curves` ownership boundary;
- optional source reference, provider key, and capability identity.

The record intentionally contains no Blender Action name, slot, FCurve, NLA, object pointer, or engine-specific field.

Generated records must own their generated curves. Imported or artist-authored records may remain unowned so later lifecycle/Modify work cannot silently overwrite artist animation.

## Serialization boundary

`animation_document()` produces strict JSON-safe portable state. `animation_from_document()` rejects missing and unknown fields instead of silently accepting host-specific metadata or schema drift.

## Next adapter slice

The Blender adapter will persist a portable animation document alongside an Action and inspect it back into `AnimationRecord`. It must verify rig compatibility and ownership without assuming an Action is safe to mutate merely because it exists in the `.blend` file.

After persistence/inspection is proven, lifecycle work can add/import/remove/replace records transactionally and later expose preservation-aware animation Modify semantics.
