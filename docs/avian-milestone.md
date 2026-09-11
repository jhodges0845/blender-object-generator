# Avian provider milestone

Avian is the second non-Human deforming-provider architecture proof after Quadruped.

The implementation uses canonical Avian identity throughout: provider key `avian`, `AvianProvider`, Avian-named geometry, rigging, animation, tests, generated metadata, and documentation. No alternate provider name is used.

## Implemented foundation

- deterministic connected low-poly Avian surface with integrated wings and tail
- Avian spine/neck/head, upper/lower wing, and tail skeleton
- normalized local skin weights and Blender deformation coverage for wing roots, wing segments, neck/head, and tail
- deterministic face-corner UVs and portable textured plumage material intent
- provider-specific Idle and Flight cycles using the shared editable Blender action/export pipeline
- Flight remains a distinct artist-facing clip instead of being renamed Walk
- automated capability isolation prevents Human and Quadruped from exposing Avian Flight
- representative automated Godot GLB and Unity FBX export coverage verifies Avian skinning plus Idle/Flight clip packaging

## Architecture closeout

Avian anatomy remains under `object_core/providers/avian*`. Shared Blender rigging, material translation, animation action generation, validation, and target adapters do not contain Avian bone names or wing/tail motion rules. The shared locomotion path only gained a provider-supplied artist-facing clip label, with `Walk` remaining the default and Avian declaring `Flight`.

The small `blender_adapter/avian_ui.py` integration is presentation-only: it exposes the Flight choice and routes it into the existing locomotion/action path. It does not own Avian anatomy, keyframes, export rules, or target-specific behavior.

## Remaining manual evidence

Automated coverage can prove deterministic motion, deformation, action creation, and file packaging, but it cannot certify that the generated wingbeat looks convincing to an artist. A Blender visual pass of Avian Idle and Flight remains a manual checkpoint. Destination import/playback beyond the representative automated file checks remains release-hardening evidence rather than a provider-architecture blocker.
