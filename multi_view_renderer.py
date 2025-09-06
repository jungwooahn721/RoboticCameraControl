#!/usr/bin/env python3
"""
Multi-view dataset renderer for a single object in Blender (headless friendly).

Usage (example):
  blender --background --python multi_view_renderer.py -- \
    --object_source builtin:suzanne \
    --object_name doll \
    --views 25 \
    --distance_min 0.35 --distance_max 0.6 \
    --elev_min -30 --elev_max 60 \
    --azim_min 0 --azim_max 360 \
    --roll_min -15 --roll_max 15 \
    --resolution 640 480 \
    --engine cycles --samples 64 \
    --depth_pass --normal_pass --seed 123

Outputs a folder: {object_name}_render_output_YYYYmmdd_HHMMSS/
  metadata.json (global scene & config info)
  00001/
    camera_info.json
    rendered_image.png
    Image.exr (Cycles full output - via compositor file output)
    Depth.exr (if depth_pass)
    Normal.exr (if normal_pass)
"""

import bpy
import math
import mathutils
import os
import sys
import json
import random
from datetime import datetime

# ---------------------------- Argument Parsing ---------------------------- #

def parse_args():
    argv = sys.argv
    if '--' in argv:
        argv = argv[argv.index('--') + 1:]
    else:
        argv = []
    import argparse
    p = argparse.ArgumentParser(description='Multi-view object renderer')
    p.add_argument('--object_source', type=str, default='builtin:suzanne',
                   help='builtin:suzanne|builtin:cube|builtin:sphere or path to mesh (.stl/.obj/.fbx/.glb)')
    p.add_argument('--object_name', type=str, default='object')
    p.add_argument('--views', type=int, default=10)
    p.add_argument('--distance_min', type=float, default=0.5)
    p.add_argument('--distance_max', type=float, default=1.0)
    p.add_argument('--elev_min', type=float, default=-30.0)
    p.add_argument('--elev_max', type=float, default=60.0)
    p.add_argument('--azim_min', type=float, default=0.0)
    p.add_argument('--azim_max', type=float, default=360.0)
    p.add_argument('--roll_min', type=float, default=0.0)
    p.add_argument('--roll_max', type=float, default=0.0)
    p.add_argument('--resolution', type=int, nargs=2, default=[800, 800])
    p.add_argument('--engine', choices=['cycles','eevee'], default='cycles')
    p.add_argument('--samples', type=int, default=32)
    p.add_argument('--seed', type=int, default=0)
    p.add_argument('--depth_pass', action='store_true')
    p.add_argument('--normal_pass', action='store_true')
    p.add_argument('--focal_length', type=float, default=50.0, help='Camera focal length (mm)')
    p.add_argument('--sensor_width', type=float, default=36.0)
    p.add_argument('--sensor_height', type=float, default=24.0)
    p.add_argument('--jitter_target', type=float, default=0.0, help='Random jitter (meters) added to look target')
    # Default output root changed to 'results' directory (auto-created) so datasets
    # no longer clutter repo root. User can still override with --output_root.
    p.add_argument('--output_root', type=str, default='results')
    args = p.parse_args(argv)
    return args

