#!/bin/bash
#
# AWS Lambda friendly protractor test packaging script
# Creates a standalone runnable version of the tests.
# Output is stored in the build directory as a .tar.gz file


# Set some basic error handling
set -ex

cd ../

# Make Directory 'lambda_protractor' within the build folder
echo "Creating directories within build directory"
mkdir -p ./build/lambda_protractor/build

# Copy 'Build/test', 'config', 'test' to lambda_protractor
echo "Copying test resources into build/lambda_protractor"
cp -R ./test ./build/lambda_protractor
cp -R ./node_modules ./build/lambda_protractor
cp -R ./build/develop ./build/lambda_protractor/build
cd ./build/lambda_protractor

# Run tar.gz command on lambda_protractor
echo "Creating tar payload within build directory"
cd ../
tar czf protractor-sync.tar.gz ./lambda_protractor


###########################################################
# .tar.gz file can now be delivered to the test-runner 
# service for test execution
###########################################################

