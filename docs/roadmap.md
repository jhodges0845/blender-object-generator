# Asset Assistant Roadmap

This is the working source of truth for current development priorities.

## Product vision

Asset Assistant is an open-source, artist-first 3D workflow assistant. Generation is optional: artists can generate, reopen, or import existing work and adopt it into the same preservation-aware workflow.

Canonical production flow:

`Generate OR Import -> Inspect/Adopt -> Configure behavior/attachment -> Preview -> Validate -> Save Editable Checkpoint -> Reopen/Continue -> Validate for Target -> Export`

## Engineering guardrails

- `object_core` remains host-independent; Blender behavior stays in `blender_adapter`.
- Providers/components own specialized semantics; shared workflow remains capability-driven.
- Hair, clothing and accessories are separate assets, never Human body semantics.
- Component kind and component behavior are independent.
- Expensive behavior is opt-in and should degrade gracefully for older hardware.
- Imported/external work is preservation-first and never silently claimed.
- Validation is mandatory before save and freshly repeated before destination export.
- `.blend` is the canonical editable checkpoint; GLB/FBX/STL/3MF are delivery formats.
- No release/tag without explicit approval.

## Completed foundation

- [x] Human, Quadruped, Avian and Box provider foundations.
- [x] Host-independent core + Blender adapter boundary.
- [x] Human/Avian semantic Modify and external model exchange.
- [x] Component records, rigid/bone attachment and parent-rig skinning.
- [x] Imported rigid and parent-skinned component adoption with artist material preservation.
- [x] Safe component remove/replace and Modify component state.
- [x] Editable `.blend` save/reopen continuity, including native Blender reopen validation.
- [x] First-class animation records and imported/artist Action registration.
- [x] External generated-animation refinement for duration/strength/export name.
- [x] Godot/Unity/Unreal/Cura target paths and six required CI checks.

## Current manual checkpoint — production character continuity

The existing hands-on checkpoint remains required before public alpha, but it no longer blocks small production-component proofs:

`Generate Human -> save/reopen -> model inspection -> external refinement -> preview/apply -> validate/save -> animation inspection -> external refinement -> preview/play/apply -> validate/save -> target validation/export`

Acceptance remains: identity survives, UI is understandable, artist-owned data is preserved, animation identity survives, and final target export contains expected state.

## Active phase — production components and external adoption

We are starting this work now rather than waiting for the manual checkpoint. Keep initial scope deliberately small until the hands-on round trip confirms UX.

### Shared component behavior

- [x] Portable behavior profiles: static, rigid, parent-skinned, self-rigged, physics-assisted.
- [x] Backward-compatible behavior inference for existing component records.
- [x] Expose currently executable behavior selection through the existing Generate/Import component workflow rather than a new parallel UI.
- [x] Working-state validation gate before editable save for base/component/ownership integrity.
- [x] Fresh target validation remains mandatory before destination export.

### External asset adoption

- [x] Imported rigid artist mesh adoption.
- [x] Imported parent-rig-skinned mesh adoption.
- [x] Existing Generate entry stage can adopt a selected external mesh as Hair, Clothing, or Accessory with Static, Rigid, or Parent-Skinned behavior where supported.
- [ ] General external-object inspection/adoption entry point: inspect richer external scenes before claiming ownership.
- [ ] Report supported/reduced-capability/blocked adoption state instead of forcing regeneration.
- [ ] Adopt recognizable external rigs/materials/weights while preserving artist ownership boundaries.
- [ ] Reuse first-class imported animation registration for external Actions.

### First production proofs

1. **Accessory proof implemented:** generated Ring/Bracelet is a separate lightweight component asset with editable radius/thickness, Static/Rigid behavior and root/bone attachment. Imported meshes use the same entry stage and lifecycle. Existing remove/replace, persistence and export paths apply; checkpoint save validates component ownership first.
2. **Hair low-cost proof active:** generated Hair Shell is a separate lightweight component with editable width/depth/cap height/back length and Static/Rigid behavior. Rigged Humans default to the head bone; unrigged assets fall back to asset-root attachment. It intentionally requires no simulation or extra bones and remains replaceable by richer hair later.
3. **Self-rigged accessory proof:** mechanical gauntlet-style contract with independent rig/animation ownership; do not make this a game-specific provider.
4. **Hair motion tier:** add bone-driven/parent-skinned motion to the same hair component workflow. Physics remains optional and layered later.
5. **Clothing proof:** parent-rig-skinned garment with explicit material ownership.
6. Only after those proofs, generalize catalog/provider UX.

### Performance rule

Hair/accessory/clothing motion must not become a baseline runtime requirement. Prefer tiers/fallbacks: static or rigid cheapest, bone-driven/skinned middle path, physics-assisted optional. Material animation such as emissive glow must not require skeletal animation.

## Provider quality follow-ups

Human visual refinement remains active: base-face/body/hand review and later provider-owned gait controls. Quadruped rich semantic Modify remains future work. Avian foundation and rich semantics are complete; further polish is evidence-driven.

## Release hardening still required

- [ ] complete real installed-Blender production-character continuity pass;
- [ ] detailed representative Human Cura slicing/physical-print review;
- [ ] broader cross-provider/component preservation audit;
- [ ] clean packaged-install smoke test in Blender 5.2.1;
- [ ] explicit version/tag/release decision and explicit approval.

## Near-term milestone

> An artist can generate **or import** a base asset/component, explicitly adopt supported external work, choose a reusable behavior/attachment profile, validate before saving, reopen and continue, refine model/animation state without losing ownership boundaries, validate again for a destination, and export — while expensive component motion remains optional for projects targeting older hardware.
