# Asset Assistant UI / UX

Asset Assistant should feel native to Blender while making the end-to-end game-asset workflow easier to understand at a glance.

## Status

The first code-side UI / UX pass is implemented and protected by CI, but the live Blender visual checkpoint was **rejected**. The screenshot review showed that wrapping the existing Create, Modify, Rig, Animate, Validate, and Export panels with repeated product headers preserved functionality but created too much vertical repetition and buried the controls artists need to reach quickly.

The next UI slice is therefore a real workspace redesign rather than another decorative wrapper pass. Asset Assistant should present one compact product/current-asset header and switch the visible workspace content based on artist intent. Existing operators, validation rules, ownership behavior, export targets, and compatibility paths remain the functional contract underneath the redesigned presentation.

## Product principles

- Preserve workflow behavior. UI changes must not move generation, rigging, animation, component, validation, or export policy into presentation code.
- Keep the adapter boundary intact. Blender panels display state and invoke existing operators; `object_core` remains host-independent.
- Prefer progressive disclosure over removing expert controls.
- Make the current asset and its readiness visible once, not repeated in every workflow section.
- Use Blender-native layout, icons, boxes, labels, properties, and operators so the add-on remains familiar and compatible with supported Blender versions.
- Validation should explain readiness before export rather than surprise the artist after export.
- First-use controls such as asset type and generation must be immediately discoverable without scrolling through repeated shell content.

## Workspace direction

The primary Blender sidebar category remains **Asset Assistant**, but the visible experience should behave as one workspace rather than six independent product shells.

The approved high-level presentation direction is:

1. **Create** — choose Human, Quadruped, Avian, Box or another supported provider; configure the base asset; generate it; and access continuation actions.
2. **Animate** — generated clip library, tuning, preview, adoption and export naming.
3. **Components** — generated and adopted hair, clothing, accessories and other reusable pieces with explicit ownership behavior.
4. **Export** — target, readiness/validation, preparation, checkpoint save and final export.

Modify, Rig and Validate remain first-class workflow capabilities, but they should be surfaced contextually inside the appropriate workspace rather than forcing a repeated top-level shell for every stage. The redesign must not remove their operators or saved-file compatibility paths.

## Completed foundation

The first pass still provides useful implementation foundations that should be retained where they help the workspace redesign:

1. **Current-asset context.** Read-only target, rig, animation and component status exists and can become the single workspace header.
2. **Create/component operator grouping.** Generation, reusable generated components, adopted components and continuation actions already use existing operator contracts.
3. **Animation workspace controls.** Generated clip selection, tuning, preview, artist-action adoption and export naming are implemented while preserving ownership semantics.
4. **Validation/export confidence.** Validation summarizes errors, warnings and passes, and export gating remains protected by the existing readiness contract.
5. **Registration compatibility.** Blender 5.2.1 CI verifies add-on registration, release ZIP construction, isolated package loading, wrapper composition and lifecycle hardening.

## Visual acceptance failure — 2026-09-12

The live Blender review showed three concrete UX problems:

- Asset Assistant identity and Current Asset context were repeated in each workflow panel.
- The repeated shell consumed most of a normal-width Blender sidebar before the artist reached the actual controls.
- The result looked like six decorated legacy panels rather than the coherent Asset Assistant workspace shown in the approved concept direction.

This is a presentation failure, not a workflow-functionality failure. Automated tests correctly proved that the existing operators survived the UI pass, but they could not judge visual hierarchy or discoverability. The workspace redesign is the corrective action.

## Compatibility note

Blender 5.2.1 callback-driven enum registration requires defaults to be established at runtime rather than with an invalid string default on a dynamic `EnumProperty`. The Hair component behavior workflow preserves the user-facing `Rigid` default while registering cleanly in Blender 5.2.1.

The UI / UX phase closes only after the redesigned workspace passes a new interactive Blender visual checkpoint with the existing functional workflow intact.
