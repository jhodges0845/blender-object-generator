# Human deformation quality checks

Human 1.0 deformation work uses two complementary validation layers.

## Automated Blender regressions

CI is the default feedback loop. Blender integration tests verify that representative joints move the expected local surface without dragging the opposite side, and they now also guard basic transition-volume preservation at the neck and shoulder during deliberate bends.

These tests are intentionally structural rather than aesthetic: they catch regressions such as no deformation, cross-body influence, or a transition collapsing to a small fraction of its neutral spread.

## Manual visual inspection

`scripts/inspect_human_deformation.py` remains the visual quality harness for silhouette, readability, and artist-facing deformation quality. Because it requires a person at Blender, it should be run at deformation milestones rather than after every small PR.

A manual pass is appropriate when several meaningful deformation changes have accumulated, when an automated regression reveals a new class of failure, or before declaring the Human 1.0 deformation milestone complete.
