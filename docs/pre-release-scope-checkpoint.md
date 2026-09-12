# Pre-release scope checkpoint

This checkpoint records the product state after the Avian leg/Walk correction and before the final release-hardening push.

## Confirmed foundation

- Human, Quadruped, and Avian all generate through the shared provider-driven Blender workflow.
- Human has Idle / Walk / Run.
- Quadruped has Idle / Walk / Run.
- Avian now has connected legs and feet plus distinct Idle / Walk / Flight clips; Run remains intentionally unsupported.
- Avian Walk and Flight are separate artist-facing actions and export identities.
- Avian leg placement and walking motion have been visually confirmed in Blender 5.2.1.
- Representative target-export coverage exists and release-package verification has begun.
- Core/provider anatomy remains host-independent while Blender-specific workflow behavior remains in the Blender adapter.

## Two required features before first public release

### Modify workflow

Asset Assistant needs a first-class way to inspect an existing generated asset, capture the structured information needed to understand its current state, and apply targeted changes without forcing the artist to regenerate from scratch.

The intended product workflow is:

`Select existing Asset Assistant asset -> Inspect / capture current state -> describe or prepare requested changes -> apply changes through a controlled modification path -> revalidate -> continue editing/exporting`

The implementation should preserve artist-authored work wherever possible and must not silently overwrite unrelated edits, animation, materials, or other preservation boundaries. The exact transport/schema and supported first-release edit set should be designed before implementation rather than inferred ad hoc from Blender scene data.

### UI overhaul

The current UI has grown incrementally as generation, rigging, animation, validation, export, clip naming, target preparation, and provider capabilities were added. Before release, the workflow should be reorganized so a new user can understand what to do next without already knowing Asset Assistant's architecture.

The overhaul should prioritize:

- a clear end-to-end workflow hierarchy;
- obvious distinction between creating a new asset and modifying an existing one;
- provider-aware controls that show only meaningful actions;
- reduced visual clutter and repeated explanatory text;
- clear current-asset / current-step context;
- preserving access to advanced controls without making the default path feel technical;
- avoiding naming collisions/confusion with Blender's own Animation UI where practical.

Visual design should follow the workflow rather than changing core architecture to fit a panel layout.

## Revised pre-release order

1. Checkpoint and documentation sync.
2. Design and implement the Modify workflow.
3. Design and implement the UI overhaul around Generate / Modify / Rig / Animate / Validate / Export.
4. Run a full cross-provider regression, preservation, architecture, and test-coverage audit.
5. Resume release hardening: packaging, tagged release automation, documentation, and reproducible artifacts.
6. Run a clean packaged-install smoke test in Blender 5.2.1.
7. Publish the first public alpha only after the above blockers are complete.

This checkpoint intentionally makes Modify and the UI overhaul release blockers. Animation polish, exhaustive destination certification, finished anatomy, and broader provider expansion remain follow-up work unless later testing exposes a release-severity defect.
