# SPDX-License-Identifier: GPL-3.0-or-later
"""Human provider implementations."""

from ..animation import generate_idle
from ..geometry import generate_deformable_mesh, generate_mesh
from ..models import BodyType, HumanoidSpec, MaterialSpec
from ..proportions import generate_proportions
from ..rigging import generate_deforming_skeleton, generate_skin_weights, generate_skeleton
from .base import Parameter


HUMAN_PARAMETERS = (
    Parameter("height_cm", "Height (cm)", 180, 120, 240),
    Parameter("weight_kg", "Weight (kg)", 95, 30, 300),
    Parameter(
        "body_type",
        "Body Type",
        "average",
        0,
        0,
        tuple((value.value, value.value.title()) for value in BodyType),
    ),
)


def _proportions(values):
    return generate_proportions(
        HumanoidSpec(
            values["height_cm"],
            values["weight_kg"],
            BodyType(values["body_type"]),
        )
    )


class HumanoidProvider:
    key, label = "humanoid", "Humanoid"
    supports_rig = supports_idle = True
    uses_skin_weights = supports_materials = False
    parameters = HUMAN_PARAMETERS

    def proportions(self, values):
        return _proportions(values)

    def mesh(self, values):
        return generate_mesh(self.proportions(values))

    def skeleton(self, values):
        return generate_skeleton(self.proportions(values))

    def idle(self, duration, strength):
        return generate_idle(duration, strength)


class HumanExperimentalProvider:
    """Opt-in Human 1.0 surface for deformation testing; not the production default."""

    key, label = "human_experimental", "Human 1.0 (Experimental)"
    supports_rig = supports_materials = True
    supports_idle = False
    uses_skin_weights = True
    parameters = HUMAN_PARAMETERS

    def proportions(self, values):
        return _proportions(values)

    def mesh(self, values):
        return generate_deformable_mesh(self.proportions(values))

    def skeleton(self, values):
        return generate_deforming_skeleton(self.proportions(values))

    def skin_weights(self, mesh, values):
        return generate_skin_weights(mesh, self.skeleton(values))

    def materials(self, values):
        # A neutral warm clay-like base is intentionally generic and easy for an
        # artist to replace. It proves portable surfacing without implying final skin.
        return (
            MaterialSpec(
                "Human Base Surface",
                ("human",),
                (0.55, 0.36, 0.28, 1.0),
                metallic=0.0,
                roughness=0.68,
            ),
        )
