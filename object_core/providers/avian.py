# SPDX-License-Identifier: GPL-3.0-or-later
"""Host-independent Avian provider foundation."""

from math import isfinite

from .base import Parameter
from .avian_geometry import generate_avian_deformable_mesh
from .avian_rigging import generate_avian_skeleton, generate_avian_skin_weights


AVIAN_PARAMETERS = (
    Parameter("body_length_cm", "Body Length (cm)", 42, 12, 140),
    Parameter("body_width_cm", "Body Width (cm)", 16, 5, 60),
    Parameter("body_height_cm", "Body Height (cm)", 20, 6, 70),
    Parameter("wingspan_cm", "Wingspan (cm)", 90, 20, 320),
    Parameter("tail_length_cm", "Tail Length (cm)", 22, 4, 100),
)


def _dimensions(parameters, values):
    dimensions = {}
    for field in parameters:
        value = values[field.key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(field.label + " must be a number")
        if not isfinite(value) or not field.minimum <= value <= field.maximum:
            raise ValueError(field.label + " is outside its supported range")
        dimensions[field.key] = float(value)
    if dimensions["wingspan_cm"] <= dimensions["body_width_cm"]:
        raise ValueError("Wingspan must be wider than the body")
    return dimensions


class AvianProvider:
    """Connected deformable Avian provider foundation."""

    key, label = "avian", "Avian"
    supports_rig = True
    supports_idle = supports_locomotion = supports_run = supports_materials = False
    uses_skin_weights = True
    parameters = AVIAN_PARAMETERS

    def dimensions(self, values):
        return _dimensions(self.parameters, values)

    def mesh(self, values):
        return generate_avian_deformable_mesh(self.dimensions(values))

    def skeleton(self, values):
        return generate_avian_skeleton(self.dimensions(values))

    def skin_weights(self, mesh, values):
        skeleton = self.skeleton(values)
        return generate_avian_skin_weights(mesh, skeleton)
