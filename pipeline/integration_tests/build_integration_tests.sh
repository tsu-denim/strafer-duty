#!/usr/bin/env bash

# Package protractor-sync based test setup for functional tests

cd functional_tests/test_setup
npm install
grunt build
cd test
./package_lambda.sh
cd ../../../
cp functional_tests/test_setup/build/integration.tar.gz ./
