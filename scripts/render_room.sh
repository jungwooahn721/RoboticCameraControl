#!/usr/bin/env bash
/home/minhopark/repos/repos4students/jungwooahn/RoboticCameraControl/tools/blender-4.5.2-linux-x64/blender \
	--background \
	--python multi_view_renderer.py -- \
	--object_source builtin:room \
	--object_name room \
	--views 20 \
	--distance_min 1.5 \
	--distance_max 2.5 \
	--elev_min -20 \
	--elev_max 40 \
	--azim_min 0 \
	--azim_max 360 \
	--resolution 640 480 \
	--engine cycles \
	--samples 32 \
	--depth_pass \
	--normal_pass \
	--seed 11
