# strafer-duty [![Build Status](https://travis-ci.org/tsu-denim/strafer-duty.svg?branch=master)](https://travis-ci.org/tsu-denim/strafer-duty) [Test Report](https://tsu-denim.github.io/strafer-duty/)

Example Strafing Run: [500 Concurrent Calls to Google Translate, with video and logs, total runtime < 1 minute](https://tsu-denim.github.io/strafer-duty-demo/#behaviors)



Massively parallel processing with AWS Lambda, Function as a Service (FaaS).

To deploy, download Cloud Formation package in releases (coming soon). Log into AWS account with
sufficient privileges to deploy CF stacks. In the Cloud Formation console,
deploy downloaded stack.

Next, install prequisites:

*Allure CLI, Python 3, PIP*

Test deployment successful by running integration tests:

*./run_integration_tests_osx.sh*

