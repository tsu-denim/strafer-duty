#!/usr/bin/env bash

# Version of Chrome binary to download from github repo release
export CHROME_VERSION='chrome-63.0.3239.84'
echo $CHROME_VERSION
export PYTHONPATH=$PYTHONPATH:$(pwd)/dist/functions
echo $PYTHONPATH

# Install library
echo "##################################################"
echo "###### STAGE - BUILD_INSTALL_PYTHON_LIBRARY ######"
echo "##################################################"
./pipeline/stages/build_install_local_library.sh

# Build protractor-sync
echo "##################################################"
echo "###### STAGE - BUILD_INSTALL_PROTRACTOR-SYNC #####"
echo "##################################################"
cd ./pipeline/integration_tests && ./build_protractor_sync.sh && cd ../../

# Cleanup any stale distribution packages
echo "##################################################"
echo "###### STAGE - CLEAN_STALE_DISTRIBUTION ##########"
echo "##################################################"
./pipeline/stages/clean_stale_distribution.sh

# TODO: Pipe runTest logs to s3 and download for integration functional_tests
# Run protractor-sync integration smoke test, set to max 1 in config
echo "##################################################"
echo "###### STAGE - RUN_INTEGRATION_PROTRACTOR-SYNC ###"
echo "##################################################"
./pipeline/stages/run_integration_protractor-sync.sh

# Run junit jasmine integration functional_tests
echo "##################################################"
echo "###### STAGE - RUN_INTEGRATION_JASMINE-JUNIT #####"
echo "##################################################"
./pipeline/stages/run_integration_jasmine-junit.sh

# Run allure jasmine integration functional_tests
echo "##################################################"
echo "###### STAGE - RUN_INTEGRATION_JASMINE-ALLURE ####"
echo "##################################################"
cp categories.json allure-results
allure generate allure-results
./pipeline/stages/run_integration_jasmine-allure.sh
mv allure-report allure-old
cp junit_results/e2e-allure.xml allure-results
cp junit_results/e2e-junit.xml allure-results
allure generate allure-results
mv artifacts allure-report/artifacts


