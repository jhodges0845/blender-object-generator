# Piece 4: Blender adapter

## Install and use

Blender 5.2.1 LTS is the primary test target. Blender 2.92.0 and its embedded
Python 3.7.7 remain covered as a legacy runtime. Headless integration tests pass
on both; other Blender versions and interactive UI review remain unverified.
No separate Python installation is needed to use the add-on.

1. Open Edit > Preferences > Add-ons. In modern Blender use the menu
   **Install from Disk**; in Blender 2.92 use **Install**.
2. Select `dist/object_generator.zip` from the project folder; do not unzip it.
3. Enable **Add Mesh: Object Generator**.
4. In the 3D Viewport, switch to Object Mode, press N, and open the **Generator** sidebar tab.
5. In **Generator**, choose **Object Type: Humanoid**, set Height (cm), Weight (kg),
   and Body Type, then click **Generate Model**.
6. Use View > Frame Selected (numpad decimal) to see the generated character.
7. Open **Rigging** and click **Add Basic Rig**, then **Enter Pose Mode**.
8. Open **Validation** in Object Mode to inspect the character and texture requirements.

Generation places a new character at the 3D cursor. It selects the new character
and its parts. Rigging is now a separate action on that same character.
The Humanoid collection contains an Empty parent, 15 editable mesh objects, and
an optional 16-bone armature. Move the Empty to move the whole character; select an individual
part to edit its geometry. Repeated generation creates another collection and
preserves existing characters and scene objects. Move characters apart to compare
them. Inputs affect the next generation; they do not update existing models.

Undo is enabled on the generation operator. Disabling the add-on removes its UI,
not generated objects. The rig uses rigid weights and separate parts; see
[posing and rig limitations](rigging.md).

## Uninstall or temporarily disable

1. Open **Edit > Preferences > Add-ons**.
2. Search for **Object Generator** (or **Humanoid Blockout** for version 0.2.0).
3. Uncheck the add-on to disable it immediately.
4. To uninstall its files, expand its entry with the arrow, click **Remove**,
   and confirm the removal.
5. If Auto-Save Preferences is off, choose **Save Preferences** from the
   Preferences menu. Restart Blender to finish clearing loaded modules.

Disabling or removing the add-on removes its sidebar and controls. Generated
collections and editable meshes stay in your scene, including their custom
metadata. Saved blend files, this source repository, and the downloaded ZIP
are unaffected. Generated rigs and weights also remain usable after removal. No separate Python
packages were installed by the ZIP.

## Update from an earlier version

Save your scene, remove the old add-on using the steps above, and restart Blender.
Install the rebuilt `dist/object_generator.zip`, then enable **Object Generator**.
The ZIP is now named object_generator.zip. The internal Blender module ID remains
humanoid_blender so saved settings still load. The core is now object_core.
Existing models are preserved; older humanoid generator metadata is recognized.

The 3D Viewport sidebar has separate Generator, Rigging, Animations, Validation,
and Export tabs. There is no internal stage-button row.
See [file export instructions](targets.md) for Godot, Cura, Unity and Unreal.
Export Asset opens a file browser once its target checklist is satisfied. Humanoid is
joined by Box in Object Type. Box has dimension controls and uses static validation.
The Animation tab can generate a looping idle
on a fresh rig; see [animation instructions](animation.md). See
[workflow and validation](workflow.md) for the current checks.

## Build

From the repository root:

```powershell
python -m scripts.build_blender_addon
```

The build copies the current independent core into the add-on ZIP automatically.
It also includes the full GPL license and project notices.
There is no manually maintained second copy and no pip install is needed inside
Blender. Build output is ignored by Git. Rebuild and reinstall after code changes;
restart Blender after updating an already loaded add-on to avoid stale modules.

## Test

GitHub Actions configures Python 3.9 through 3.12 and Blender 2.92.0/5.2.1
jobs on pull requests, pushes to main, and manual runs. Blender jobs verify
the official archive checksum and run `scripts/test_blender.py` headlessly.
The standalone subprocess check is skipped inside Blender; the layered-slot
test is additionally skipped on 2.92. Remote CI results must be checked on the PR.

Ordinary Python tests skip Blender integration tests explicitly:

```powershell
python -m unittest discover -s tests -v
```

Run the full suite with the installed Blender:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 2.92\blender.exe' --background --factory-startup --python-exit-code 1 --python scripts/test_blender.py
```

This uses a separate Blender process and does not alter your open scene or saved
preferences. Integration tests use private temporary scenes and clean up their
own data. They check registration, the generation operator, source geometry,
unit conversion, repeated generation, and cleanup after a simulated failure.

## Boundaries

`object_core` creates proportions and mesh data. `humanoid_blender/adapter.py`
only creates Blender data blocks from that mesh. `ui.py` handles the sidebar,
artist inputs, cursor placement, and selection. Neither adapter module changes
body-generation rules. Core imports are relative so the core can also live under
the add-on package without modifying Python's global import paths.

The adapter preserves source axes (Z up, positive Y forward). It converts source
centimeters using `0.01 / scene.unit_settings.scale_length`. At default unit scale,
a 180 cm character is 1.8 Blender units tall. At scale 0.01 it is 180 units tall.
It does not change the scene's unit system or scale. With units set to None,
the same scale convention still applies.

Mesh translation uses Blender's documented
[Mesh.from_pydata API](https://docs.blender.org/api/3.0/bpy.types.Mesh.html).
The sidebar uses registered properties, an operator, and a panel, following the
[Blender property API](https://docs.blender.org/api/main/bpy.props.html).

## Check the release ZIP

After building, run the isolated package check in a separate Blender process:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 2.92\blender.exe' --background --factory-startup --python-exit-code 1 --python scripts/test_blender_package.py
```

This extracts the ZIP into a temporary folder, removes checkout import access,
registers the bundled add-on, and generates a character. It saves
`artifacts/blockout-preview.blend` and `artifacts/blockout-preview.png` for visual
review. These generated files are ignored by Git. Existing preview outputs are
replaced. The preview scene is editable even without installing the add-on.
