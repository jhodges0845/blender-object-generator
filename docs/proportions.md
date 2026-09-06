# Piece 2: stylized adult proportions

`generate_proportions(spec)` returns immutable `HumanoidProportions` data. It
uses no Blender APIs, randomness, or external dependencies. All dimensions are
centimeters and describe full widths/depths, not radii. This is an artistic
starting point, not a prediction of a person's anatomy or exact body mass.

## Measurement conventions

The reference pose is symmetric, upright, with straight legs and level feet.
Head height runs from chin to crown. Neck length runs from the shoulder plane
to the chin. Torso length runs from the hip joint plane to the shoulder plane
and includes the pelvis. Upper leg runs hip to knee; lower leg runs knee to
ankle. Foot height runs floor to ankle. These six vertical segments sum to
the requested standing height. Arm lengths run shoulder to elbow and elbow to
wrist; hand length runs wrist to fingertip. Foot length runs heel to toe.

Shoulder width is the distance between shoulder joints. Chest, waist, and hip
width/depth describe outer cross sections at those levels. Limb thickness is
an initial circular cross-section diameter. These dimensions are inputs to a
future mesh generator, not a complete surface or a rig definition.

## Rules

The first generator accepts heights from 120 through 240 cm and weights from
30 through 300 kg, inclusive. These are initial implementation limits chosen
for this prototype, not medical classifications or guarantees of plausible
anatomy at every combination. `HumanoidSpec` remains more general; this generator
raises `ValueError` for unsupported inputs instead of silently clamping them.

Segment lengths and head dimensions are fixed height fractions. The reference
character is 180 cm and 80 kg. Its equivalent weight at another height is:

```text
reference_weight = 80 * (height_cm / 180)^3
girth_scale = sqrt(weight_kg / reference_weight)
body_width_or_depth = height_cm * base_ratio * girth_scale * preset_factor
```

The square root scales cross-sectional area with weight while segment lengths
stay fixed. Increasing height and scaling weight by the cube of that height
change scales every output dimension uniformly. At fixed weight, a taller body
has slimmer transverse dimensions. Head dimensions, hands, and foot length do
not change with weight in this initial model.

Preset factors provide narrower forms for slim, broader shoulders/limbs and a
narrower waist for muscular, and progressively fuller waists/hips for overweight
and obese. They are not inferred from weight. Presets are not normalized to
equal volume: two presets at the same weight may have different implied volumes.
Weight is an artistic size control at this stage, not an exact mass constraint.

All calibration values live in `object_core/proportions/rules.py`. Adjusting
those values does not require changes to an adapter. The defaults will need
visual review once we generate meshes; dimensions alone cannot validate appearance.

## Try it

From the project root:

```powershell
python -m examples.proportions
```

This prints dimensions for all five presets at the same height and weight,
making the preset effects easy to compare. Edit the example's `HumanoidSpec`
to try other measurements. No geometry is generated yet.
