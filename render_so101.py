import bpy

# Set render engine to Cycles for better quality
bpy.context.scene.render.engine = 'CYCLES'

# Set resolution
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 100

# Set output path
bpy.context.scene.render.filepath = '/home/minhopark/repos/repos4students/jungwooahn/RoboticCameraControl/so101_rendered.png'

# Ensure there's a camera
if not bpy.context.scene.camera:
    bpy.ops.object.camera_add()
    bpy.context.scene.camera = bpy.context.object

# Position the camera to view the robot
cam = bpy.context.scene.camera
cam.location = (2, -2, 1)
cam.rotation_euler = (1.2, 0, 0.8)  # Adjust as needed

# Add a light if not present
if not any(obj.type == 'LIGHT' for obj in bpy.context.scene.objects):
    bpy.ops.object.light_add(type='SUN')
    light = bpy.context.object
    light.location = (5, -5, 5)

# Render the image
bpy.ops.render.render(write_still=True)

print("Render completed: so101_rendered.png")
