# Asset Assistant Fresh-Chat Handoff

Use this document as the starting context when continuing development in a new ChatGPT conversation. Verify live GitHub state before acting; this file records the intended architecture, workflow, completed work, and current active slice.

## Repository and workflow rules

Repository: `jhodges0845/blender-object-generator`

Main is protected. Changes go through branches and pull requests. Required CI checks are:

- Core tests — Python 3.9
- Core tests — Python 3.10
- Core tests — Python 3.11
- Core tests — Python 3.12 with coverage
- Blender integration — 2.92.0
- Blender integration — 5.2.1

For this current production-component phase, successful PRs may be merged automatically after all required checks pass. After creating a PR, wait about one minute before the first CI inspection. If CI fails, inspect and fix the exact failing job rather than guessing. Never create tags/releases without explicit approval.

## Product architecture

Asset Assistant is an artist-first 3D workflow assistant. The shared core must remain host-independent. Blender-specific behavior belongs in `blender_adapter`; anatomy/asset-specific behavior belongs in providers/components; destination-specific behavior belongs in target adapters.

Canonical workflow:

`Generate OR Import -> Inspect/Adopt -> Configure behavior/attachment -> Preview -> Validate -> Save Editable Checkpoint -> Reopen/Continue -> Validate for Target -> Export`

Important rules:

- Generation is optional. External work should be supported through explicit inspection/adoption when possible.
- Never silently claim ownership of imported rigs, materials, animation curves, geometry, weights, or other artist-authored data.
- Unsupported external structures should degrade to reduced capability rather than force regeneration.
- Hair, clothing, and accessories are separate assets, not Human body semantics.
- Component kind and component behavior are separate concepts.
- Expensive behavior is opt-in and should have lower-cost fallbacks for older hardware.
- `.blend` is the canonical editable working/checkpoint format. GLB/FBX/STL/3MF are delivery formats.
- Validation is mandatory before editable save and must be freshly repeated before destination export.

## Reusable component behavior profiles

Portable behavior profiles now include:

- `static`
- `rigid`
- `parent_skinned`
- `self_rigged`
- `physics_assisted`

Do not create separate special-purpose workflows for hair/clothing/accessories if the existing Generate/Import -> behavior -> attachment -> validate/save/export path can handle them.

Examples:

- ring: Static or Rigid
- fitted clothing: Parent-Skinned
- mechanical gauntlet: eventually Self-Rigged
- hair: Static/Rigid low-cost tier, Parent-Skinned/Bone-Driven middle tier, optional Physics-Assisted later

Non-skeletal behavior such as material emission, visibility, shape keys, and physics should not be forced into skeletal animation.

## Editable continuity and validation

Editable checkpoint support is implemented. Marked Asset Assistant `.blend` files revalidate on reopen, including Blender native File/Open and Recent Files. Ordinary unmarked `.blend` files remain side-effect free until explicitly adopted.

Checkpoint save now validates working-state ownership/continuity before writing. Target export already performs destination validation; keep that as a fresh export gate.

Manual production-character checkpoint still required before public alpha:

`Generate Human -> save/reopen -> model inspection -> external refinement -> preview/apply -> validate/save -> animation inspection -> external refinement -> preview/play/apply -> validate/save -> target validation/export`

## Model Modify

Human rich semantic Modify and external model exchange are implemented. Useful Human targets include:

- body
- torso
- shoulders
- head
- face
- jaw
- cheeks
- arm.left / arm.right
- leg.left / leg.right

Current executable semantic operations are primarily `shape` and `scale` for topology-preserving Human geometry refinement.

For aesthetic refinement of Maxine, model inspection JSON alone is not a literal visual representation. Pair the JSON with Blender viewport screenshots when making appearance decisions.

## Animation architecture

Animations are first-class assets with stable IDs independent from Action names. Generated clips are Asset Assistant-owned/reproducible. Artist/imported Actions can be registered while preserving artist curve ownership.

External generated-animation refinement is implemented for:

- duration / cycle speed
- strength
- export name

Stable animation IDs and unrelated clips are preserved. Richer provider-owned motion semantics such as torso lean, arm swing, knee lift, contact timing, and root motion are future work.

