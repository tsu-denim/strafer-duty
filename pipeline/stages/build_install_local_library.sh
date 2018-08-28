#!/usr/bin/env bash
set -x

sudo -H pip3 install -r requirements.txt --ignore-installed urllib3
sudo -H pip3 install ./
