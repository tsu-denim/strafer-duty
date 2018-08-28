#!/usr/bin/env bash
set -x

export PYTHONPATH=${PYTHONPATH}:$(pwd)/dist/functions

sudo -H pip install -r requirements.txt
sudo -H pip install ./