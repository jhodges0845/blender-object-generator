# Asset Assistant UI / UX

Asset Assistant should feel native to Blender while making the end-to-end game-asset workflow easier to understand at a glance.

## Status

The code-side UI / UX pass is complete. The six-stage workflow, polished product shell, component hierarchy, animation workspace, validation presentation, export confidence state, and Blender registration compatibility checks are implemented and protected by CI.

The remaining acceptance checkpoint is a visual review in Blender. That review should focus on spacing, density, wording, hierarchy, and whether the implemented sidebar matches the approved product direction. Visual feedback may produce small follow-up adjustments, but new workflow or engine features are outside this phase.

## Product principles

- Preserve workflow behavior. UI changes must not move generation, rigging, animation, component, validation, or export policy into presentation code.
- Keep the adapter boundary intact. Blender panels display state and invoke existing operators; `object_core` remains host-independent.
- Prefer progressive disclosure over removing expert controls.
- Make the current asset and its readiness visible before asking the artist to act.
- Use Blender-native layout, icons, boxes, labels, properties, and operators so the add-on remains familiar and compatible with supported Blender versions.
- Validation should explain readiness before export rather than surprise the artist after export.

## Navigation

The primary Blender sidebar category remains **Asset Assistant**. The ordered workflow is:

1. Create
2. Modify
3. Rig
4. Animate
5. Validate
6. Export

This preserves the existing functional workflow while using clearer creator-facing language. Existing operators, saved-file properties, and compatibility paths remain intact.

## UI / UX pass slices

The visual pass landed incrementally so CI could prove that presentation work did not regress behavior.

1. **Product shell and current-asset context — complete.** Consistent Asset Assistant identity, clearer stage labels, and a compact read-only asset summary are in place.
2. **Create and component hierarchy — complete.** Creation choices, reusable generated components, adopted components, and continuation actions are grouped without changing their operator contracts.
3. **Animation workspace — complete.** Generated clip selection, tuning, preview, artist-action adoption, and export naming are easier to scan while preserving ownership semantics.
4. **Validation and export confidence — complete.** Validation summarizes errors, warnings, and passes; results are grouped by severity; export readiness and the final export action are visually explicit without weakening validation gates.
5. **Compatibility checkpoint — code complete, visual acceptance pending.** Blender 5.2.1 CI verifies registration, the six-stage polished shell, Validate readiness framing, Export confidence framing, release ZIP construction, and isolated release ZIP loading. Final visual acceptance requires an interactive Blender review.

After visual acceptance, the UI / UX phase is closed. Further workflow or engine features belong in later phases.
