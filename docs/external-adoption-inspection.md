# External Adoption Inspection

Asset Assistant now has a non-destructive inspection contract for artist-authored Blender objects before ownership transfer.

`inspect_external_object(root, object)` returns one of three capability states:

- `supported` — the object matches a currently executable adoption path.
- `reduced_capability` — useful artist-authored structure was recognized, but current adoption cannot manage every detected feature safely.
- `blocked` — adoption would violate current ownership or structural safety rules.

The inspection does not reparent objects, add Asset Assistant metadata, retarget armatures, change vertex groups, claim materials, or otherwise normalize artist work.

Current detection covers mesh eligibility, existing Asset Assistant ownership, child hierarchies, armature modifiers, vertex groups, and artist materials. External rigs are intentionally reported as reduced capability instead of being silently retargeted. Multiple armature modifiers and generated body geometry are blocked.

This is the backend foundation for the roadmap's general external-object inspection/adoption entry point. The next UI slice should surface the status and reasons before the artist confirms ownership transfer, then reuse the existing rigid or parent-skinned adoption paths where fully supported.
