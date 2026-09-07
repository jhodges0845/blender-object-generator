# SPDX-License-Identifier: GPL-3.0-or-later
"""Build a self-contained Asset Assistant Blender add-on."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def build_addon():
    root = Path(__file__).resolve().parents[1]
    output = root / "dist" / "asset_assistant.zip"
    output.parent.mkdir(exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        # Source uses the host-neutral name blender_adapter. Keep the historical
        # installed module ID humanoid_blender for Blender/saved-file compatibility.
        for package in ("blender_adapter", "object_core"):
            destination = Path("humanoid_blender")
            if package == "object_core":
                destination /= "object_core"
            for source in sorted((root / package).rglob("*.py")):
                archive.write(source, (destination / source.relative_to(root / package)).as_posix())
        archive.write(root / "docs" / "blender.md", "humanoid_blender/README.md")
        archive.write(root / "docs" / "rigging.md", "humanoid_blender/rigging.md")
        archive.write(root / "docs" / "workflow.md", "humanoid_blender/workflow.md")
        archive.write(root / "docs" / "animation.md", "humanoid_blender/animation.md")
        archive.write(root / "LICENSE", "humanoid_blender/LICENSE")
        archive.write(root / "NOTICE", "humanoid_blender/NOTICE")
    return output


if __name__ == "__main__":
    print(build_addon())
