# SPDX-License-Identifier: GPL-3.0-or-later
"""Resolve host-independent contracts and providers in a ZIP or checkout."""
from importlib import import_module
from importlib.util import find_spec

_bundled_name = __package__ + '.object_core'
_core_name = _bundled_name if find_spec(_bundled_name) is not None else 'object_core'
_core = import_module(_core_name)
ObjectMesh = _core.ObjectMesh
Skeleton = _core.Skeleton
AssetSnapshot = import_module(_core_name + '.models.validation').AssetSnapshot
validate_asset = import_module(_core_name + '.validation').validate_asset
_objects = import_module(_core_name + '.objects')
OBJECT_TYPES = _objects.OBJECT_TYPES
get_provider = _objects.get_provider