# ---------------------------- Utility Functions --------------------------- #

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def import_object(object_source, object_name):
    imported_objs = []
    if object_source.startswith('builtin:'):
        kind = object_source.split(':',1)[1]
        if kind == 'suzanne':
            bpy.ops.mesh.primitive_monkey_add()
        elif kind == 'cube':
            bpy.ops.mesh.primitive_cube_add()
        elif kind == 'sphere':
            bpy.ops.mesh.primitive_uv_sphere_add()
        elif kind == 'apple':
            # Base sphere for apple body
            bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32)
            body = bpy.context.active_object
            body.scale = (0.95, 0.95, 1.05)
            # Slight squash to suggest apple shape
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            # Add a simple red material
            mat = bpy.data.materials.new(name='AppleMaterial')
            mat.use_nodes = True
            principled = mat.node_tree.nodes.get('Principled BSDF')
            if principled:
                # Base color
                if 'Base Color' in principled.inputs:
                    principled.inputs['Base Color'].default_value = (0.8, 0.05, 0.02, 1.0)
                # Subsurface socket name may vary or be removed in simplified node; guard it
                if 'Subsurface' in principled.inputs:
                    try:
                        principled.inputs['Subsurface'].default_value = 0.05
                    except Exception:
                        pass
                if 'Roughness' in principled.inputs:
                    principled.inputs['Roughness'].default_value = 0.45
            body.data.materials.append(mat)
            # Add stem (cylinder)
            bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.4, location=(0, 0, 1.05))
            stem = bpy.context.active_object
            stem.scale = (0.3, 0.3, 1.0)
            stem.location.z += 0.1
            stem_mat = bpy.data.materials.new(name='StemMaterial')
            stem_mat.use_nodes = True
            p2 = stem_mat.node_tree.nodes.get('Principled BSDF')
            if p2:
                if 'Base Color' in p2.inputs:
                    p2.inputs['Base Color'].default_value = (0.1, 0.25, 0.05, 1.0)
                if 'Roughness' in p2.inputs:
                    p2.inputs['Roughness'].default_value = 0.8
            stem.data.materials.append(stem_mat)
            # Join stem into body for a single object
            bpy.ops.object.select_all(action='DESELECT')
            body.select_set(True)
            stem.select_set(True)
            bpy.context.view_layer.objects.active = body
            bpy.ops.object.join()
            imported_objs.append(bpy.context.active_object)
        elif kind == 'cone':
            bpy.ops.mesh.primitive_cone_add(vertices=64)
        elif kind == 'cylinder':
            bpy.ops.mesh.primitive_cylinder_add(vertices=64)
        elif kind == 'torus':
            bpy.ops.mesh.primitive_torus_add(major_segments=64, minor_segments=32)
        elif kind == 'plane':
            bpy.ops.mesh.primitive_plane_add(size=2)
        elif kind == 'capsule':  # cylinder with hemispherical ends
            bpy.ops.mesh.primitive_cylinder_add(vertices=48, depth=1.0)
            cyl = bpy.context.active_object
            # Add sphere, scale in Z then separate halves
            bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, location=(0,0,0.5))
            top = bpy.context.active_object
            top.scale = (0.5,0.5,0.5)
            bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, location=(0,0,-0.5))
            bot = bpy.context.active_object
            bot.scale = (0.5,0.5,0.5)
            bpy.ops.object.select_all(action='DESELECT')
            for o in (cyl, top, bot):
                o.select_set(True)
            bpy.context.view_layer.objects.active = cyl
            bpy.ops.object.join()
            imported_objs.append(bpy.context.active_object)
        elif kind == 'table':  # simple table: top + 4 legs
            bpy.ops.mesh.primitive_cube_add(size=2)
            top = bpy.context.active_object
            top.scale = (1.0,1.0,0.1)
            legs = []
            leg_offsets = [(0.9,0.9,-1.0),(0.9,-0.9,-1.0),(-0.9,0.9,-1.0),(-0.9,-0.9,-1.0)]
            for (lx,ly,lz) in leg_offsets:
                bpy.ops.mesh.primitive_cube_add(size=0.3, location=(lx,ly,lz))
                leg = bpy.context.active_object
                leg.scale = (0.3,0.3,1.5)
                legs.append(leg)
            bpy.ops.object.select_all(action='DESELECT')
            top.select_set(True)
            for leg in legs:
                leg.select_set(True)
            bpy.context.view_layer.objects.active = top
            bpy.ops.object.join()
            imported_objs.append(bpy.context.active_object)
        elif kind == 'room':  # inverted cube (normals inside) to act as a simple room
            bpy.ops.mesh.primitive_cube_add(size=6)
            room = bpy.context.active_object
            # Flip normals by scaling -1 on one axis & applying
            room.scale.x = -room.scale.x
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            imported_objs.append(room)
        else:
            raise ValueError(f'Unknown builtin primitive {kind}')
        obj = bpy.context.active_object
        obj.name = object_name
        imported_objs.append(obj)
    else:
        path = os.path.abspath(object_source)
        ext = os.path.splitext(path)[1].lower()
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        if ext == '.stl':
            bpy.ops.import_mesh.stl(filepath=path)
        elif ext == '.obj':
            # Blender 4.x uses wm.obj_import
            bpy.ops.wm.obj_import(filepath=path)
        elif ext == '.fbx':
            bpy.ops.import_scene.fbx(filepath=path)
        elif ext in ('.glb', '.gltf'):
            bpy.ops.import_scene.gltf(filepath=path)
        else:
            raise ValueError(f'Unsupported file extension {ext}')
        imported_objs = bpy.context.selected_objects
        for i, o in enumerate(imported_objs):
            if i == 0:
                o.name = object_name

    # Join all imported objects into one (optional) for simpler stats if >1
    if len(imported_objs) > 1:
        bpy.ops.object.select_all(action='DESELECT')
        for o in imported_objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = imported_objs[0]
        bpy.ops.object.join()
        imported_objs = [bpy.context.active_object]

    obj = imported_objs[0]

    # Set origin & move to world origin
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.location = (0.0, 0.0, 0.0)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return obj


