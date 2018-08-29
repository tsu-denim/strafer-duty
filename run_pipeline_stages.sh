#!/usr/bin/env bash

export CHROME_VERSION='chrome-63.0.3239.84'
echo $CHROME_VERSION
export PYTHONPATH=$PYTHONPATH:$(pwd)/dist/functions
echo $PYTHONPATH

# Install library
echo "##################################################"
echo "###### STAGE - BUILD_INSTALL_LOCAL_LIBRARY #######"
echo "##################################################"
./pipeline/stages/build_install_local_library.sh

# Run unit tests
echo "##################################################"
echo "###### STAGE - RUN_UNIT_TESTS ####################"
echo "##################################################"
./pipeline/stages/run_unit_tests.sh &

# Cleanup any stale distribution packages
echo "##################################################"
echo "###### STAGE - CLEAN_STALE_DISTRIBUTION ##########"
echo "##################################################"
./pipeline/stages/clean_stale_distribution.sh &

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
#./pipeline/stages/zip_cf_distributable.sh

# Deploy CloudFormation stack
echo "##################################################"
echo "###### STAGE - DEPLOY_CF_STACK ###################"
echo "##################################################"
#python3 -u ./pipeline/stages/deploy.py

# TODO: Pipe runTest logs to s3 and download for integration tests
# Run protractor-sync integration smoke test, set to max 1 in config
echo "##################################################"
echo "###### STAGE - RUN_INTEGRATION_PROTRACTOR-SYNC ###"
echo "##################################################"
#./pipeline/stages/run_integration_protractor-sync.sh

# Run junit jasmine integration tests
echo "##################################################"
echo "###### STAGE - RUN_INTEGRATION_JASMINE-JUNIT #####"
echo "##################################################"
#./pipeline/stages/run_integration_jasmine-junit.sh

# Run allure jasmine integration tests
echo "##################################################"
echo "###### STAGE - RUN_INTEGRATION_JASMINE-ALLURE ####"
echo "##################################################"
#cp categories.json allure-results
#allure generate allure-results
#./pipeline/stages/run_integration_jasmine-allure.sh
