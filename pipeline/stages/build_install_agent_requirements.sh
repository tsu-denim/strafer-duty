#!/usr/bin/env bash

# Download binaries from repo releases in parallel
echo "Forking downloads of repo release binaries from github..."
wget https://github.com/tsu-denim/xvfb-portable/releases/download/v1.0/xvfb.tar.gz --quiet &
wget https://github.com/tsu-denim/node-portable/releases/download/node-v6.11.4-linux-x64/node.tar.gz --quiet &
wget https://github.com/tsu-denim/ffmpeg-portable/releases/download/v0.1-alpha/ffmpeg.tar.gz --quiet &
wget https://github.com/tsu-denim/chromium-full-gtk2-lambda/releases/download/63.2.33/chrome-63.0.3239.84.tar.gz --quiet &

echo "Forking complete, waiting for operations to complete..."
wait
echo "Forked downloads complete!"