def add_light():
    bpy.ops.object.light_add(type='SUN', location=(3, -3, 5))
    light = bpy.context.active_object
    light.data.energy = 3.0
    return light


def setup_camera(focal_length, sensor_w, sensor_h):
    bpy.ops.object.camera_add(location=(0, -2, 0.5))
    cam = bpy.context.active_object
    cam.data.lens = focal_length
    cam.data.sensor_width = sensor_w
    cam.data.sensor_height = sensor_h
    bpy.context.scene.camera = cam
    return cam


def look_at(cam, target, roll_deg=0.0):
    direction = (target - cam.location).normalized()
    # Build a rotation matrix where -Z is forward for camera, Y is up.
    # Blender camera looks along -Z.
    up = mathutils.Vector((0,0,1))
    if abs(direction.dot(up)) > 0.999:
        up = mathutils.Vector((0,1,0))
    right = direction.cross(up).normalized()
    up_corr = right.cross(direction).normalized()
    # Matrix columns: X(right), Y(up), Z(forward)
    rot_mat = mathutils.Matrix((
        (right.x, up_corr.x, -direction.x),
        (right.y, up_corr.y, -direction.y),
        (right.z, up_corr.z, -direction.z)
    ))
    cam.rotation_euler = rot_mat.to_euler()
    if roll_deg != 0.0:
        # Roll around viewing axis (-Z local) -> rotate Euler.roll component
        # Convert to matrix, apply roll.
        current = cam.matrix_world.to_3x3()
        axis = (cam.matrix_world @ mathutils.Vector((0,0,-1)) - cam.location).normalized()
        roll_rad = math.radians(roll_deg)
        R = mathutils.Matrix.Rotation(roll_rad, 4, axis)
        cam.matrix_world = R @ cam.matrix_world


def spherical_sample(dist, azim_deg, elev_deg):
    a = math.radians(azim_deg)
    e = math.radians(elev_deg)
    x = dist * math.cos(e) * math.cos(a)
    y = dist * math.cos(e) * math.sin(a)
    z = dist * math.sin(e)
    return mathutils.Vector((x, y, z))


def compute_object_stats(obj):
    mesh = obj.data
    verts = len(mesh.vertices)
    faces = len(mesh.polygons)
    bbox_local = [tuple(v) for v in obj.bound_box]
    # World-space bbox
    ws = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
    min_w = [min(c[i] for c in ws) for i in range(3)]
    max_w = [max(c[i] for c in ws) for i in range(3)]
    size = [max_w[i]-min_w[i] for i in range(3)]
    return {
        'vertices': verts,
        'faces': faces,
        'bbox_local': bbox_local,
        'bbox_world_min': min_w,
        'bbox_world_max': max_w,
        'bbox_size': size,
    }


def ensure_output_dir(root, object_name):
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_dir = os.path.join(root, f'{object_name}_render_output_{ts}')
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def configure_render(engine, res_x, res_y, samples, use_depth, use_normal):
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.resolution_percentage = 100
    if engine == 'cycles':
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = samples
        scene.cycles.progressive = 'PATH'
        scene.cycles.use_adaptive_sampling = True
    else:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
        scene.eevee.taa_render_samples = samples

    scene.use_nodes = True
    tree = scene.node_tree
    tree.nodes.clear()

    rl = tree.nodes.new('CompositorNodeRLayers')
    file_out = tree.nodes.new('CompositorNodeOutputFile')
    file_out.label = 'Dataset File Output'
    file_out.base_path = ''

    view_layer = scene.view_layers[0]

    # Add requested passes first (must be enabled before linking)
    if use_depth:
        view_layer.use_pass_z = True
        # Add depth slot if an input named Depth does not already exist
        if 'Depth' not in file_out.inputs:
            before = len(file_out.file_slots)
            file_out.file_slots.new('Depth')
            # Try to rename its path safely (API variations tolerant)
            try:
                file_out.file_slots[before].path = 'Depth'
            except Exception:
                pass
    if use_normal:
        view_layer.use_pass_normal = True
        if 'Normal' not in file_out.inputs:
            before = len(file_out.file_slots)
            file_out.file_slots.new('Normal')
            try:
                file_out.file_slots[before].path = 'Normal'
            except Exception:
                pass

    links = tree.links
    def safe_link(out_name, in_name):
        if out_name in rl.outputs and in_name in file_out.inputs:
            try:
                links.new(rl.outputs[out_name], file_out.inputs[in_name])
            except Exception:
                pass

    safe_link('Image', 'Image')
    if use_depth:
        safe_link('Depth', 'Depth')
    if use_normal:
        safe_link('Normal', 'Normal')

    return file_out


