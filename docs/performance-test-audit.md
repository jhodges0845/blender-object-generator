# Performance and test-coverage audit

Date: 2026-09-12

This checkpoint was opened after the rich Modify and Human facial-geometry work because development feedback was becoming slower and the repository needed a fresh test/optimization review before more feature growth.

## Scope

The audit covers:

- CI/test execution topology;
- current automated coverage by subsystem;
- obvious repository/runtime hot paths introduced or amplified by recent growth;
- documentation/test gaps that should be closed before public alpha; and
- low-risk optimizations that can be made without weakening branch protection or correctness checks.

This is not a claim that every runtime path has been profiled. Where the repository provides evidence, the finding is stated as verified; where profiling is still required, it is listed as follow-up work.

## Verified CI slowdown

The clearest current slowdown is duplicated test discovery/execution in GitHub Actions.

Before this audit:

- each of the four standalone Python jobs ran `unittest discover -s tests`, so they discovered Blender tests even though most of those tests immediately skipped without `bpy`;
- each of the two Blender jobs also ran `unittest discover -s tests`, so the complete core suite was executed again inside Blender 2.92 and Blender 5.2.1;
- the recent PR #131 Python 3.9 job discovered 289 tests and skipped 109 Blender-dependent tests, demonstrating the avoidable discovery/import work in ordinary Python CI;
- the same core tests were therefore being exercised across all four Python jobs and again in both Blender jobs.

### Optimization applied in this checkpoint

CI is now scoped by responsibility while retaining the same six required matrix checks:

- standalone Python jobs discover only `tests/core`;
- Blender jobs discover only `tests/blender`;
- both supported Blender versions remain required;
- all four supported Python CI versions remain required;
- the isolated release-package test remains in the Blender matrix;
- Python 3.12 now emits an `object_core` line-coverage report so future audits have a quantitative baseline.

This removes redundant suite execution rather than deleting tests or weakening provider/Blender compatibility coverage.

## Test coverage health

### Strongly covered areas

The current suite has meaningful automated regression protection for:

- Human, Quadruped, Avian, and Box provider contracts;
- Human connected topology, UVs, proportions, joint-support geometry, head resolution, and facial landmark relationships;
- deforming skeletons and normalized/localized skin weights;
- Human/Quadruped Run and provider-specific Idle/Walk/Flight behavior;
- Avian and Human semantic Modify geometry;
- Modify planning, ownership blockers, external exchange v1/v2, persistent semantic patch state, and Blender apply paths;
- Blender generation, rigging, deformation, materials, animation, validation, UI workflow structure, and target export behavior;
- Godot/Unity/Unreal/Cura adapter behavior and packaging paths;
- deterministic/reproducible release ZIP generation.

### Coverage gaps / limits

The following remain real gaps rather than hidden green checks:

1. **No historical quantitative line-coverage baseline.** The suite was broad but CI did not measure source coverage. This checkpoint adds an `object_core` report on Python 3.12 without imposing a threshold yet.
2. **Visual quality is not unit-testable by geometry relationships alone.** Human facial readability, Avian gait quality, and future character likeness still need manual Blender checkpoints.
3. **Hair/clothing/accessory components are not implemented yet.** They therefore correctly have no executable component tests beyond blockers/contract behavior.
4. **Quadruped rich semantic Modify is not implemented yet.** Provider foundation coverage is strong, but the semantic executor remains future work.
5. **No stable performance-regression suite exists.** CI verifies correctness, not generation/inspection/apply latency. Timing thresholds should only be added after representative operations are measured enough to avoid flaky tests.
6. **Destination certification remains uneven.** Human has the strongest direct interactive evidence; broader Quadruped/Avian engine certification remains release-hardening work.

## Runtime/repository optimization audit

### Blender UI redraw

The repository already has a dedicated redraw fast path: export polling and attention state consume the stored validation snapshot instead of running the expensive inspector on every redraw. The new Modify panel does not call `inspect_generated_asset` from `draw`; inspection is operator-triggered. No new redraw-time rich-Modify regression was found in this audit.

### Modify inspection/apply

`inspect_generated_asset` intentionally reproduces expected provider geometry to verify ownership. Rich external apply may re-inspect between parameter, semantic, and animation-name stages so every destructive stage is checked against current state.

That safety model is correct, but the cost will grow as provider meshes and semantic recipes become richer. This is a **profiling target**, not an immediate optimization: before caching or removing inspections, measure generation/inspection/apply time on representative Human/Avian assets and preserve the current safety guarantees.

Potential later optimizations include caching reproducible expected meshes by provider parameters + semantic recipe during a single operator execution, or allowing apply stages to pass forward already-validated snapshots when no intervening scene mutation can invalidate them. These must be benchmarked and covered before adoption.

### Large modules

Several Blender adapter modules have grown substantially (`ui.py`, `targets.py`, `modification.py`, `modify_ui.py`). Their size is primarily a maintainability concern, not evidence of runtime slowness by itself. Split them only around stable responsibilities when doing so reduces coupling or test setup cost; avoid churn-only refactors before the current Human/component milestones.

### Repository data size

No evidence in the tracked tree suggests large generated binaries are responsible for the reported slowdown. Blender runtimes are downloaded into Actions cache rather than committed to the repository, and release artifacts are generated by workflow/scripts. The main verified performance issue in this checkpoint is test topology, not repository file size.

## Recommended order

1. Merge the CI suite-scoping optimization and establish the first `object_core` coverage baseline.
2. Compare CI duration over several PRs instead of drawing conclusions from one run/cache state.
3. Keep Human facial work behind visual checkpoints; do not increase topology indefinitely without proving visible value.
4. Before component work becomes large, add core contract tests first, then Blender integration tests only for behavior that actually requires Blender.
5. Add lightweight timing instrumentation for representative generation and Modify inspection/apply operations, initially informational rather than pass/fail.
6. Revisit module boundaries after the component contract exists, when the correct responsibility split is clearer.
7. Run the full pre-release cross-provider regression/coverage audit again after component work and the Avian/Human external Modify proofs are complete.

## Audit conclusion

The repository is not showing an architectural collapse. The provider/core/adapter boundaries and test breadth remain healthy. The immediate slowdown has a concrete CI cause: core and Blender suites were discovering/executing overlapping work across six jobs. This checkpoint removes that duplication and begins quantitative core coverage reporting without reducing required compatibility checks.

The next performance risks are likely to come from richer mesh generation and repeated preservation inspection, so those should be measured before optimization rather than guessed at.
