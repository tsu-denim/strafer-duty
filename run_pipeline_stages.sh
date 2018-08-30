#!/usr/bin/env bash

# Version of Chrome binary to download from github repo release
export CHROME_VERSION='chrome-63.0.3239.84'
echo $CHROME_VERSION
export PYTHONPATH=$PYTHONPATH:$(pwd)/dist/functions
echo $PYTHONPATH

# Install library
echo "##################################################"
echo "###### STAGE - DOWNLOAD_INSTALL_REQUIREMENTS #####"
echo "##################################################"
./pipeline/stages/build_install_agent_requirements.sh

# Run unit functional_tests
echo "##################################################"
echo "###### STAGE - RUN_UNIT_TESTS ####################"
echo "##################################################"
./pipeline/stages/run_unit_tests.sh

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

# Build static linked distributable and install
# TODO: Add log groups to yaml template with retention policy so they are managed as part of the stack
echo "##################################################"
echo "###### STAGE - BUILD_CF_DISTRIBUTION #############"
echo "##################################################"
./pipeline/stages/build_cf_distribution.sh

# Build CloudFormation stack template and upload to S3 Bucket
echo "##################################################"
echo "###### STAGE - ZIP_CF_DISTRIBUTION ###############"
echo "##################################################"
./pipeline/stages/zip_cf_distributable.sh

# Deploy CloudFormation stack
echo "##################################################"
echo "###### STAGE - DEPLOY_CF_STACK ###################"
echo "##################################################"
python3.6 -u ./pipeline/stages/deploy.py

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


