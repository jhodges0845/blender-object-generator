# Dog animation milestone

Dog now provides portable Idle and Walk clips through the shared provider animation contract.

- Idle: subtle spine breathing, neck/head motion, and segmented tail sway.
- Walk: in-place quadruped gait with diagonal fore/hind pairing, lower-leg follow-through, spine counter-motion, neck stabilization, and tail follow-through.
- Blender remains provider-agnostic; the existing shared animation adapter consumes both clips without Dog-specific branches.

Next after animation validation: add Dog materials/surface treatment, then run the Dog 1.0 checkpoint audit for tests, docs, architecture, export validation, and manual visual review before moving to Bird.
