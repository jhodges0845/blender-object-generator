# UI / UX Slice 2 — Create and Components

This slice reorganizes the Blender adapter presentation without changing workflow behavior or ownership boundaries.

## Create hierarchy

- The Create stage remains the entry point for base asset generation.
- Existing generation properties and operators remain unchanged.
- Reusable components are grouped separately from base creation so artists can understand that hair, clothing, accessories, and adopted meshes remain independent editable pieces.
- Generated components and externally adopted components are presented as distinct choices while keeping their existing operator IDs and dialogs.
- Editable checkpoint reopening is presented as a separate continuation path rather than another creation action.

## Architecture constraints

- `object_core` remains host-independent.
- Blender-specific presentation stays in `blender_adapter`.
- No component generation, adoption, attachment, ownership, validation, or persistence behavior is reimplemented in UI code.
- Existing component operators remain the only mutation entry points used by this hierarchy.
- Later animation and export polish is intentionally outside this slice.
