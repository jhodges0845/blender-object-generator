# Asset Assistant Roadmap

This is the working source of truth for current development priorities. Before continuing development, verify live GitHub main, open PRs, and CI state rather than assuming the state recorded here is still current.

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

## Development / CI rules

Main is protected and changes go through branches/PRs. Required CI covers Python 3.9, 3.10, 3.11, 3.12 with coverage plus Blender 5.2.1. Blender 2.92.0 is no longer a supported or required runtime; new development should target Blender 5.2.1 rather than carrying legacy compatibility work that would constrain the current architecture. During the current production-component phase, successful PRs are authorized to merge automatically after all required checks pass. After creating a PR, wait about one minute before the first CI inspection. On failure, inspect and fix the exact failing job rather than guessing. Never create a release or tag without explicit approval.

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

Keep initial scope deliberately small until the hands-on round trip confirms UX. Do not create separate special-purpose workflows for hair, clothing, and accessories when the existing Generate/Import -> behavior -> attachment -> validate/save/export workflow can handle them.

### Shared component behavior

- [x] Portable behavior profiles: static, rigid, parent-skinned, self-rigged, physics-assisted.
- [x] Backward-compatible behavior inference for existing component records.
- [x] Expose currently executable behavior selection through the existing Generate/Import component workflow rather than a new parallel UI.
- [x] Working-state validation gate before editable save for base/component/ownership integrity.
- [x] Fresh target validation remains mandatory before destination export.

### External asset adoption

Generation is not required. Asset Assistant should inspect recognizable external geometry, rigs, materials, weights, animations and attachments before claiming management rights. Adoption is preservation-first: never silently claim artist-authored rigs, materials, animation curves, geometry, weights, NLA, drivers, or unrelated objects. Unsupported structures should report reduced capability or blocked adoption rather than force regeneration.

- [x] Imported rigid artist mesh adoption.
- [x] Imported parent-rig-skinned mesh adoption.
- [x] Existing Generate entry stage can adopt a selected external mesh as Hair, Clothing, or Accessory with Static, Rigid, or Parent-Skinned behavior where supported.
- [ ] General external-object inspection/adoption entry point: inspect richer external scenes before claiming ownership.
- [ ] Report supported/reduced-capability/blocked adoption state instead of forcing regeneration.
- [ ] Adopt recognizable external rigs/materials/weights while preserving artist ownership boundaries.
- [ ] Reuse first-class imported animation registration for external Actions.

### First production proofs

1. **Accessory proof implemented — PR #161:** generated Ring/Bracelet is a separate lightweight component asset with editable radius/thickness, Static/Rigid behavior and root/bone attachment. Imported meshes use the same entry stage and lifecycle. Existing remove/replace, persistence and export paths apply; checkpoint save validates component ownership first.
2. **Hair low-cost proof implemented — PR #162:** generated Hair Shell is a separate lightweight component with editable width/depth/cap height/back length and Static/Rigid behavior. Rigged Humans default to the head bone; unrigged assets fall back to asset-root attachment. It requires no simulation or extra bones.
3. **Hair bone-driven tier implemented — PR #163:** rigged Humans can choose Parent-Skinned/Bone-Driven hair. The cap follows `head`; longer rear hair blends through `neck` and `torso`, producing real low-cost deformation during character motion without physics or an extra component rig. Static/Rigid remains available as the cheaper fallback. PR #163 merged with all six checks green; main was `40f464364bf06c97aa2e94c38af81f871ae76d13` immediately afterward.
4. **Clothing proof active — PR #164 / `feature/clothing-production-proof`:** generated Basic Shirt is a separate lightweight parent-rig-skinned Human component with fit ease/length controls and torso/neck weighting. It appears in the existing Generate -> Reusable components area, uses no extra rig or physics, reuses component persistence/validation/save/export, and leaves materials independently editable. **Verify PR #164 and CI live before continuing; do not assume it is still open or unmerged.**
5. **Self-rigged accessory proof:** mechanical gauntlet-style contract with independent rig/animation ownership; keep it generic rather than game-specific.
6. **Physics hair tier:** optional later enhancement only after the bone-driven path is visually accepted; never required for older-hardware targets.
7. Only after those proofs, generalize catalog/provider UX.

### Performance rule

Hair/accessory/clothing motion must not become a baseline runtime requirement. Prefer tiers/fallbacks: Static/Rigid cheapest, Parent-Skinned/Bone-Driven middle path, Physics-Assisted optional. Material animation such as emissive glow must not require skeletal animation. This is especially important for projects targeting older hardware.

## Animation continuity

Animations are first-class assets with stable IDs independent from Blender Action names. Generated clips are Asset Assistant-owned/reproducible. Artist/imported Actions can be registered while preserving artist curve ownership. External generated-animation refinement currently supports duration/cycle speed, strength and export name while preserving stable identity and unrelated clips. Richer provider-owned motion semantics remain later work.

A self-rigged component may eventually own its own animation set independently from character Idle/Walk/Run. Non-skeletal behaviors such as material emission, visibility, shape keys and physics must not be forced through the skeletal animation contract.

## Near-term order after PR #164

1. General external-object inspection/adoption status: supported / reduced capability / blocked before ownership transfer.
2. Reuse imported animation registration for external Actions during adoption.
3. Self-rigged generic accessory proof with independent component rig/animation ownership.
4. Optional physics-assisted hair only after bone-driven hair is visually accepted.
5. Broader component preservation/round-trip audit and manual installed-Blender validation.

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
