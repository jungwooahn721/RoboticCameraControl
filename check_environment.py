import bpy
import math

def print_vector(vec, label):
    return f"{label}: ({vec.x:.3f}, {vec.y:.3f}, {vec.z:.3f})"

def print_euler(euler, label):
    return f"{label}: ({math.degrees(euler.x):.1f}°, {math.degrees(euler.y):.1f}°, {math.degrees(euler.z):.1f}°)"

print("=== Blender Scene Environment Check ===")
print(f"Scene: {bpy.context.scene.name}")
print(f"Total objects: {len(bpy.context.scene.objects)}")
print()

print("=== Objects List ===")
for obj in bpy.context.scene.objects:
    print(f"Name: {obj.name}")
    print(f"  Type: {obj.type}")
    if hasattr(obj, 'location'):
        print(print_vector(obj.location, "  Location"))
    if hasattr(obj, 'rotation_euler'):
        print(print_euler(obj.rotation_euler, "  Rotation"))
    if hasattr(obj, 'scale'):
        print(print_vector(obj.scale, "  Scale"))
    if obj.parent:
        print(f"  Parent: {obj.parent.name}")
    else:
        print("  Parent: None")
    if obj.children:
        print(f"  Children: {[child.name for child in obj.children]}")
    else:
        print("  Children: None")
    if obj.type == 'MESH' and obj.data.materials:
        mats = [mat.name for mat in obj.data.materials]
        print(f"  Materials: {mats}")
    print()

print("=== Cameras ===")
cameras = [obj for obj in bpy.context.scene.objects if obj.type == 'CAMERA']
for cam in cameras:
    print(f"Name: {cam.name}")
    print(print_vector(cam.location, "  Location"))
    print(print_euler(cam.rotation_euler, "  Rotation"))
    if bpy.context.scene.camera == cam:
        print("  Active Camera: Yes")
    else:
        print("  Active Camera: No")
    print()

print("=== Lights ===")
lights = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']
for light in lights:
    print(f"Name: {light.name}")
    print(f"  Type: {light.data.type}")
    print(print_vector(light.location, "  Location"))
    print(f"  Energy: {light.data.energy}")
    print()

print("=== Constraints ===")
for obj in bpy.context.scene.objects:
    if obj.constraints:
        print(f"Object: {obj.name}")
        for const in obj.constraints:
            print(f"  Constraint: {const.name} ({const.type})")
            if hasattr(const, 'target') and const.target:
                print(f"    Target: {const.target.name}")
        print()

print("=== Render Settings ===")
render = bpy.context.scene.render
print(f"Engine: {render.engine}")
print(f"Resolution: {render.resolution_x} x {render.resolution_y}")
print(f"Output Path: {render.filepath}")
print()

print("Check complete.")
