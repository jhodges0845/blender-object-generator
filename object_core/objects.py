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


def validate_provider(provider):
    """Validate declarations without generating assets or depending on a host.

    This checks supported operations, not the quality or export readiness of an
    individual result. Static providers need no skeleton or animation methods.
    """
    for field in ('key', 'label'):
        value = getattr(provider, field, None)
        if not isinstance(value, str) or not value.strip():
            raise ValueError('Provider ' + field + ' must be a nonempty string')
    for field in ('supports_rig', 'supports_idle'):
        if not isinstance(getattr(provider, field, None), bool):
            raise TypeError(provider.key + ': ' + field + ' must be a boolean')
    if provider.supports_idle and not provider.supports_rig:
        raise ValueError(provider.key + ': idle support requires rig support')
    required = ['mesh']
    if provider.supports_rig:
        required.append('skeleton')
    if provider.supports_idle:
        required.append('idle')
    for method in required:
        if not callable(getattr(provider, method, None)):
            raise TypeError(provider.key + ': required method ' + method + ' must be callable')
    parameters = getattr(provider, 'parameters', None)
    if not isinstance(parameters, tuple):
        raise TypeError(provider.key + ': parameters must be a tuple of Parameter definitions')
    keys = set()
    for parameter in parameters:
        if not isinstance(parameter, Parameter):
            raise TypeError(provider.key + ': parameters must contain Parameter definitions')
        if not isinstance(parameter.key, str) or not parameter.key.strip() or parameter.key in keys:
            raise ValueError(provider.key + ': parameter keys must be nonempty and unique')
        keys.add(parameter.key)
    return provider


OBJECT_TYPES = {provider.key: validate_provider(provider) for provider in (HumanoidProvider(), BoxProvider())}


def get_provider(key):
    try:
        provider = OBJECT_TYPES[key]
    except KeyError:
        raise ValueError('Unsupported object type: ' + str(key)) from None
    validate_provider(provider)
    if provider.key != key:
        raise ValueError('Provider registry key does not match declared key: ' + str(key))
    return provider
