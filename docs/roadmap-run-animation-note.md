# Run animation milestone

Asset Assistant treats `Run` as a first-class generated clip for Human and Quadruped.

- Human Run: faster cycle, stronger opposing leg and arm drive than Walk.
- Quadruped Run: faster four-legged cycle with stronger fore/hind limb motion plus spine, neck, and tail motion.
- Blender UI: Run controls appear in the Animations sidebar when the selected provider supports Run.
- Export: generated `Run` actions use the same clip library/export path as `Idle` and `Walk`, so Godot, Unity, and Unreal receive the clip with the engine-facing name `Run` unless the artist renames it.
- Scope: in-place locomotion only. Root-motion support remains a separate future capability.
