#!/usr/bin/env bash
set -x

sudo -H pip3 install -r requirements.txt &
sudo -H pip3 install ./ &

wait
