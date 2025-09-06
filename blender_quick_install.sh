mkdir -p tools
cd tools
curl -L -o blender-4.5.2-linux-x64.tar.xz https://download.blender.org/release/Blender4.5/blender-4.5.2-linux-x64.tar.xz
tar -xf blender-4.5.2-linux-x64.tar.xz
cd ..
ln -s tools/blender-4.5.2-linux-x64 blender-4.5.2-linux-x64
./blender-4.5.2-linux-x64/blender --version