# strafer-duty [![Build Status](https://travis-ci.org/tsu-denim/strafer-duty.svg?branch=master)](https://travis-ci.org/tsu-denim/strafer-duty) [Test Report](https://tsu-denim.github.io/strafer-duty/)

Example Strafing Run: [500 Concurrent Calls to Google Translate, with video and logs, total runtime < 1 minute](https://tsu-denim.github.io/strafer-duty-demo/#behaviors)

Load test user workflows using Selenium, Chrome, and AWS Lamdba! Runs on the free tier for 100hrs a month in 5 AWS regions! Completely hands-off, uses only AWS managed services:

- https://aws.amazon.com/step-functions/
- https://aws.amazon.com/sns/
- https://aws.amazon.com/simpledb/ (Amazon's secret! High concurrency NoSQL at no extra cost vs costly dynamodb)

To deploy, download Cloud Formation package in releases (see launch button here -> https://tsu-denim.github.io/strafer-duty/ ). Log into AWS account with
sufficient privileges to deploy CF stacks. In the Cloud Formation console,
deploy downloaded stack.

Next, install prequisites:

*Allure CLI, Python 3, PIP*

Test deployment successful by running integration tests:

*./run_integration_tests_osx.sh*

