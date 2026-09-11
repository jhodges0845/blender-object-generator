# SPDX-License-Identifier: GPL-3.0-or-later
"""Provider registry and declaration validation.

Concrete provider implementations live under ``object_core.providers`` so the
registry can remain focused on shared contracts as new asset families are added.
"""

from .providers import (
    DOG_PARAMETERS,
    HUMAN_PARAMETERS,
    BoxProvider,
    DogProvider,
    HumanExperimentalProvider,
    HumanoidProvider,
    Parameter,
)


def validate_provider(provider):
    """Validate declarations without generating assets or depending on a host."""
    for field in ("key", "label"):
        value = getattr(provider, field, None)
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Provider " + field + " must be a nonempty string")
    for field in ("supports_rig", "supports_idle", "uses_skin_weights"):
        if not isinstance(getattr(provider, field, None), bool):
            raise TypeError(provider.key + ": " + field + " must be a boolean")
    supports_locomotion = getattr(provider, "supports_locomotion", False)
    if not isinstance(supports_locomotion, bool):
        raise TypeError(provider.key + ": supports_locomotion must be a boolean")
    supports_run = getattr(provider, "supports_run", False)
    if not isinstance(supports_run, bool):
        raise TypeError(provider.key + ": supports_run must be a boolean")
    supports_materials = getattr(provider, "supports_materials", False)
    if not isinstance(supports_materials, bool):
        raise TypeError(provider.key + ": supports_materials must be a boolean")
    if provider.supports_idle and not provider.supports_rig:
        raise ValueError(provider.key + ": idle support requires rig support")
    if supports_locomotion and not provider.supports_rig:
        raise ValueError(provider.key + ": locomotion support requires rig support")
    if supports_run and not provider.supports_rig:
        raise ValueError(provider.key + ": run support requires rig support")
    if provider.uses_skin_weights and not provider.supports_rig:
        raise ValueError(provider.key + ": skin weights require rig support")

    required = ["mesh"]
    if provider.supports_rig:
        required.append("skeleton")
    if provider.supports_idle:
        required.append("idle")
    if supports_locomotion:
        required.append("locomotion")
    if supports_run:
        required.append("run")
    if provider.uses_skin_weights:
        required.append("skin_weights")
    if supports_materials:
        required.append("materials")
    for method in required:
        if not callable(getattr(provider, method, None)):
            raise TypeError(provider.key + ": required method " + method + " must be callable")

    parameters = getattr(provider, "parameters", None)
    if not isinstance(parameters, tuple):
        raise TypeError(provider.key + ": parameters must be a tuple of Parameter definitions")
    keys = set()
    for parameter in parameters:
        if not isinstance(parameter, Parameter):
            raise TypeError(provider.key + ": parameters must contain Parameter definitions")
        if not isinstance(parameter.key, str) or not parameter.key.strip() or parameter.key in keys:
            raise ValueError(provider.key + ": parameter keys must be nonempty and unique")
        keys.add(parameter.key)
    return provider


OBJECT_TYPES = {
    provider.key: validate_provider(provider)
    for provider in (HumanoidProvider(), HumanExperimentalProvider(), BoxProvider(), DogProvider())
}


def get_provider(key):
    try:
        provider = OBJECT_TYPES[key]
    except KeyError:
        raise ValueError("Unsupported object type: " + str(key)) from None
    validate_provider(provider)
    if provider.key != key:
        raise ValueError("Provider registry key does not match declared key: " + str(key))
    return provider


# Preserve the existing import surface for callers that imported these symbols
# from object_core.objects before provider implementations were split out.
__all__ = [
    "Parameter",
    "DOG_PARAMETERS",
    "DogProvider",
    "HUMAN_PARAMETERS",
    "HumanoidProvider",
    "HumanExperimentalProvider",
    "BoxProvider",
    "validate_provider",
    "OBJECT_TYPES",
    "get_provider",
]
