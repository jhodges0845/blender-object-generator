"""Software-independent character generation contracts."""

from .models import BodyType, HumanoidSpec, HumanoidProportions, HumanoidMesh, MeshPart
from .proportions import generate_proportions
from .geometry import generate_mesh

__all__ = ["BodyType", "HumanoidSpec", "HumanoidProportions", "HumanoidMesh",
           "MeshPart", "generate_proportions", "generate_mesh"]
