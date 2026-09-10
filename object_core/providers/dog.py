# SPDX-License-Identifier: GPL-3.0-or-later
"""Host-independent Dog/quadruped provider."""

from math import isfinite

from .base import Parameter
from .dog_animation import generate_dog_idle, generate_dog_walk
from .dog_geometry import generate_dog_deformable_mesh
from .dog_rigging import generate_dog_skeleton, generate_dog_skin_weights


DOG_PARAMETERS = (
    Parameter("body_length_cm", "Body Length (cm)", 70, 25, 140),
    Parameter("shoulder_height_cm", "Shoulder Height (cm)", 55, 15, 100),
    Parameter("body_width_cm", "Body Width (cm)", 24, 8, 55),
    Parameter("head_length_cm", "Head Length (cm)", 24, 8, 45),
    Parameter("tail_length_cm", "Tail Length (cm)", 35, 5, 80),
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
    return dimensions


class DogProvider:
    """Connected deformable quadruped provider."""

    key, label = "dog", "Dog"
    supports_rig = supports_idle = supports_locomotion = True
    uses_skin_weights = True
    supports_materials = False
    parameters = DOG_PARAMETERS

    def dimensions(self, values):
        return _dimensions(self.parameters, values)

    def mesh(self, values):
        return generate_dog_deformable_mesh(self.dimensions(values))

    def skeleton(self, values):
        return generate_dog_skeleton(self.dimensions(values))

    def skin_weights(self, mesh, values):
        skeleton = self.skeleton(values)
        return generate_dog_skin_weights(mesh, skeleton)

    def idle(self, duration, strength):
        return generate_dog_idle(duration, strength)

    def locomotion(self, duration, strength):
        return generate_dog_walk(duration, strength)
