# SPDX-License-Identifier: GPL-3.0-or-later
"""Object type providers. Host adapters dispatch here without body-shape rules."""

from dataclasses import dataclass
from math import isfinite
from typing import Union
from .models import BodyType, HumanoidSpec, ObjectMesh, MeshPart
from .proportions import generate_proportions
from .geometry import generate_mesh
from .rigging import generate_skeleton
from .animation import generate_idle


@dataclass(frozen=True)
class Parameter:
    key: str
    label: str
    default: Union[float, str]
    minimum: float
    maximum: float
    choices: tuple = ()


class HumanoidProvider:
    key, label = 'humanoid', 'Humanoid'
    supports_rig = supports_idle = True
    parameters = (Parameter('height_cm', 'Height (cm)', 180, 120, 240),
                  Parameter('weight_kg', 'Weight (kg)', 95, 30, 300),
                  Parameter('body_type', 'Body Type', 'average', 0, 0,
                            tuple((v.value, v.value.title()) for v in BodyType)))

    def proportions(self, values):
        return generate_proportions(HumanoidSpec(values['height_cm'], values['weight_kg'], BodyType(values['body_type'])))

    def mesh(self, values):
        return generate_mesh(self.proportions(values))

    def skeleton(self, values):
        return generate_skeleton(self.proportions(values))

    def idle(self, duration, strength):
        return generate_idle(duration, strength)


class BoxProvider:
    key, label = 'box', 'Box'
    supports_rig = supports_idle = False
    parameters = tuple(Parameter(key, label, 100, 1, 1000) for key, label in
                       (('width_cm', 'Width (cm)'), ('depth_cm', 'Depth (cm)'), ('height_cm', 'Height (cm)')))

    def mesh(self, values):
        dimensions = []
        for field in self.parameters:
            value = values[field.key]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(field.label + ' must be a number')
            if not isfinite(value) or not field.minimum <= value <= field.maximum:
                raise ValueError(field.label + ' is outside its supported range')
            dimensions.append(value)
        width, depth, height = dimensions
        vertices = ((-width/2, -depth/2, 0), (width/2, -depth/2, 0),
                    (width/2, depth/2, 0), (-width/2, depth/2, 0),
                    (-width/2, -depth/2, height), (width/2, -depth/2, height),
                    (width/2, depth/2, height), (-width/2, depth/2, height))
        faces = ((3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))
        return ObjectMesh((MeshPart('box', vertices, faces),))


OBJECT_TYPES = {provider.key: provider for provider in (HumanoidProvider(), BoxProvider())}


def get_provider(key):
    try:
        return OBJECT_TYPES[key]
    except KeyError:
        raise ValueError('Unsupported object type: ' + str(key)) from None
