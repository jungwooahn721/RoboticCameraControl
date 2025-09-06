#!/usr/bin/env bash
/home/minhopark/repos/repos4students/jungwooahn/RoboticCameraControl/tools/blender-4.5.2-linux-x64/blender \
	--background \
	--python multi_view_renderer.py -- \
	--object_source builtin:plane \
	--object_name plane \
	--views 30 \
	--distance_min 3 \
	--distance_max 3.3 \
	--elev_min -10 \
	--elev_max 10 \
	--azim_min 0 \
	--azim_max 90 \
	--resolution 320 240 \
	--engine cycles \
	--samples 16 \
	--depth_pass \
	--normal_pass \
	--seed 8
