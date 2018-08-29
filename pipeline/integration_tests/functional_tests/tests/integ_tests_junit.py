import pytest
import requests
import os

from functions.lib.manifest import JasmineManifest
from functions.lib.junit_formatter import JunitHelper


def test_junit_passed(report_path):
    report = JunitHelper(report_path)
    case_list = report.get_test_attributes()
    contains_pass = False

    for case in case_list:
        if case.is_match(
                "should pass if an element is not supposed to exist and is missing #integrationSuite") and case.is_passed == "true":
            contains_pass = True
    assert contains_pass


def test_junit_failed(report_path):
    report = JunitHelper(report_path)
    case_list = report.get_test_attributes()
    contains_fail = False

    for case in case_list:
        if case.is_match(
                "should fail if an element is not supposed to exist but is found #integrationSuite") and case.is_failed == "true":
            contains_fail = True
    assert contains_fail


def test_junit_skipped(report_path):
    report = JunitHelper(report_path)
    case_list = report.get_test_attributes()
    contains_skip = False

    for case in case_list:
        if case.is_match("can be skipped if we want them to #integrationSuite") and case.is_skipped == "true":
            contains_skip = True
    assert contains_skip


def test_junit_expired(report_path):
    report = JunitHelper(report_path)
    case_list = report.get_test_attributes()
    contains_expired = False

    for case in case_list:
        if case.is_match(
                "Expired test is considered failed") and case.is_expired == "true" and case.is_failed == "true":
            contains_expired = True
    assert contains_expired


def test_junit_disabled(report_path):
    report = JunitHelper(report_path)
    case_list = report.get_test_attributes()
    contains_disabled = False

    for case in case_list:
        if case.is_match(
                "can be disabled and hidden from the Jasmine reporter #integrationSuite") and case.is_skipped == "true" and case.suite_name == "E2E.Disabled":
            contains_disabled = True
    assert contains_disabled


@pytest.mark.xfail(reason="Artifacts are no longer exposed this way, these need to be downloaded instead")
def test_junit_video_artifact(report_path):
    report = JunitHelper(report_path)
    case_list = report.get_test_attributes()
    has_video = False

    for case in case_list:
        if case.is_passed == "true":
            vid = requests.get(case.video_link)
            assert vid.status_code == 200
            assert vid.headers['content-type'] == "video/mp4"
            has_video = True

    assert has_video


@pytest.mark.xfail(reason="Artifacts are no longer exposed this way, these need to be downloaded instead")
def test_junit_chrome_log_artifact(report_path):
    report = JunitHelper(report_path)
    case_list = report.get_test_attributes()
    has_log = False

    for case in case_list:
        if case.is_passed == "true":
            log = requests.get(case.chrome_log_link)
            assert log.status_code == 200
            assert log.headers['content-type'] == "text/plain; charset=UTF-8"
            has_log = True

    assert has_log


@pytest.mark.xfail(reason="Artifacts are no longer exposed this way, these need to be downloaded instead")
def test_junit_chromedriver_log_artifact(report_path):
    report = JunitHelper(report_path)
    case_list = report.get_test_attributes()
    has_log = False

    for case in case_list:
        if case.is_passed == "true":
            log = requests.get(case.chromedriver_log_link)
            assert log.status_code == 200
            assert log.headers['content-type'] == "text/plain; charset=UTF-8"
            has_log = True

    assert has_log


@pytest.mark.xfail(reason="Artifacts are no longer exposed this way, these need to be downloaded instead")
def test_junit_console_log_artifact(report_path):
    report = JunitHelper(report_path)
    case_list = report.get_test_attributes()
    has_log = False

    for case in case_list:
        if case.is_passed == "true":
            log = requests.get(case.console_log_link)
            assert log.status_code == 200
            assert log.headers['content-type'] == "text/plain; charset=UTF-8"
            has_log = True

    assert has_log


def test_junit_retry(report_path):
    report = JunitHelper(report_path)
    case_list = report.get_test_attributes()
    has_retry = False

    for case in case_list:
        if case.is_retried == "true":
            has_retry = True

    assert has_retry


def test_junit_manifest(report_path):
    setup_tests_abs_path = os.path.abspath('pipeline/integration_tests/webdriver_tests/jasmine_reporter_test.ts')

    jasmine_manifest = JasmineManifest([setup_tests_abs_path],
                                       ['#integrationSuite'], ['#quarantine'])
    jasmine_manifest_skipped = JasmineManifest([setup_tests_abs_path],
                                               ['#quarantine'], [])
    report = JunitHelper(report_path)
    runnable_case_list = report.get_runnable_test_elements(jasmine_manifest)
    not_runnable_case_list = jasmine_manifest.get_all_non_runnable_tests()
    complete_case_list = jasmine_manifest.jasmine_tests
    total_junit_cases = len(report.get_test_attributes()) - 1  # one record is a fake for expired test
    total_tests = jasmine_manifest.get_total_number_tests()
    total_runnable = jasmine_manifest.get_total_number_runnable()
    total_not_runnable = jasmine_manifest.get_total_number_not_runnable()

    does_total_match = False
    for item in complete_case_list:
        print(item.test_name)
    if total_runnable + total_not_runnable == total_tests:
        does_total_match = True

    assert does_total_match
    assert total_tests == total_junit_cases
    assert jasmine_manifest.get_total_number_runnable() == jasmine_manifest_skipped.get_total_number_not_runnable()
    assert jasmine_manifest_skipped.get_total_number_runnable() == jasmine_manifest.get_total_number_not_runnable()
    assert jasmine_manifest.get_total_number_tests() == jasmine_manifest_skipped.get_total_number_tests()

    # runnable cases in junit are found within its own inventory
    for item in runnable_case_list:
        is_found = False
        for case in report.get_test_attributes():
            if case.is_match(item.get('name')):
                is_found = True
                break
        assert is_found

    for item in not_runnable_case_list:
        is_found = False
        for case in report.get_test_attributes():
            if case.is_match(item.test_name):
                is_found = True
                break
        assert is_found

    for item in complete_case_list:
        is_found = False
        for case in report.get_test_attributes():
            if case.is_match(item.test_name):
                is_found = True
                break
        assert is_found
