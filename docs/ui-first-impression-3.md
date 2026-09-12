# UI first-impression checkpoint 3

This pass responds directly to the 2026-09-12 live Blender screenshot after PR #192.

## Goal

Make the empty Create experience feel like one intentional product flow instead of a stack of equally weighted Blender panels.

## Changes

- Hide the Current Asset empty-state card only while Create > Generate has no selected/generated asset.
- Consolidate Create Character, provider choice, quick setup, advanced controls, and Generate into one dominant card.
- Increase provider tile height and spacing.
- Increase the primary Generate action height.
- Keep Generate / Modify / Rig visible but visually secondary.
- Reduce Continue Existing to a quiet secondary action.
- Preserve the existing Current Asset summary once an asset exists or when another workflow needs it.

## Acceptance

Review in Blender before calling the UI/UX pass complete. The bar is first-glance product impact, not merely functional clarity.
