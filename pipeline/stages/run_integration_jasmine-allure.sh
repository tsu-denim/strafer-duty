#!/usr/bin/env bash
set -ex

python3 -m pytest --junitxml=junit_results/e2e-allure.xml \
--report_path='allure-report/data/test-cases/*' \
pipeline/integration_tests/functional_tests/integ_tests_allure.py
set +ex