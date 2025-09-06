import bpy

print("Objects in the scene:")
for obj in bpy.context.scene.objects:
    print(f"- {obj.name} (type: {obj.type})")

# Check if there's a cube
cubes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH' and 'cube' in obj.name.lower()]
if cubes:
    print(f"\nFound cube(s): {[c.name for c in cubes]}")
else:
    print("\nNo cubes found in the scene.")
