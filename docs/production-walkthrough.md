# Blender 5.2.1 production walkthrough

Use this checklist for the final hands-on validation before an alpha/release decision. Run it from a clean install of the packaged Asset Assistant add-on in Blender 5.2.1. Record any failure with the exact workflow stage and visible message; do not work around silent data loss.

## 1. Clean packaged install

1. Build or download the current `asset_assistant.zip` from the current commit.
2. In Blender 5.2.1, install/replace the add-on and enable **Asset Assistant**.
3. Start from a new file and confirm the Asset Assistant workflow panels load without errors.

Expected: the packaged add-on enables normally and the Generator/Rigging/Animations/Validation/Export workflow is available.

## 2. Generate and refine a Human

1. Generate a Human with default values.
2. Confirm the body is one editable generated asset and can be selected through the Asset Assistant target UI.
3. Use model inspection/refinement on at least one supported semantic area (for example shoulders, face or jaw).
4. Preview the proposed change before applying it.
5. Apply it and validate the working state.

Expected: the asset keeps the same identity; no unrelated geometry/material state disappears.

## 3. Add production components

Add each through the existing reusable component workflow:

- Hair Shell — test Static/Rigid and the Parent-Skinned/Bone-Driven tier on a rigged Human.
- Basic Shirt — confirm parent-skinned torso/neck following.
- Ring/Bracelet — confirm root or bone attachment.
- Mechanical Gauntlet — confirm its independent component armature and **Flex** animation exist.

Expected: components remain separate assets under the Human, attachment/behavior choices are understandable, and the gauntlet's rig/action is independent from character locomotion.

Do **not** evaluate physics hair yet. Physics-assisted hair remains gated on visual acceptance of the bone-driven tier.

## 4. External adoption safety

Create or import a simple artist-owned mesh with an artist material and inspect it for adoption.

Check at least:

1. plain external mesh -> Supported;
2. external mesh with a structure needing cleanup -> Reduced Capability;
3. generated body/already-owned or conflicting structure -> Blocked.

For a supported case, adopt it as Hair, Clothing or Accessory and confirm its material is still artist-owned/editable.

Expected: status is shown before ownership transfer; blocked/reduced cases are not silently rewritten; supported adoption preserves artist data.

## 5. Animation workflow

1. Generate **Idle**, **Walk** and **Run** for the Human.
2. Switch among them in Blender and verify the expected clip plays.
3. Rename at least one export-facing animation name in the UI.
4. If available, register an external/artist Action through the imported Action workflow.
5. Confirm the Mechanical Gauntlet's **Flex** action remains independent.

Expected: Human clip identity does not get confused with Quadruped/other providers, export names are editable without changing stable animation identity, and component animation does not replace a Human clip.

## 6. Save, close and reopen

1. Save an Asset Assistant editable checkpoint `.blend`.
2. Close the file or Blender.
3. Reopen the checkpoint through the normal workflow.
4. Verify:
   - the same Human is recognized;
   - semantic refinements are still present;
   - Hair/Shirt/Accessory/Gauntlet components remain registered;
   - artist-owned materials remain intact;
   - the gauntlet still owns one component armature and Flex action;
   - Idle/Walk/Run and any registered artist Action still have the expected names/identity.

Expected: the reopened file is immediately usable; no regeneration is required.

## 7. Target validation and engine exports

Run fresh target validation before each export.

### Godot

1. Export GLB.
2. Import into Godot.
3. Confirm the model appears correctly and Idle/Walk/Run are present and playable.
4. Check the gauntlet remains attached; inspect its independent animation data if the target workflow exposes it.

### Unity

1. Export FBX.
2. Import into Unity.
3. Confirm geometry/material/rig and Idle/Walk/Run are available.
4. Confirm adding the self-rigged gauntlet did not remove the Human clip library.

### Unreal

1. Export the Unreal bundle.
2. Import the model/skeleton FBX.
3. Import the generated clip sidecars against that skeleton.
4. Confirm Idle/Walk/Run play correctly.
5. Confirm the self-rigged component did not prevent model or clip export.

Expected: every destination gets the current saved state and the Human's clip library remains intact even with a component-owned armature present.

## 8. Cura / physical-print review

1. Use a representative Human pose.
2. Validate for Cura.
3. Export STL (and 3MF if/when exposed by the current UI).
4. Open the output in Cura and inspect connected-solid warnings, scale, wall thickness, supports and repair messages.

Expected: Asset Assistant reports geometry that still requires print preparation instead of silently producing a misleading "ready" result. A real Cura slicing review remains human-required evidence.

## 9. Final acceptance notes

Record each section as **Pass**, **Fail**, or **Needs polish**. A visual-quality issue can be a polish follow-up; ownership loss, wrong animation identity, failed reopen, destructive external adoption, broken target validation, or missing expected export data is a release blocker.

Do not create a version tag or release until the walkthrough is reviewed and release approval is explicit.
