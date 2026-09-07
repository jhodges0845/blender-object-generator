# Humanoid-assumption architecture audit

This bounded audit reviews shared runtime infrastructure for assumptions that would force future providers to behave like the current Human/Humanoid provider.

## Result

No remaining concrete biped-anatomy dependency was found in shared rigging, animation inspection, validation, workflow capability gating, or target/export scoping.

The existing non-humanoid rotor regression proves the shared rigid rig, provider animation, Blender validation, and GLB export path without humanoid bone names. Box proves that a static provider can skip rigging and animation.

## Findings addressed

- The Blender mesh translator exposed `create_character()` with a `Humanoid` default even though it accepts the generic `ObjectMesh` contract. `create_asset()` is now the canonical generic entry point; `create_character` remains an alias for source compatibility.
- Core validation said `character` when reporting a missing mesh and described all multipart blockouts in joint-specific terms. Messages are now asset-neutral.
- Unity target guidance always requested humanoid/avatar mapping. Guidance now asks for rig/avatar configuration appropriate to the provider.

## Intentional compatibility names

The following are not architecture dependencies and are intentionally retained until a separately planned compatibility migration is justified:

- installed Blender module ID `humanoid_blender`;
- `humanoid.*` Blender operator identifiers;
- `scene.humanoid_settings` and `HUMANOID_*` registered class identifiers;
- legacy root generator value `humanoid_blockout`;
- legacy mesh metadata key `body_part`, while shared rigging prefers `part_name`;
- default provider key `humanoid` and Human-provider-specific models/proportion generators.

These names can look humanoid-specific in a text search, but generic runtime behavior does not branch on humanoid anatomy because of them.

## Provider-specific behavior that correctly remains

Human proportions, body types, Human mesh construction, Human skeleton layout, and the current Human idle clip are provider/domain behavior. They should not be generalized merely to remove the word `humanoid`; future providers should supply their own anatomy and motion behavior behind the provider contract.

## Remaining architecture work outside this audit

Surface/UV/print operation capabilities are still intentionally deferred until concrete workflow operations need them. Human Provider 1.0 will also require a richer deformation/skin-weight contract than the current rigid one-part/one-bone adapter. Those are capability evolution tasks, not unresolved humanoid-assumption findings from this audit.
