#!/usr/bin/env bash
set -x

# Install setup.py to dist directory
echo $CHROME_VERSION

sudo -H pip3 install . -t dist

# Untar ffmpeg and node runtime environment into lambda package
sudo tar -xf ./bin/ffmpeg.tar.gz -C ./dist/
sudo tar -xf ./bin/node.tar.gz -C ./dist/
sudo mkdir -p dist/functions
sudo cp ./bin/$CHROME_VERSION.tar.gz ./dist/functions/