"""Resolve the bundled core in a release ZIP or the sibling core in a checkout."""

from importlib import import_module
from importlib.util import find_spec

_bundled_name = __package__ + ".humanoid_core"
_core_name = _bundled_name if find_spec(_bundled_name) is not None else "humanoid_core"
_core = import_module(_core_name)
_rules = import_module(_core_name + ".proportions.rules")

BodyType = _core.BodyType
HumanoidSpec = _core.HumanoidSpec
HumanoidMesh = _core.HumanoidMesh
generate_proportions = _core.generate_proportions
generate_mesh = _core.generate_mesh
MIN_HEIGHT_CM = _rules.MIN_HEIGHT_CM
MAX_HEIGHT_CM = _rules.MAX_HEIGHT_CM
MIN_WEIGHT_KG = _rules.MIN_WEIGHT_KG
MAX_WEIGHT_KG = _rules.MAX_WEIGHT_KG