## Implemented providers / targets

Provider foundations:

- Human
- Quadruped
- Avian
- Box

Target paths:

- Godot GLB/glTF
- Unity FBX
- Unreal FBX
- Cura STL

Human, Quadruped, and Avian animation/export foundations already exist. Human, Quadruped, and Avian Run/Flight behavior follows provider capability; Avian intentionally uses Flight rather than Run.

## Component phase completed so far

### PR #160 — production component workflow foundation

Merged. Added reusable component behavior profiles, external-adoption architecture rules, older-hardware performance rule, and validation-before-save / fresh-validation-before-export documentation. A backward-compatibility regression in component record round-tripping was found and fixed before merge.

### PR #161 — first usable accessory workflow

Merged. Added:

- generated separate Ring / Bracelet accessory
- Static or Rigid behavior
- root/bone attachment
- adoption of one selected external mesh as Hair / Clothing / Accessory
- Static / Rigid / Parent-Skinned adoption where supported
- preservation of artist-owned materials
- working-state validation gate before editable checkpoint save

### PR #162 — low-cost generated hair

Merged. Added a generated separate Hair Shell with editable width, depth, cap height, and back length. Static/Rigid remains the cheapest tier. Rigged Humans default rigid hair to `bone:head`; unrigged assets fall back to asset-root attachment.

### PR #163 — bone-driven hair tier

Merged. Main after this merge was `40f464364bf06c97aa2e94c38af81f871ae76d13` at the time this handoff was written. Added Parent-Skinned/Bone-Driven hair using the existing Human rig rather than simulation or an extra component rig. Hair cap follows `head`; longer rear hair blends through `neck` and `torso`. Static/Rigid stays available as the lower-cost fallback.

## Current active PR / slice

At the time this handoff was written, the active branch is:

`feature/clothing-production-proof`

Active PR:

`#164 — Add parent-skinned clothing production proof`

Current intent of PR #164:

- generated Basic Shirt in existing Generate -> Reusable components area
- separate Clothing component, not Human body geometry
- Parent-Skinned to existing Human torso/neck rig
- editable fit ease and length controls
- no extra rig or physics
- reuse existing component persistence, validation-before-save, reopen, remove/replace, and export paths
- materials remain independently editable / not claimed
- host-independent clothing geometry/weight tests
- older-hardware performance remains baseline

Before doing anything in a fresh chat, inspect PR #164 and its CI live. Do not assume it is still open, green, failed, or merged.

## Near-term order after PR #164

After clothing proof is green/merged and the docs are synced, the next likely slices are:

1. General external-object inspection/adoption status that reports supported / reduced capability / blocked before ownership transfer.
2. Reuse imported animation registration for external Actions during adoption.
3. Self-rigged accessory proof using a generic mechanical-gauntlet-style contract with independent component rig/animation ownership. Keep it generic, not Aevum-Divide-specific.
4. Optional physics-assisted hair only after the bone-driven tier is visually accepted. Physics must never become mandatory for older-hardware targets.
5. Broader component preservation/round-trip audit and manual installed-Blender validation.

## Aevum Divide constraints relevant to Asset Assistant

Aevum Divide is now a 3D action-adventure. Asset Assistant should be capable of supporting production work for Maxine, but game-specific details must not leak into the shared core.

Performance constraint: the game must run on older hardware. Prefer opt-in tiers and graceful fallbacks:

- Low: Static/Rigid
- Medium: Parent-Skinned/Bone-Driven
- High: optional Physics-Assisted

For Maxine hair specifically, Bone-Driven is the current preferred practical baseline before considering physics.

## Fresh-chat operating instruction

When continuing in a new chat:

1. Read `docs/roadmap.md`, `docs/architecture.md`, and this file.
2. Inspect live GitHub main, open PRs, and CI before making assumptions.
3. Continue the current active PR if one exists; do not create duplicate branches/files.
4. Keep docs synced with each architectural or workflow change.
5. Preserve the one-minute wait after creating a PR before the first CI inspection.
6. Merge successful PRs automatically only within this current production-component phase authorization.
7. Stop and report at a true visual/manual checkpoint or if user intervention is required.
