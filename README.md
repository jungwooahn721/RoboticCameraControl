# Robotic Camera Control with SO101 Arm in Blender

This repository contains scripts and files for importing, rendering, and analyzing the SO101 robotic arm in Blender using the Phobos add-on. It focuses on background (headless) operations for automation.

## Prerequisites

- **Blender 4.5.2 LTS**: Download from [blender.org](https://www.blender.org/download/lts/3-3/). The scripts assume it's installed at `/home/minhopark/repos/repos4students/jungwooahn/RoboticCameraControl/blender-4.5.2-linux-x64/`.
- **Phobos Add-on**: Automatically installed by `import_so101.py`. Requires Python dependencies (handled by the script).
- **SO101 URDF**: Located at `SO-ARM100/Simulation/SO101/so101_new_calib.urdf`.
- **Linux Environment**: Commands are for bash.

## Files Overview

### Python Scripts
- **`import_so101.py`**: Imports the SO101 URDF into Blender using Phobos. Saves as `so101_imported.blend`.
- **`render_so101.py`**: Renders an image of the imported arm. Adds camera/light if needed. Outputs `so101_rendered.png`.
- **`check_environment.py`**: Detailed scene inspection (objects, positions, hierarchy, materials, etc.).
- **`check_scene.py`**: Simple list of objects in the scene.
- **`add_cube.py`**: Adds a cube to a new scene and saves as `output.blend`.
- **`check_cube.py`**: (Not detailed in repo; assumes similar to check scripts).
- **`render_cube.py`**: Renders `output.blend` to `render_output.png`.

### Blend Files
- **`so101_imported.blend`**: Imported SO101 arm model.
- **`output.blend`**: Scene with a cube (from `add_cube.py`).
- **`output.blend1`**: Backup or variant.

### Other
- **`memo.txt`**: Notes or logs.
- **`render_output.png`**, **`render_cube.py`**: Rendered images.
- Blender binaries and add-ons in `blender-4.5.2-linux-x64/`.

## Tutorials and How-to Guides

### 1. Import the SO101 Arm
**Goal**: Load the URDF into Blender and save the model.

**Steps**:
1. Ensure Blender and Phobos are set up.
2. Run the import script:
   ```
   cd /home/minhopark/repos/repos4students/jungwooahn/RoboticCameraControl
   ./blender-4.5.2-linux-x64/blender --background --python import_so101.py
   ```
3. This installs Phobos, imports the URDF, and saves `so101_imported.blend`.

**What Happens**:
- Phobos add-on is enabled.
- STL meshes from the URDF are loaded.
- Armature hierarchy is created for joints/links.
- File saved with 50+ objects (armatures and meshes).

**Troubleshooting**:
- If Phobos fails, check Python dependencies (numpy, scipy, etc.).
- Ensure URDF path is correct.

### 2. Render an Image of the Arm
**Goal**: Generate a visual of the imported arm.

**Steps**:
1. After importing, run the render script:
   ```
   ./blender-4.5.2-linux-x64/blender --background so101_imported.blend --python render_so101.py
   ```
2. View `so101_rendered.png` (1920x1080, Cycles engine).

**What Happens**:
- Camera positioned at (2, -2, 1) with rotation for a side view.
- Sun light added.
- Render takes ~5-10 seconds.

**Customization**:
- Edit `render_so101.py` to change camera angle, resolution, or engine (e.g., switch to EEVEE for faster renders).

### 3. Check the Scene Environment
**Goal**: Inspect objects, positions, and relationships.

**Steps**:
1. Run the check script on any blend file:
   ```
   ./blender-4.5.2-linux-x64/blender --background so101_imported.blend --python check_environment.py
   ```
2. Output includes:
   - Object list with types, locations, rotations, parents/children.
   - Materials (e.g., '3d_printed', 'sts3215').
   - Hierarchy (e.g., base_link → shoulder_link → ...).
   - Cameras, lights, constraints (none in imported file).

**Example Output Snippet**:
```
Name: base_link
  Type: ARMATURE
  Location: (0.000, 0.000, 0.000)
  Parent: None
  Children: ['shoulder_link', ...]
```

**Use Cases**:
- Verify import success.
- Debug positions or materials.

### 4. Add and Render a Cube (Example)
**Goal**: Test basic Blender operations.

**Steps**:
1. Add a cube:
   ```
   ./blender-4.5.2-linux-x64/blender --background --python add_cube.py
   ```
2. Render it:
   ```
   ./blender-4.5.2-linux-x64/blender --background output.blend --python render_cube.py
   ```
3. View `render_output.png`.

**What Happens**:
- New scene with cube, camera, and light.
- Simple render for testing.

### 5. General Usage Tips
- **Background Mode**: All scripts use `--background` for headless operation. No GUI opens.
- **Paths**: Update paths in scripts if Blender is installed elsewhere.
- **Errors**: Check terminal output for issues (e.g., missing files, add-on errors).
- **Customization**: Modify scripts for different URDFs, render settings, or checks.
- **Saving Changes**: Scripts like `render_so101.py` don't save the blend file by default. Add `bpy.ops.wm.save_as_mainfile(filepath="...")` if needed.
- **Dependencies**: Phobos requires lxml, networkx, etc. Installed automatically by `import_so101.py`.

## Example Workflow
1. Import the arm: Run `import_so101.py`.
2. Check the scene: Run `check_environment.py` on `so101_imported.blend`.
3. Render: Run `render_so101.py`.
4. View results: Open `so101_rendered.png` or `so101_imported.blend` in Blender GUI.

## Notes
- **Blend Files**: Created files are saved in the workspace. Overwrite with caution.
- **Performance**: Renders may take time; use EEVEE for speed.
- **URDF Details**: The SO101 has 8 links/joints, with STL meshes for visuals.
- **Contributing**: Update scripts as needed for your setup.

For issues, check Blender/Phobos docs or modify scripts for debugging.
