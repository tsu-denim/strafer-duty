#!/usr/bin/env bash
set -x

# Install the python library to a folder
sudo -H pip3 install . -t dist
sudo mkdir -p dist/functions

echo "Forking copy/deflate operations..."

# Get xvfb and copy to folder
sudo cp ./xvfb.tar.gz ./dist/functions/ &
# Get node and decompress to folder
sudo tar -xf ./node.tar.gz -C ./dist/ &
# Get ffmpeg and decompress to folder
sudo tar -xf ./ffmpeg.tar.gz -C ./dist/ &
# Get Chrome and copy to folder
sudo cp ./$CHROME_VERSION.tar.gz ./dist/functions/ &

# Wait until all binaries are copied or decompressed
echo "Waiting for forked copy/deflate operations to finish.."
wait
echo "Forked copy/deflate operations have finished!"



