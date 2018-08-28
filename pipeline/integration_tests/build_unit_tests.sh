#!/usr/bin/env bash

# Clone protractor-sync project to use for webdriver testing

git clone https://github.com/blackboard/protractor-sync.git


# Package protractor sync with custom protractor config for the lambda test runner

cp package_lambda.sh protractor-sync/test
mkdir protractor-sync/test/lambda
cp protractor.conf.js protractor-sync/test/lambda
cd protractor-sync

# Install jasmine-allure2-reporter because this is not included
# with protractor-sync package.json
npm install jasmine-allure2-reporter

npm install
grunt build
cd test
./package_lambda.sh
cd ../../
cp protractor-sync/build/unit.tar.gz ./
