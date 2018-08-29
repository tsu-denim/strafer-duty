#!/usr/bin/env bash
set -x

# Install setup.py to dist directory
echo $CHROME_VERSION

sudo -H pip3 install . -t dist

wget https://github.com/tsu-denim/chromium-full-gtk2-lambda/releases/download/63.2.33/chrome-63.0.3239.84.tar.gz
wget https://github.com/tsu-denim/xvfb-portable/releases/download/v1.0/xvfb.tar.gz
wget https://github.com/tsu-denim/node-portable/releases/download/node-v6.11.4-linux-x64/node.tar.gz
wget https://github.com/tsu-denim/ffmpeg-portable/releases/download/v0.1-alpha/ffmpeg.tar.gz

# Untar ffmpeg and node runtime environment into lambda package
sudo tar -xf ./ffmpeg.tar.gz -C ./dist/
sudo tar -xf ./node.tar.gz -C ./dist/
sudo mkdir -p dist/functions
sudo cp ./$CHROME_VERSION.tar.gz ./dist/functions/
sudo cp ./xvfb.tar.gz ./dist/functions/