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

## Human 1.0 milestone result

The accumulated Human 1.0 deformation pass was reviewed interactively in Blender 5.2.1 in September 2026 using the inspection harness and closer viewport views of representative poses.

Observed result: **pass for the Human 1.0 editable blockout milestone.** The connected weighted mesh visibly follows the deforming skeleton through representative neck, shoulder, elbow, wrist, hip, knee, and ankle poses. No obvious mesh separation, detached limbs, or catastrophic joint collapse was observed. The overall neutral silhouette reads as one connected character foundation rather than the earlier multipart primitive path.

Shoulder/armpit, elbow, wrist, and other joint transitions remain visibly angular in some poses. That is recorded as a quality limitation of the intentionally low-poly foundation rather than a blocking defect for Human 1.0. Higher-fidelity topology, skinning, and anatomically smoother deformation remain future refinement work rather than requirements for this milestone.

This manual result complements, rather than replaces, the automated deformation regressions. Any future reproducible deformation regression should still receive automated coverage where practical.
