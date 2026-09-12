# Pre-release scope checkpoint

This checkpoint began after the Avian leg/Walk correction and now tracks the final path to the first public alpha.

## Current status

- Modify design, inspection, planning, metadata apply, transactional parameter regeneration, and the first artist-facing Modify UI are implemented.
- The Blender sidebar is unified under one **Asset Assistant** tab with **Generate / Modify / Rig / Animate / Validate / Export**.
- The post-Modify/UI regression and architecture audit is in progress in `docs/post-modify-ui-audit.md`.
- After that audit is green, the remaining blockers are release/distribution hardening plus the final packaged-install Blender 5.2.1 smoke test.

## Confirmed foundation

- Human, Quadruped, and Avian all generate through the shared provider-driven Blender workflow.
- Human has Idle / Walk / Run.
- Quadruped has Idle / Walk / Run.
- Avian has connected legs and feet plus distinct Idle / Walk / Flight clips; Run remains intentionally unsupported.
- Avian Walk and Flight are separate artist-facing actions and export identities.
- Avian leg placement and walking motion have been visually confirmed in Blender 5.2.1.
- Representative target-export coverage exists and release-package verification has begun.
- Core/provider anatomy remains host-independent while Blender-specific workflow behavior remains in the Blender adapter.

## Completed pre-release blockers

### Modify workflow

The first-release Modify path now supports:

`Select existing Asset Assistant asset -> Inspect -> edit supported provider values -> Preview Changes -> Apply Changes -> revalidate`

The implementation uses a portable core snapshot/request/plan contract and Blender-side ownership inspection. Destructive provider-parameter changes stage replacement generated components before swapping them onto the existing root, and ambiguous artist-owned rig/animation relationships block automatic replacement instead of being silently discarded.

Generated animation export-name changes also have a metadata-only apply path. Omitted parameters remain unchanged.

### UI overhaul

The main workflow is now organized as one ordered Asset Assistant sidebar experience:

`Generate -> Modify -> Rig -> Animate -> Validate -> Export`

Stable historical panel/operator identifiers remain underneath for compatibility. Animation export-name controls remain nested under Animate. A real Blender 5.2.1 visual polish/usability pass is still required because automated tests can verify structure but not judge spacing or discoverability.

## Revised pre-release order

1. ~~Checkpoint and documentation sync.~~ Complete.
2. ~~Design and implement the Modify workflow.~~ Complete for the first-release boundary.
3. ~~Design and implement the UI overhaul around Generate / Modify / Rig / Animate / Validate / Export.~~ Structural overhaul complete; visual pass remains.
4. Run and close the full cross-provider regression, preservation, architecture, and test-coverage audit.
5. Resume release hardening: packaging, tagged release automation, documentation, and reproducible artifacts.
6. Run a clean packaged-install smoke test in Blender 5.2.1.
7. Publish the first public alpha only after the above blockers are complete.

Animation polish, exhaustive destination certification, finished anatomy, and broader provider expansion remain follow-up work unless later testing exposes a release-severity defect.
