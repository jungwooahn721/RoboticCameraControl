import bpy

# Load the blend file
bpy.ops.wm.open_mainfile(filepath="output.blend")

# Find the cube object
cube = bpy.data.objects.get("Cube")
if cube:
    print(f"Cube location: {cube.location}")
else:
    print("Cube not found")
