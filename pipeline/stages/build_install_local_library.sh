#!/usr/bin/env bash
set -x

sudo pip3 install -r requirements.txt --ignore-installed urllib3
sudo pip3 install ./
