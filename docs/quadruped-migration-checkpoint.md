# Quadruped migration checkpoint

The canonical four-legged provider identity is now **Quadruped** across provider modules, registry key, generated mesh metadata, generated material/texture names, tests, and current documentation.

New assets store `object_type="quadruped"`. Existing generated assets saved with the historical pre-Quadruped provider key are accepted as migration input, rewritten to the canonical root/mesh metadata when resolved, and then handled by the Quadruped provider.

The next provider milestone is **Avian**, using canonical `avian` naming from its first implementation.
