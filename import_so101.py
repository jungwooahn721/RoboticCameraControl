import bpy

# Install Phobos add-on
addon_zip = '/home/minhopark/repos/repos4students/jungwooahn/RoboticCameraControl/phobos.zip'
bpy.ops.preferences.addon_install(filepath=addon_zip)

# Enable Phobos add-on
bpy.ops.preferences.addon_enable(module='phobos')

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import the URDF
urdf_path = '/home/minhopark/repos/repos4students/jungwooahn/RoboticCameraControl/SO-ARM100/Simulation/SO101/so101_new_calib.urdf'
try:
    bpy.ops.phobos.import_robot_model(filepath=urdf_path)
except RuntimeError as e:
    print(f"Import completed with warning: {e}")

# Save the file
bpy.ops.wm.save_as_mainfile(filepath='/home/minhopark/repos/repos4students/jungwooahn/RoboticCameraControl/so101_imported.blend')
