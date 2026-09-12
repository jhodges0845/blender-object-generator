# Semantic Modify Apply

Semantic Modify now has a provider-backed apply path rather than treating rich external requests as parameter aliases.

## Persistence model

Generated assets keep their procedural provider parameters unchanged and store a JSON semantic operation stack on the Asset Assistant root. Inspection exports the current stack. A new external request adds operations to that stack. Regeneration always starts from the provider's procedural base mesh and reapplies the complete semantic stack in order.

This keeps semantic edits reproducible and non-destructive: the system does not bake an opaque edited mesh and forget how it was produced.

## Shared vs provider responsibilities

Shared Modify code owns identity binding, request parsing, planning, ownership checks, transactional staging, rollback, persistence, and reinspection.

Providers own anatomy. A provider may expose semantic targets and optionally implement `validate_semantic_operation` and `apply_semantics`. Shared code never interprets targets such as `beak`, `face`, `hair`, or `muzzle`.

## Current concrete implementation

Avian is the first provider with semantic geometry apply. It currently supports provider-defined `shape` and `scale` edits for body, chest, head, beak, left/right wings, tail, left/right legs, and left/right feet. These edits preserve topology, so existing generated rig/animation identities can be regenerated and rebound through the established transactional Modify path.

Human and Quadruped semantic manifests remain useful for inspection and external planning, but their rich semantic apply implementations are intentionally still blocked until provider-specific geometry behavior is added.

## Product target

This architecture is intended to grow toward requests such as generic Avian -> eagle and generic Human -> a specific character design without adding those identities to the shared Modify engine. Each provider should add richer semantic targets and arguments as its geometry system becomes capable of reproducing them.
