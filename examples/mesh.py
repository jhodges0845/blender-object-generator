"""Run with python -m examples.mesh; optionally pass --output blockout.json."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from humanoid_core import BodyType, HumanoidSpec, generate_mesh, generate_proportions


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a humanoid blockout without Blender")
    parser.add_argument("--height", type=float, default=180, help="Height in centimeters")
    parser.add_argument("--weight", type=float, default=95, help="Weight in kilograms")
    parser.add_argument("--body-type", choices=[kind.value for kind in BodyType], default="average")
    parser.add_argument("--output", type=Path, help="Optional JSON mesh output path")
    args = parser.parse_args()
    try:
        spec = HumanoidSpec(args.height, args.weight, BodyType(args.body_type))
        mesh = generate_mesh(generate_proportions(spec))
    except (TypeError, ValueError) as error:
        parser.error(str(error))
    minimum, maximum = mesh.bounds_cm
    print(f"{args.body_type}: {args.height:g} cm, {args.weight:g} kg")
    print(f"{len(mesh.parts)} parts, {mesh.vertex_count} vertices, {mesh.face_count} faces")
    print(f"Mesh height: {maximum[2] - minimum[2]:.1f} cm; floor: {minimum[2]:.1f} cm")
    for part in mesh.parts:
        print(f"  {part.name:<18} {len(part.vertices):3} vertices  {len(part.faces):3} faces")
    if args.output:
        payload = {"units": "cm", "up_axis": "Z", "forward_axis": "Y", **asdict(mesh)}
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Saved {args.output.resolve()}")


if __name__ == "__main__":
    main()
