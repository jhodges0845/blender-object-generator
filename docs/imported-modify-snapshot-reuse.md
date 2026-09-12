# Imported Modify snapshot reuse

## Finding

The post-Modify validation refresh is already a single explicit read-only target validation pass. `BlenderOutputAdapter.prepare()` delegates to `validate()`; it does not export or write files. That refresh should stay fresh because it is the snapshot presented to the artist after Modify.

The imported-request apply path had a clearer duplicate: `ASSET_ASSISTANT_OT_modify_apply_imported.execute()` inspected the current asset so `request_from_json()` could validate the returned request against the current asset id and provider, then `_apply_external_request()` immediately inspected the same unchanged asset again before planning the first apply stage.

No scene mutation occurs between those two inspections.

## Safe optimization

Carry the operator's already-current snapshot into `_apply_external_request()` for its initial planning pass. The helper keeps its existing standalone behavior by inspecting when no snapshot is supplied.

This does not remove any apply-stage safety checks. Parameter, semantic, and metadata apply functions still perform their own authoritative `_check_plan_matches()` inspection immediately before mutation and still run their post-apply validation.

The optimization therefore removes only the redundant operator/helper boundary inspection while preserving:

- request asset-id/provider validation;
- plan blocker checks;
- per-stage pre-apply ownership verification;
- post-apply geometry/rig/material/animation verification;
- the final explicit target validation refresh shown to the artist.

## Validation-refresh profiling conclusion

Do not skip `_refresh_validation()` after Modify. It runs one target-specific read-only validation pass and produces the explicit validation snapshot used by the UI. Future work can profile individual target validators if real-world assets make that pass expensive, but there is no proven duplicate inside the refresh itself to remove now.
