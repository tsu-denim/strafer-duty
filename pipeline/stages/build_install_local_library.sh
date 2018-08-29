#!/usr/bin/env bash
set -x

sudo -H pip3 install -r requirements.txt --quiet &
sudo -H pip3 install ./ --quiet &

cd pipeline/integration_tests && ./build_unit_tests.sh && cd ../../
cd pipeline/integration_tests && ./build_integration_tests.sh && ../../

# Wait until python library has been installed
wait
