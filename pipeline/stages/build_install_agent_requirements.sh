#!/usr/bin/env bash

# Download binaries from repo releases in parallel
wget https://github.com/tsu-denim/xvfb-portable/releases/download/v1.0/xvfb.tar.gz --quiet &
wget https://github.com/tsu-denim/node-portable/releases/download/node-v6.11.4-linux-x64/node.tar.gz --quiet &
wget https://github.com/tsu-denim/ffmpeg-portable/releases/download/v0.1-alpha/ffmpeg.tar.gz --quiet &
wget https://github.com/tsu-denim/chromium-full-gtk2-lambda/releases/download/63.2.33/chrome-63.0.3239.84.tar.gz --quiet &

sudo -H apt-get install software-properties-common -qq
sudo -H add-apt-repository ppa:deadsnakes/ppa
sudo -H apt-get update -qq
sudo -H apt-get install python3.6 -qq
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo -H python3.6

wait