#!/usr/bin/env bash

# protractor-sync unit test suite
set -x
set +e

cd pipeline/integration_tests && ./build_unit_tests.sh && cd ../../
strafer-duty --roleToAssume "$PIPELINE_ROLE" \
--jsonConfigPath "pipeline/integration_tests/webdriver_tests/unit-test-config.json" \
--tarPath "pipeline/integration_tests/unit.tar.gz" \
--outputReportName "junit_results/unit.xml" \
--ciMode