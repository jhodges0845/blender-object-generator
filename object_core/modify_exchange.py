# SPDX-License-Identifier: GPL-3.0-or-later
"""Portable JSON exchange contracts for external Modify workflows."""

import json

from .modification import ModificationRequest


INSPECTION_SCHEMA = "asset-assistant.modify-inspection/v1"
REQUEST_SCHEMA = "asset-assistant.modify-request/v1"


def inspection_document(snapshot):
    """Return a JSON-serializable inspection document for an Asset Assistant snapshot."""
    return {
        "schema": INSPECTION_SCHEMA,
        "asset": {
            "asset_id": snapshot.asset_id,
            "provider_key": snapshot.provider_key,
            "provider_label": snapshot.provider_label,
            "parameters": dict(snapshot.parameters),
            "animations": [
                {"clip_id": clip.clip_id, "export_name": clip.export_name}
                for clip in snapshot.animations
            ],
            "components": {
                "has_rig": snapshot.has_rig,
                "has_materials": snapshot.has_materials,
                "has_animations": snapshot.has_animations,
                "owns_geometry": snapshot.owns_geometry,
                "owns_rig": snapshot.owns_rig,
                "owns_materials": snapshot.owns_materials,
                "owns_animations": snapshot.owns_animations,
            },
            "warnings": list(snapshot.warnings),
        },
        "request_template": {
            "schema": REQUEST_SCHEMA,
            "asset_id": snapshot.asset_id,
            "provider_key": snapshot.provider_key,
            "parameter_changes": {},
            "animation_export_names": {},
            "notes": "Describe intended changes here if useful; Asset Assistant ignores notes during apply.",
        },
    }


def inspection_json(snapshot):
    return json.dumps(inspection_document(snapshot), indent=2, sort_keys=True) + "\n"


def request_from_document(document, snapshot):
    """Validate a returned request document against the currently inspected asset."""
    if not isinstance(document, dict):
        raise TypeError("Modify request file must contain a JSON object")
    if document.get("schema") != REQUEST_SCHEMA:
        raise ValueError("Unsupported Modify request schema")
    if document.get("asset_id") != snapshot.asset_id:
        raise ValueError("Modify request targets a different Asset Assistant asset")
    if document.get("provider_key") != snapshot.provider_key:
        raise ValueError("Modify request provider does not match the selected asset")

    parameter_changes = document.get("parameter_changes", {})
    animation_names = document.get("animation_export_names", {})
    if not isinstance(parameter_changes, dict):
        raise TypeError("parameter_changes must be a JSON object")
    if not isinstance(animation_names, dict):
        raise TypeError("animation_export_names must be a JSON object")

    return ModificationRequest(
        parameter_changes=tuple(parameter_changes.items()),
        animation_export_names=tuple(animation_names.items()),
    )


def request_from_json(payload, snapshot):
    try:
        document = json.loads(payload)
    except json.JSONDecodeError as error:
        raise ValueError("Modify request is not valid JSON: " + str(error)) from None
    return request_from_document(document, snapshot)
