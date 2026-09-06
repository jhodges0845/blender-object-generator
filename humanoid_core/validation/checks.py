# SPDX-License-Identifier: GPL-3.0-or-later
"""Evaluate observations against an explicit intended use, without editing assets."""

from ..models.validation import AssetSnapshot, ValidationIssue


def validate_asset(snapshot: AssetSnapshot, *, asset_use="RIGGED", require_textures=False):
    if not isinstance(snapshot, AssetSnapshot):
        raise TypeError("snapshot must be AssetSnapshot")
    if asset_use not in ("STATIC", "RIGGED", "ANIMATED"):
        raise ValueError("asset_use must be STATIC, RIGGED, or ANIMATED")
    if not isinstance(require_textures, bool):
        raise TypeError("require_textures must be bool")
    results = []

    def add(code, status, message):
        results.append(ValidationIssue(code, status, message))

    if not snapshot.mesh_count:
        add("geometry", "ERROR", "No meshes found in this character.")
    elif snapshot.invalid_meshes:
        add("geometry", "ERROR", "Repair mesh geometry: " + "; ".join(snapshot.invalid_meshes))
    else:
        add("geometry", "PASS", "Meshes have finite vertices, faces, and closed edges.")
    if snapshot.rig_errors:
        add("rig", "ERROR", "; ".join(snapshot.rig_errors))
    elif asset_use != "STATIC" and not snapshot.has_rig:
        add("rig", "ERROR", "Add a rig in the Rigging tab.")
    else:
        add("rig", "PASS", "Rig and vertex weights found." if snapshot.has_rig else "Rig is not required for static use.")
    if asset_use == "ANIMATED" and not snapshot.has_animation:
        add("animation", "ERROR", "No keyed animation clip found. Generate an idle in Animation or add your own clip.")
    else:
        add("animation", "PASS", "Keyed clip found; review its motion." if snapshot.has_animation else "Animation is not required for this use.")
    if snapshot.missing_materials:
        add("materials", "WARN", "Assign materials here or in the game engine: " + ", ".join(snapshot.missing_materials))
    else:
        add("materials", "PASS", "Material assignments found.")
    if snapshot.missing_images:
        add("textures", "ERROR", "Missing texture data: " + "; ".join(snapshot.missing_images))
    elif require_textures and not snapshot.texture_count:
        add("textures", "ERROR", "Image textures are expected, but none were found in connected image nodes.")
    else:
        add("textures", "PASS", "Referenced image textures found." if snapshot.texture_count else "No image textures expected; material-only use selected.")
    if (require_textures or snapshot.texture_count) and snapshot.missing_uvs:
        add("uvs", "ERROR", "Add UV maps for image texture export: " + ", ".join(snapshot.missing_uvs))
    else:
        add("uvs", "PASS", "UV layers found; review unwrap quality." if require_textures or snapshot.texture_count
            else "Image textures are not in use; UVs are not required by this check.")
    for warning in snapshot.texture_warnings:
        add("texture_review", "WARN", warning)
    for warning in snapshot.transform_warnings:
        add("transforms", "WARN", warning)
    if snapshot.is_blockout:
        add("blockout", "WARN", "Separate blockout parts: review joint gaps, intersections, and deformation.")
    add("export_review", "WARN", "Target-engine export, polygon budget, shading, and animation quality need manual review.")
    return tuple(results)
