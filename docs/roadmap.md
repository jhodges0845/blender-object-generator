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

Main is protected and changes go through branches/PRs. Required CI covers Python 3.9, 3.10, 3.11 and 3.12 plus Blender 5.2.1 integration coverage. Blender 2.92.0 is no longer a supported or required runtime. Blender CI also performs a real component `.blend` save/reopen smoke test and an isolated packaged-add-on smoke test. During the current production-hardening phase, successful PRs are authorized to merge after all required checks pass. On failure, inspect and fix the exact failing job rather than guessing. Never create a release or tag without explicit approval.

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
- [x] Godot/Unity/Unreal/Cura target adapters with automated Blender 5.2.1 coverage.
- [x] Real `.blend` reopen smoke coverage for base asset identity, self-rigged component ownership and stable animation identity.

## Current manual checkpoint — production character continuity

Automated implementation is now at the hands-on production checkpoint. Follow [production walkthrough](production-walkthrough.md) in Blender 5.2.1 before public alpha.

Acceptance remains: identity survives, UI is understandable, artist-owned data is preserved, animation identity survives, components remain independently manageable, and destination exports contain expected state.

## Production components and external adoption

Keep the shared workflow capability-driven. Do not create separate special-purpose workflows for hair, clothing and accessories when the existing Generate/Import -> behavior -> attachment -> validate/save/export workflow can handle them.

### Shared component behavior

- [x] Portable behavior profiles: static, rigid, parent-skinned, self-rigged, physics-assisted.
- [x] Backward-compatible behavior inference for existing component records.
- [x] Expose currently executable behavior selection through the existing Generate/Import component workflow rather than a new parallel UI.
- [x] Working-state validation gate before editable save for base/component/ownership integrity.
- [x] Fresh target validation remains mandatory before destination export.
- [x] Self-rigged component lifecycle validation and cleanup preserve unrelated artist Actions.
- [x] Character Idle/Walk/Run export remains functional when component-owned armatures are present.

### External asset adoption

Generation is not required. Asset Assistant inspects external work before claiming management rights. Adoption is preservation-first: never silently claim artist-authored rigs, materials, animation curves, geometry, weights, NLA, drivers, or unrelated objects. Unsupported structures report reduced capability or blocked adoption rather than force regeneration.

- [x] Imported rigid artist mesh adoption.
- [x] Imported parent-rig-skinned mesh adoption.
- [x] Existing Generate entry stage can adopt a selected external mesh as Hair, Clothing, or Accessory with Static, Rigid, or Parent-Skinned behavior where supported.
- [x] General external-object inspection entry point before ownership transfer — PR #165.
- [x] Supported / reduced-capability / blocked status surfaced before adoption — PR #166.
- [x] Reuse first-class imported animation registration for external Actions — PR #167.
- [ ] Expand safe reduced-capability adoption for recognizable external rigs/hierarchies without destructive retargeting. Current reduced cases remain preservation-first and may require artist cleanup.

### First production proofs

1. **Accessory proof — PR #161:** generated Ring/Bracelet is a separate lightweight component with editable radius/thickness, Static/Rigid behavior and root/bone attachment.
2. **Hair low-cost proof — PR #162:** generated Hair Shell is a separate lightweight component with editable width/depth/cap height/back length and Static/Rigid behavior.
3. **Hair bone-driven tier — PR #163:** rigged Humans can choose Parent-Skinned/Bone-Driven hair using head/neck/torso weighting without physics or an extra component rig.
4. **Clothing proof — PR #164 merged:** generated Basic Shirt is a separate lightweight parent-rig-skinned Human component with fit ease/length controls and torso/neck weighting.
5. **Self-rigged accessory proof completed:** generic Mechanical Gauntlet owns its own armature and Flex action independently from character locomotion. Lifecycle hardening landed in PR #169; multi-rig export preservation landed in PR #170; real reopen proof landed in PR #171.
6. **Physics hair tier:** optional later enhancement only after the bone-driven path is visually accepted; never required for older-hardware targets.
7. Generalize catalog/provider UX only after the production walkthrough provides evidence that the shared workflow is understandable.

### Performance rule

Hair/accessory/clothing motion must not become a baseline runtime requirement. Prefer tiers/fallbacks: Static/Rigid cheapest, Parent-Skinned/Bone-Driven middle path, Physics-Assisted optional. Material animation such as emissive glow must not require skeletal animation. This is especially important for projects targeting older hardware.

## Animation continuity

Animations are first-class assets with stable IDs independent from Blender Action names. Generated clips are Asset Assistant-owned/reproducible. Artist/imported Actions can be registered while preserving artist curve ownership. External generated-animation refinement supports duration/cycle speed, strength and export name while preserving stable identity and unrelated clips.

Self-rigged components can own an independent animation/rig lifecycle without being folded into the character Idle/Walk/Run library. Non-skeletal behaviors such as material emission, visibility, shape keys and physics must not be forced through the skeletal animation contract.

## Automated hardening completed for the manual checkpoint

- [x] External adoption status and imported Action registration.
- [x] Self-rigged component proof and owned-rig/action cleanup boundaries.
- [x] Base character multi-clip export with a second component-owned armature present.
- [x] Real Blender 5.2.1 `.blend` save/reopen smoke for component and animation identity.
- [x] Blender 5.2.1 packaged add-on build and isolated package smoke test in CI.
- [x] Python 3.9-3.12 core tests and Blender 5.2.1 integration suite green.

## Manual / evidence-gated work remaining

- [ ] Complete the installed-Blender production walkthrough in Blender 5.2.1.
- [ ] Visually accept/reject the bone-driven hair tier before any physics-hair work.
- [ ] Perform representative Human Cura slicing/physical-print review.
- [ ] Verify Godot, Unity and Unreal output from the current packaged build, including Idle/Walk/Run and a self-rigged component case.
- [ ] Decide whether reduced-capability external-rig adoption needs expansion before alpha.
- [ ] Explicit version/tag/release decision and explicit approval.

## Provider quality follow-ups

Human visual refinement remains active: base-face/body/hand review and later provider-owned gait controls. Quadruped rich semantic Modify remains future work. Avian foundation and rich semantics are complete; further polish is evidence-driven.

## Near-term milestone

> An artist can generate **or import** a base asset/component, explicitly adopt supported external work, choose a reusable behavior/attachment profile, validate before saving, reopen and continue, refine model/animation state without losing ownership boundaries, validate again for a destination, and export — while expensive component motion remains optional for projects targeting older hardware.
