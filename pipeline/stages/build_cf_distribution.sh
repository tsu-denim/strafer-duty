#!/usr/bin/env bash
set -x

# Install setup.py to dist directory
echo $CHROME_VERSION

# Download binaries from repo releases in parallel
wget https://github.com/tsu-denim/xvfb-portable/releases/download/v1.0/xvfb.tar.gz &
wget https://github.com/tsu-denim/node-portable/releases/download/node-v6.11.4-linux-x64/node.tar.gz &
wget https://github.com/tsu-denim/ffmpeg-portable/releases/download/v0.1-alpha/ffmpeg.tar.gz &
wget https://github.com/tsu-denim/chromium-full-gtk2-lambda/releases/download/63.2.33/chrome-63.0.3239.84.tar.gz &

# Without waiting on the downloads, also install the python library
(sudo -H pip3 install . -t dist; \
sudo mkdir -p dist/functions) &

# Wait until downloads are finished and python library has been installed
wait



# Get xvfb and copy to folder
sudo cp ./xvfb.tar.gz ./dist/functions/ &
# Get node and decompress to folder
sudo tar -xf ./node.tar.gz -C ./dist/ &
# Get ffmpeg and decompress to folder
 sudo tar -xf ./ffmpeg.tar.gz -C ./dist/ &
# Get Chrome and copy to folder
 sudo cp ./$CHROME_VERSION.tar.gz ./dist/functions/ &

# Wait until all binaries are copied or decompressed
wait




