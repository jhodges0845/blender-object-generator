# Modify runtime optimization

This note continues the performance audit after PR #132.

## Findings

- The Modify panel draw path does not run full ownership inspection or regenerate provider geometry on redraw. It resolves the selected generated asset/provider and renders stored status.
- Full `inspect_generated_asset()` is intentionally expensive because geometry ownership compares the live Blender mesh against reproducible provider output.
- Semantic Modify previously reproduced expected geometry three times during one apply: once in the pre-apply ownership check, once to build the requested semantic result, and once again in the post-apply ownership check.
- Parameter regeneration previously had the same kind of duplication: the staged provider mesh was built before swap, then post-apply inspection regenerated provider geometry again.
- External multi-stage Modify previously discarded the validated snapshot returned by each apply stage, then immediately performed another full UI-level inspection before planning the next stage and once more at the end.
- Imported Modify previously inspected the unchanged asset once to validate the returned request and then immediately inspected it again when entering the external apply helper.
- The post-Modify target validation refresh is a distinct read-only validation pass. It updates the view layer, inspects the current asset, applies target-specific checks, and intentionally remains fresh after mutation.

## First safe optimization

The semantic apply path now reuses the exact semantic mesh that was already generated to write the live vertices when performing its post-apply ownership validation. The post-apply validation still checks live part identities, topology, vertex coordinates, rig state, material state, animation state, and stored metadata. Only redundant provider geometry generation is skipped.

The public inspection contract is unchanged. The reuse path is private to the Blender adapter so callers cannot bypass normal ownership reproduction during ordinary inspection or pre-apply validation.

A Blender regression test asserts that semantic apply performs only the required pre-apply `_expected_mesh` reproduction; the post-apply check must reuse the already-generated semantic result.

## Second safe optimization

External Modify sequencing now carries the validated snapshot returned by each apply stage forward into planning for the next requested stage. Parameter, semantic, and metadata apply functions still perform their own authoritative pre-apply checks and return a post-apply inspected snapshot. The UI no longer throws that result away and immediately asks for the same full inspection again.

This removes redundant UI-level ownership inspections between external Modify stages and removes the extra final inspection after the last stage. No ownership or preservation check inside the apply functions is removed.

A Blender regression test covers a semantic external request and asserts that the UI performs only its required initial inspection; the apply function remains responsible for its own pre/post validation and returns the final authoritative snapshot.

## Third safe optimization

Parameter regeneration now carries the exact provider mesh used to build the staging asset into post-swap ownership validation. The live replacement geometry is still checked against that mesh for part identities, topology, vertex coordinates, coordinate scale, rig state, material state, animation state, and metadata. Only the redundant second provider geometry generation is skipped.

The pre-apply `_check_plan_matches()` inspection is unchanged and still independently reproduces the current asset before any destructive swap. The staged mesh is only reused after it has already been generated for the replacement components.

A Blender regression test asserts that parameter apply performs only the required pre-apply `_expected_mesh` reproduction; post-apply validation must reuse the staged mesh.

## Fourth safe optimization

Imported Modify now reuses the already-current asset snapshot created to validate the returned request when entering the external apply helper. The request still binds to the current asset id and provider before any mutation.

Standalone calls to the external apply helper still perform their own initial inspection when no snapshot is supplied. Parameter, semantic, and metadata apply stages still execute their authoritative pre-apply `_check_plan_matches()` inspections and post-apply validation.

The explicit target validation refresh after Modify is unchanged. This is intentional: it produces a fresh export-readiness snapshot for the mutated asset rather than reusing Modify ownership state for a different purpose.

Regression coverage verifies both paths: imported apply reuses the supplied current snapshot, while standalone helper use still inspects for itself.

## Current conclusion

The measured/inspected duplication found in the rich Modify path has now been removed without weakening preservation boundaries:

1. semantic post-apply provider mesh regeneration;
2. redundant external-stage UI inspections;
3. parameter post-swap provider mesh regeneration;
4. duplicate imported-request/helper-boundary inspection.

The combined external parameter + semantic + metadata path still performs a fresh ownership inspection inside each destructive apply stage. Those checks are intentional safety boundaries and should not be removed merely to reduce call count.

Likewise, post-Modify target validation remains a fresh read-only validation pass because export-readiness checks are not interchangeable with Modify ownership checks.

## Future profiling targets

1. Measure representative Human and Avian Generate / Inspect / Apply latency with stable instrumentation before making further runtime changes.
2. Compare CI durations across several post-split runs and record a stable baseline before adding performance thresholds.
3. Revisit combined external requests only if measured latency shows the preserved per-stage ownership checks are a material user-facing bottleneck.

Preservation and ownership checks remain authoritative; performance changes must not weaken them.
