#!/usr/bin/env bash
set -x

sudo -H pip3 install -r requirements.txt &
sudo -H pip3 install ./ &
pip3 install awscli --upgrade --user

# Wait until python library has been installed
wait
