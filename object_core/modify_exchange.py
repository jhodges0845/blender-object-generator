# SPDX-License-Identifier: GPL-3.0-or-later
"""Portable JSON exchange contracts for external Modify workflows."""

import json

from .modification import ModificationRequest, SemanticOperation
from .objects import get_provider


INSPECTION_SCHEMA = "asset-assistant.modify-inspection/v2"
REQUEST_SCHEMA = "asset-assistant.modify-request/v2"
LEGACY_REQUEST_SCHEMA = "asset-assistant.modify-request/v1"


def _json_value(value):
    if isinstance(value, tuple):
        if value and all(isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], str) for item in value):
            return {key: _json_value(item) for key, item in value}
        return [_json_value(item) for item in value]
    return value


def _semantic_document(operation):
    return {
        "operation": operation.operation,
        "target": operation.target,
        "arguments": {key: _json_value(value) for key, value in operation.arguments},
    }


def inspection_document(snapshot):
    """Return a JSON-serializable inspection document for an Asset Assistant snapshot."""
    provider = get_provider(snapshot.provider_key)
    targets = [
        {
            "key": target.key,
            "label": target.label,
            "kind": target.kind,
            "operations": list(target.operations),
        }
        for target in getattr(provider, "semantic_targets", ())
    ]
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
            "semantic_targets": targets,
            "semantic_operations": [
                _semantic_document(operation) for operation in snapshot.semantic_operations
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
            "semantic_operations": [],
            "notes": "Describe intended changes here if useful; Asset Assistant ignores notes during apply.",
        },
    }


def inspection_json(snapshot):
    return json.dumps(inspection_document(snapshot), indent=2, sort_keys=True) + "\n"


def _semantic_operations(document):
    raw = document.get("semantic_operations", [])
    if not isinstance(raw, list):
        raise TypeError("semantic_operations must be a JSON array")
    result = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise TypeError("semantic_operations[" + str(index) + "] must be a JSON object")
        operation = item.get("operation")
        target = item.get("target")
        arguments = item.get("arguments", {})
        if not isinstance(operation, str) or not operation.strip():
            raise ValueError("semantic operation name must be a nonempty string")
        if not isinstance(target, str) or not target.strip():
            raise ValueError("semantic operation target must be a nonempty string")
        if not isinstance(arguments, dict):
            raise TypeError("semantic operation arguments must be a JSON object")
        result.append(SemanticOperation(operation.strip(), target.strip(), tuple(arguments.items())))
    return tuple(result)


def request_from_document(document, snapshot):
    """Validate a returned request document against the currently inspected asset."""
    if not isinstance(document, dict):
        raise TypeError("Modify request file must contain a JSON object")
    schema = document.get("schema")
    if schema not in (REQUEST_SCHEMA, LEGACY_REQUEST_SCHEMA):
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

    semantic = () if schema == LEGACY_REQUEST_SCHEMA else _semantic_operations(document)
    return ModificationRequest(
        parameter_changes=tuple(parameter_changes.items()),
        animation_export_names=tuple(animation_names.items()),
        semantic_operations=semantic,
    )


def request_from_json(payload, snapshot):
    try:
        document = json.loads(payload)
    except json.JSONDecodeError as error:
        raise ValueError("Modify request is not valid JSON: " + str(error)) from None
    return request_from_document(document, snapshot)
