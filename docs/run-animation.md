# Run animation

`Run` is a first-class generated in-place animation clip for Human 1.0 and Dog.

Human Run uses a shorter cycle and stronger opposing arm/leg motion than Walk. Dog Run uses a shorter quadruped gait with stronger fore/hind motion plus spine, neck, and tail movement.

The Blender Animations sidebar exposes Run generation when the selected provider supports it. Generated Run actions use the same stable ownership and export-name metadata as Idle and Walk, so engine exports receive `Run` by default and the artist can rename the engine-facing clip through the existing animation-name controls.

Run is currently in-place locomotion. Root motion is intentionally out of scope for this milestone.
