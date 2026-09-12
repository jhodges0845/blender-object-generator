# Modify runtime optimization

This note continues the performance audit after PR #132.

## Findings

- The Modify panel draw path does not run full ownership inspection or regenerate provider geometry on redraw. It resolves the selected generated asset/provider and renders stored status.
- Full `inspect_generated_asset()` is intentionally expensive because geometry ownership compares the live Blender mesh against reproducible provider output.
- Semantic Modify previously reproduced expected geometry three times during one apply: once in the pre-apply ownership check, once to build the requested semantic result, and once again in the post-apply ownership check.
- Parameter regeneration still has a similar follow-up opportunity: the staged provider mesh is built before swap, while post-apply inspection regenerates provider geometry again.
- External multi-stage Modify can also re-inspect between parameter, semantic, and metadata stages. Those inspections protect against stale or unsafe state and should only be reduced when equivalent preservation guarantees can be proven.

## First safe optimization

The semantic apply path now reuses the exact semantic mesh that was already generated to write the live vertices when performing its post-apply ownership validation. The post-apply validation still checks live part identities, topology, vertex coordinates, rig state, material state, animation state, and stored metadata. Only redundant provider geometry generation is skipped.

The public inspection contract is unchanged. The reuse path is private to the Blender adapter so callers cannot bypass normal ownership reproduction during ordinary inspection or pre-apply validation.

A Blender regression test asserts that semantic apply performs only the required pre-apply `_expected_mesh` reproduction; the post-apply check must reuse the already-generated semantic result.

## Next profiling targets

1. Parameter regeneration: carry the staged mesh into post-swap ownership validation rather than regenerating it.
2. External Modify sequencing: determine whether stage-result snapshots can be safely passed forward without an extra full inspection between every stage.
3. Validation refresh after Modify: measure target-adapter preparation separately before changing it, because export validation may intentionally perform work beyond Modify ownership checks.

Preservation and ownership checks remain authoritative; performance changes must not weaken them.
