#!/usr/bin/env bash
/home/minhopark/repos/repos4students/jungwooahn/RoboticCameraControl/tools/blender-4.5.2-linux-x64/blender \
	--background \
	--python multi_view_renderer.py -- \
	--object_source builtin:torus \
	--object_name torus \
	--views 50 \
	--distance_min 4 \
	--distance_max 4.4 \
	--elev_min -25 \
	--elev_max 25 \
	--azim_min 0 \
	--azim_max 200 \
	--resolution 320 240 \
	--engine cycles \
	--samples 16 \
	--depth_pass \
	--normal_pass \
	--seed 7
