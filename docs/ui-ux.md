# Asset Assistant UI / UX

Asset Assistant should feel native to Blender while making the end-to-end game-asset workflow easier to understand at a glance.

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

The visual pass should land incrementally so CI can prove that presentation work does not regress behavior.

1. **Product shell and current-asset context** — consistent Asset Assistant identity, clearer stage labels, and a compact read-only asset summary.
2. **Create and component hierarchy** — group creation choices, advanced settings, reusable components, and continuation actions without changing their operators. Generated and adopted components remain distinct in the UI while sharing the existing component contracts.
3. **Animation workspace** — make clip selection, preview, tuning, adoption, and naming easier to scan while preserving generated and artist-owned animation semantics.
4. **Validation and export confidence** — emphasize target, readiness, actionable validation, and the final export action without weakening validation gates.
5. **Visual compatibility checkpoint** — verify the complete sidebar in supported Blender versions and compare the implemented hierarchy against the approved concept direction.

The checkpoint ends the UI / UX phase. Further workflow or engine features belong in later phases.
