# SPDX-License-Identifier: GPL-3.0-or-later
"""Portable JSON exchange contracts for external Modify workflows."""

import json

from .components import component_document, component_from_document
from .modification import ComponentOperation, ModificationRequest, SemanticOperation
from .objects import get_provider


INSPECTION_SCHEMA = "asset-assistant.modify-inspection/v3"
REQUEST_SCHEMA = "asset-assistant.modify-request/v3"
LEGACY_REQUEST_SCHEMAS = (
    "asset-assistant.modify-request/v1",
    "asset-assistant.modify-request/v2",
)


def _json_value(value):
    if isinstance(value, tuple):
        if value and all(isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], str) for item in value):
            return {key: _json_value(item) for key, item in value}
        return [_json_value(item) for item in value]
    return value


def semantic_operation_document(operation):
    return {
        "operation": operation.operation,
        "target": operation.target,
        "arguments": {key: _json_value(value) for key, value in operation.arguments},
    }


def component_operation_document(operation):
    return {
        "operation": operation.operation,
        "component_id": operation.component_id,
        "component": None if operation.component is None else component_document(operation.component),
    }


def inspection_document(snapshot):
    """Return a JSON-serializable inspection document for an Asset Assistant snapshot."""
    provider = get_provider(snapshot.provider_key)
    executable = set(getattr(provider, "semantic_apply_capabilities", ()))
    targets = [
        {
            "key": target.key,
            "label": target.label,
            "kind": target.kind,
            "operations": list(target.operations),
            "executable_operations": [operation for operation in target.operations if (target.key, operation) in executable],
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
            "applied_semantic_operations": [semantic_operation_document(operation) for operation in snapshot.semantic_operations],
            "attached_components": [component_document(record) for record in snapshot.components],
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
            "component_operations": [],
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


def _component_operations(document):
    raw = document.get("component_operations", [])
    if not isinstance(raw, list):
        raise TypeError("component_operations must be a JSON array")
    result = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise TypeError("component_operations[" + str(index) + "] must be a JSON object")
        operation = item.get("operation")
        component_id = item.get("component_id")
        component_raw = item.get("component")
        if not isinstance(operation, str) or not operation.strip():
            raise ValueError("component operation name must be a nonempty string")
        if not isinstance(component_id, str) or not component_id.strip():
            raise ValueError("component operation id must be a nonempty string")
        component = None
        if component_raw is not None:
            component = component_from_document(component_raw)
        result.append(ComponentOperation(operation.strip(), component_id.strip(), component))
    return tuple(result)


def request_from_document(document, snapshot):
    """Validate a returned request document against the currently inspected asset."""
    if not isinstance(document, dict):
        raise TypeError("Modify request file must contain a JSON object")
    schema = document.get("schema")
    if schema != REQUEST_SCHEMA and schema not in LEGACY_REQUEST_SCHEMAS:
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

    legacy_v1 = schema == "asset-assistant.modify-request/v1"
    semantic = () if legacy_v1 else _semantic_operations(document)
    components = _component_operations(document) if schema == REQUEST_SCHEMA else ()
    return ModificationRequest(
        parameter_changes=tuple(parameter_changes.items()),
        animation_export_names=tuple(animation_names.items()),
        semantic_operations=semantic,
        component_operations=components,
    )


def request_from_json(payload, snapshot):
    try:
        document = json.loads(payload)
    except json.JSONDecodeError as error:
        raise ValueError("Modify request is not valid JSON: " + str(error)) from None
    return request_from_document(document, snapshot)
