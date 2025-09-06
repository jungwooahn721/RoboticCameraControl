"""Multi View Renderer Documentation

This file documents the usage of `multi_view_renderer.py`.
You can also execute this file directly (python readme_multi_view_renderer.py)
to print the same help text to the console.

SUMMARY
-------
Generates a multi‑view synthetic dataset for a single object placed at the
origin. Cameras are sampled randomly in spherical coordinates (distance,
azimuth, elevation) plus an optional roll, always looking at the (possibly
jittered) target near the object origin.

OUTPUT STRUCTURE
----------------
By default outputs are now placed under ./results . Each run creates:
results/<object_name>_render_output_YYYYmmdd_HHMMSS/
  metadata.json                # Global configuration + object stats
  00001/
    rendered_image.png         # Color (PNG)
    Image.exr                  # Full combined EXR (from compositor)
    Depth.exr (optional)       # If --depth_pass
    Normal.exr (optional)      # If --normal_pass
    camera_info.json           # Per‑view intrinsic & extrinsic data
  00002/
    ...
  ...

KEY FEATURES
------------
* Random 6-DoF views (3 positional via spherical sampling + roll).
* Configurable ranges for distance, azimuth, elevation, roll.
* Cycles or Eevee rendering.
* Optional depth & normal passes (EXR) via compositor.
* Intrinsics (focal length, FOV, principal point) recorded.
* Extrinsics in quaternion (wxyz) + Euler (XYZ) + look vector.
* Object statistics: vertex count, face count, AABB local & world.
* Reproducible sampling via --seed.

COMMAND SYNTAX
--------------
blender --background --python multi_view_renderer.py -- [ARGS]

IMPORTANT: Everything after the first `--` is passed to the script's argparse.

MANDATORY / COMMON ARGS
-----------------------
--object_source      builtin:suzanne|builtin:cube|builtin:sphere|builtin:apple|builtin:cone|builtin:cylinder|builtin:torus|builtin:plane|builtin:capsule|builtin:table|builtin:room OR path to .stl/.obj/.fbx/.glb
--object_name        Logical name used in output folder naming & metadata
--views              Number of camera samples (>=1)

CAMERA SAMPLING RANGE ARGS
--------------------------
--distance_min / --distance_max    (meters)
--elev_min / --elev_max            (degrees, inclination above(+)/below(-) XY plane)
--azim_min / --azim_max            (degrees around Z, 0° at +X, increasing CCW)
--roll_min / --roll_max            (degrees roll about viewing axis)
--jitter_target                    Random translation added to the look-at target cube (meters)

RENDER / INTRINSICS ARGS
------------------------
--resolution W H          Output resolution (pixels)
--engine cycles|eevee     Render engine (Cycles recommended for physically based)
--samples N               Samples (Cycles: path samples; Eevee: TAA samples)
--focal_length MM         Camera focal length (mm)
--sensor_width MM         Sensor width (mm) (affects FOV)
--sensor_height MM        Sensor height (mm)
--depth_pass              Enable Z pass (Depth.exr)
--normal_pass             Enable Normal pass (Normal.exr)
--seed N                  Random seed for reproducibility
--output_root PATH        Parent directory for output dataset (default 'results')

EXAMPLES
--------
1) Builtin Suzanne, 50 Cycles views with depth & normal:

  cd /home/minhopark/repos/repos4students/jungwooahn/RoboticCameraControl
  /home/minhopark/repos/repos4students/jungwooahn/RoboticCameraControl/blender-4.5.2-linux-x64/blender \
    --background --python multi_view_renderer.py -- \
    --object_source builtin:suzanne \
    --object_name doll \
    --views 50 \
    --distance_min 0.4 --distance_max 0.8 \
    --elev_min -25 --elev_max 65 \
    --azim_min 0 --azim_max 360 \
    --roll_min -10 --roll_max 10 \
    --resolution 640 480 \
    --engine cycles --samples 64 \
    --depth_pass --normal_pass --seed 42

2) External STL model, 200 views, Eevee faster draft:

  blender --background --python multi_view_renderer.py -- \
    --object_source ./meshes/doll.stl \
    --object_name doll \
    --views 200 \
    --distance_min 0.6 --distance_max 1.2 \
    --elev_min -15 --elev_max 60 \
    --azim_min 0 --azim_max 360 \
    --roll_min -5 --roll_max 5 \
    --resolution 800 800 \
    --engine eevee --samples 32 --seed 7

3) Narrow azimuth sweep only (front arc) & slight jitter:

  blender --background --python multi_view_renderer.py -- \
    --object_source builtin:cube \
    --object_name cube_demo \
    --views 30 \
    --distance_min 0.5 --distance_max 0.7 \
    --elev_min 0 --elev_max 40 \
    --azim_min -60 --azim_max 60 \
    --roll_min 0 --roll_max 0 \
    --jitter_target 0.01 \
    --resolution 512 512 \
    --engine cycles --samples 32 --seed 99

DATASET METADATA FIELDS (GLOBAL)
--------------------------------
object_name, object_source, object_stats (vertices, faces, bbox info),
config (all CLI args), blender_version, datetime, total_views, engine, completed.

PER-VIEW CAMERA INFO
--------------------
index, distance, azimuth_deg, elevation_deg, roll_deg,
camera_location, camera_quaternion_wxyz, camera_euler_xyz_deg,
look_vector, target_point, intrinsics {...}, and relative paths.

NOTES
-----
* Depth values are in Blender units (meters) from camera plane.
* Normal pass: camera space normals (Cycles) unless modified.
* If you need world-space normals, you can add a geometry node & output through compositor.
* Increase samples for cleaner Cycles images; enable denoising (not yet wired in script).
* To integrate HDRI lighting, append an environment texture node to the World.

EXTENSIONS (Ideas)
------------------
* Stratified / Fibonacci sphere sampling
* Automatic denoising toggle
* Multi-object batching
* Semantic mask pass (object index / cryptomatte)

"""

if __name__ == "__main__":
    print(__doc__)
