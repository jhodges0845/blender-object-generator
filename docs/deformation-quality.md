# Human deformation quality checks

Human 1.0 deformation work uses automated structural regressions as the default feedback loop and a manual Blender harness for milestone-level visual review.

## Automated Blender regressions

CI verifies representative deformation on both supported Blender runtimes. Coverage now includes shoulder, elbow, wrist, hip, knee, ankle, and neck.

The automated checks cover two complementary failure classes:

- expected local mesh movement without dragging the opposite side for side-specific poses; and
- transition-spread retention during deliberate bends so representative joint regions do not collapse to a small fraction of their neutral size.

These checks are intentionally structural rather than aesthetic. They protect against no deformation, cross-body influence, and obvious transition collapse, but they do not prove that a posed silhouette looks natural.

## Weighting and support geometry

The Human deforming path keeps influences within connected-joint neighborhoods, uses a deliberate same-side torso/upper-leg bridge at the hip, and uses softer weighting for torso/neck and torso/shoulder transitions. Geometry includes additional support around the neck and shoulder exits as well as the other representative bend regions.

Automated core tests also guard deterministic normalized weights, bounded influence counts, left/right isolation, shared neck/shoulder weights, connected topology, and the current hand/foot blockout structure.

## Manual visual inspection

`scripts/inspect_human_deformation.py` is the visual quality harness for silhouette, readability, pinching, bunching, twisting, and other artist-facing deformation issues.

Because it requires a person at Blender, it should **not** be run after every small PR. A manual pass is appropriate when:

- several meaningful geometry/weighting changes have accumulated;
- automated coverage exposes a new class of deformation failure; or
- the Human 1.0 deformation milestone is about to be declared complete.

The current plan is to batch the next manual inspection with a meaningful Human 1.0 milestone rather than interrupting UV/material work for per-PR screenshots.
