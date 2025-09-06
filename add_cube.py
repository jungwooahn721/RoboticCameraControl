import bpy

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Add a cube
bpy.ops.mesh.primitive_cube_add()

# Add a camera
bpy.ops.object.camera_add()
bpy.context.scene.camera = bpy.context.object

# Save the file
bpy.ops.wm.save_as_mainfile(filepath="output.blend")
