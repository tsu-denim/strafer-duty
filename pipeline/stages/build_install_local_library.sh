#!/usr/bin/env bash
set -x

export PYTHONPATH=${PYTHONPATH}:$(pwd)/dist/functions

pip install -r requirements.txt
pip install ./