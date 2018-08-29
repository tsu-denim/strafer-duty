#!/usr/bin/env bash

# Clone protractor-sync project to use for webdriver and jasmine reporter integration testing
git clone https://github.com/blackboard/protractor-sync.git

# Copy lambda friendly protractor config and packaging script
mkdir protractor-sync/test/lambda
cp ./protractor.conf.js ./protractor-sync/test/lambda
cp package_protractor_sync.sh protractor-sync/test

# Copy jasmine reporter tests to test spec directory
cp ./webdriver_tests/jasmine_reporter_test.ts ./protractor-sync/test/spec

# Install jasmine-allure2-reporter because this is not included
# with protractor-sync package.json, then install package.json dependencies
cd protractor-sync
    npm install jasmine-allure2-reporter
    npm install
    grunt build

    # Create lambda friendly protractor-sync tarball
    cd test
        ./package_protractor_sync.sh
    cd ../
cd ../

cp protractor-sync/build/protractor-sync.tar.gz ./
