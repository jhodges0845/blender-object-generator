# Provider naming migration

Asset Assistant uses canonical provider identities throughout current implementation and documentation:

- `Human`
- `Quadruped`
- `Avian` (next provider milestone)
- `Box`

New four-legged assets store `object_type="quadruped"`, use `quadruped` mesh-part metadata, and use Quadruped-named provider modules, materials, tests, and documentation.

Existing generated assets saved before the Quadruped migration may carry an older provider identifier. Provider lookup accepts that historical value only as a compatibility input, rewrites the generated root and matching mesh-part metadata to `quadruped`, and then proceeds through the canonical Quadruped implementation. The historical value is not a current provider identity and must not be used for new assets or new implementation code.

Avian starts directly with canonical Avian terminology; no alternate provider identity is planned.
