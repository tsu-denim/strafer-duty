#!/usr/bin/env bash

# TODO: Find better repositories for these, they are full of garbage dependencies and pollute the build log
# Install node.js 7 and grunt-cli
curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install -g grunt-cli