def camera_intrinsics_dict(cam, scene):
    lens = cam.data.lens
    sw = cam.data.sensor_width
    sh = cam.data.sensor_height
    resx = scene.render.resolution_x
    resy = scene.render.resolution_y
    fov_x = 2*math.atan(sw/(2*lens))
    fov_y = 2*math.atan(sh/(2*lens))
    return {
        'focal_length_mm': lens,
        'sensor_width_mm': sw,
        'sensor_height_mm': sh,
        'resolution': [resx, resy],
        'fov_x_deg': math.degrees(fov_x),
        'fov_y_deg': math.degrees(fov_y),
        'principal_point_px': [resx/2, resy/2],
    }


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# ---------------------------- Main Procedure ------------------------------ #

def main():
    args = parse_args()
    random.seed(args.seed)

    clear_scene()

    obj = import_object(args.object_source, args.object_name)
    add_light()
    cam = setup_camera(args.focal_length, args.sensor_width, args.sensor_height)

    obj_stats = compute_object_stats(obj)

    out_root = ensure_output_dir(args.output_root, args.object_name)

    file_out_node = configure_render(
        args.engine, args.resolution[0], args.resolution[1], args.samples,
        args.depth_pass, args.normal_pass
    )

    scene = bpy.context.scene

    global_meta = {
        'object_name': args.object_name,
        'object_source': args.object_source,
        'object_stats': obj_stats,
        'config': vars(args),
        'blender_version': bpy.app.version_string,
        'datetime': datetime.now().isoformat(),
        'total_views': args.views,
        'engine': scene.render.engine,
    }

    # Save placeholder global metadata early
    save_json(os.path.join(out_root, 'metadata.json'), global_meta)

    # Generate views
    for idx in range(1, args.views+1):
        # Random spherical sample
        dist = random.uniform(args.distance_min, args.distance_max)
        elev = random.uniform(args.elev_min, args.elev_max)
        azim = random.uniform(args.azim_min, args.azim_max)
        roll = random.uniform(args.roll_min, args.roll_max)

        cam_pos = spherical_sample(dist, azim, elev)
        cam.location = cam_pos

        target = mathutils.Vector((0,0,0))
        if args.jitter_target > 0:
            jt = args.jitter_target
            target += mathutils.Vector((random.uniform(-jt,jt), random.uniform(-jt,jt), random.uniform(-jt,jt)))

        look_at(cam, target, roll)

        view_dir = os.path.join(out_root, f'{idx:05d}')
        os.makedirs(view_dir, exist_ok=True)

        # Set paths
        scene.render.filepath = os.path.join(view_dir, 'rendered_image.png')
        file_out_node.base_path = view_dir  # EXRs will be named Image.exr, Depth.exr, Normal.exr

        # Render
        bpy.ops.render.render(write_still=True)

        # Gather camera info
        cam_quat = cam.matrix_world.to_quaternion()
        cam_info = {
            'index': idx,
            'distance': dist,
            'azimuth_deg': azim,
            'elevation_deg': elev,
            'roll_deg': roll,
            'camera_location': list(cam.location),
            'camera_quaternion_wxyz': [cam_quat.w, cam_quat.x, cam_quat.y, cam_quat.z],
            'camera_euler_xyz_deg': [math.degrees(a) for a in cam.rotation_euler],
            'target_point': list(target),
            'look_vector': list((target - cam.location).normalized()),
            'intrinsics': camera_intrinsics_dict(cam, scene),
            'paths': {
                'color_png': os.path.relpath(scene.render.filepath, out_root),
                'exr_image': 'Image.exr',
                'exr_depth': 'Depth.exr' if args.depth_pass else None,
                'exr_normal': 'Normal.exr' if args.normal_pass else None,
            }
        }
        save_json(os.path.join(view_dir, 'camera_info.json'), cam_info)

    # Update global metadata with finished flag
    global_meta['completed'] = True
    save_json(os.path.join(out_root, 'metadata.json'), global_meta)
    print(f'Finished rendering {args.views} views. Output at: {out_root}')

if __name__ == '__main__':
    main()
