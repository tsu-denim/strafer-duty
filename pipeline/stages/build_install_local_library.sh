#!/usr/bin/env bash
set -x

# Silently grab python libs
sudo -H pip3 install -r requirements.txt --quiet

# Silently install python distributable to enable shell commands
sudo -H pip3 install ./ --quiet


