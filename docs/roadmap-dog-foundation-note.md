# Dog Provider 1.0 foundation

Dog is the active provider milestone after Human 1.0. The first phase intentionally stays in `object_core`: define quadruped-specific parameters, generate a deterministic editable blockout, register through the generic provider registry, and cover the contract with standalone tests.

This phase deliberately does not add rigging, animation, materials, or Blender-specific Dog branches. Those capabilities should be added only after the basic non-Human provider path is proven through the existing architecture.

Next after this foundation: exercise Dog through Blender generation and workflow gating, then build the connected deformable quadruped mesh, skeleton, skin weights, surface, and animation in focused increments.
