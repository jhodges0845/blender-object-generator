# Piece 3: humanoid blockout mesh

```python
from humanoid_core import BodyType, HumanoidSpec, generate_proportions, generate_mesh

spec = HumanoidSpec(180, 95, BodyType.OVERWEIGHT)
mesh = generate_mesh(generate_proportions(spec))
for part in mesh.parts:
    print(part.name, len(part.vertices), len(part.faces))
```

## Data and coordinates

`HumanoidMesh` contains an immutable tuple of `MeshPart` objects. Each part has
a unique name, a tuple of XYZ vertices, and polygon faces containing zero-based
indices into that part's vertices. Coordinates are centimeters in a right-handed
system: Z is up, positive Y is forward, and positive X is the character's left.
Faces wind counterclockwise as seen from outside. The ground is Z=0 and the
character is centered on X=0. An adapter is responsible for unit/axis conversion.

`vertex_count`, `face_count`, and `bounds_cm` provide aggregate statistics. Bounds
are the minimum and maximum XYZ corners. The data contracts check finite numeric
coordinates, face index validity, nonempty data, and unique names; they do not
claim to validate arbitrary meshes for manifoldness or self-intersection.

## Generated parts

The generator creates 15 separate closed parts with 272 vertices and 182 polygon
faces: head, neck, torso, plus left/right upper arms, forearms, hands, upper legs,
lower legs, and feet. Side names use `.left` and `.right` suffixes. Every cross
section has eight vertices. Sides are quads and end caps are convex octagons;
face count is not a triangle count. A triangle-only consumer will need to
triangulate polygons; adapters should use a consistent triangulation policy.

Torso cross sections follow the hip, waist, chest, and shoulder dimensions. The
waist sits at 35% and chest at 78% of torso height above the hip plane. Head
sections give a simple chin and crown. Limb sections taper toward extremities;
hands are flattened blocks without fingers. Feet project toward positive Y.

The arms point outward 30 degrees from vertical in the XZ plane, giving a neutral
A-pose. Legs are straight, with hip centers one quarter of the hip width from
the centerline. Segment endpoints preserve the calculated limb lengths. All
parts share world coordinates, allowing an adapter to place them without adding
its own body-placement rules.

## Limits

This is a blockout for reviewing proportions. Parts may overlap at joints and
some extreme inputs may cause additional intersections. The overall humanoid
is not a single welded surface. There are no UVs, facial features, fingers,
materials, normals, rig, or skin weights. Tapered quads may be nonplanar.
Production topology and joint deformation are future work.

The generator takes `HumanoidProportions` directly, including artist-adjusted
dimensions. Its overall height and symmetry are tested over the initial
proportion generator's supported range. Arbitrary custom dimensions can produce
implausible shapes or place hands below the feet; anatomical validity is not
enforced by the data contract.

## Run and inspect

From the repository root:

```powershell
python -m examples.mesh --height 180 --weight 95 --body-type overweight
python -m unittest discover -s tests -v
```

To save inspectable mesh data, use:

```powershell
python -m examples.mesh --body-type muscular --output blockout.json
```

The optional JSON file includes units and axis conventions as well as every
part's vertices and faces. The output's parent folder must already exist; an
existing output file will be replaced. This is a debugging example, not a stable
interchange format. The Blender adapter from piece 4 creates editable objects; see
[installation](blender.md).
