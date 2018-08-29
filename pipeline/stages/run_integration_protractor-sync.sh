#!/usr/bin/env bash

# protractor-sync unit test suite
set -x
set +e

strafer-duty --roleToAssume "$PIPELINE_ROLE" \
--jsonConfigPath "pipeline/integration_tests/webdriver_tests/unit-test-config.json" \
--tarPath "pipeline/integration_tests/protractor-sync.tar.gz" \
--excludeTags="integrationSuite" \
--outputReportName "junit_results/unit.xml" \
--ciMode