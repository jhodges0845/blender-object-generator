# Asset Assistant sidebar overhaul

Asset Assistant uses one Blender sidebar category named **Asset Assistant**. The artist workflow is presented in the same order the asset moves through the tool:

1. Generate
2. Modify
3. Rig
4. Animate
5. Validate
6. Export

This keeps the product in one place instead of scattering stages across separate sidebar tabs. Existing operator and panel identifiers remain stable for saved files and scripts; only artist-facing labels, category placement, and ordering change.

## Interaction rules

- The current Asset Assistant asset remains selected through the shared target control.
- Generate creates a new asset and never overwrites an existing one.
- Modify is preservation-first: inspect, preview, then apply.
- Rig and Animate only show actions supported by the selected provider.
- Validate is the explicit readiness checkpoint.
- Export is the final stage and continues to gate file creation on validation/readiness.
- Generated animation export-name controls remain nested under Animate.

This is the pre-release navigation baseline. Future UI polish should preserve the six-stage mental model rather than adding new top-level workflow tabs.