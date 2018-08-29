#!/usr/bin/env bash
set +ex

cd ./pipeline/integration_tests && ./build_integration_tests.sh && cd ../../
strafer-duty --roleToAssume="$PIPELINE_ROLE" \
--jsonConfigPath "pipeline/integration_tests/functional_tests/functional-test-config.json" \
--tarPath "pipeline/integration_tests/integration.tar.gz" \
--outputReportName "junit_results/integration.xml" \
--ciMode \
--mockExpiredTest

set -e
sudo -H python3.6 -m pytest --junitxml=junit_results/e2e-junit.xml --report_path junit_results/integration.xml \
                  ./pipeline/integration_tests/functional_tests/tests/integ_tests_junit.py