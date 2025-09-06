#!/usr/bin/env bash
/home/minhopark/repos/repos4students/jungwooahn/RoboticCameraControl/tools/blender-4.5.2-linux-x64/blender \
	--background \
	--python multi_view_renderer.py -- \
	--object_source builtin:table \
	--object_name table \
	--views 50 \
	--distance_min 5 \
	--distance_max 5.5 \
	--elev_min -30 \
	--elev_max 30 \
	--azim_min 0 \
	--azim_max 240 \
	--resolution 640 480 \
	--engine cycles \
	--samples 32 \
	--depth_pass \
	--normal_pass \
	--seed 10
