import pytest
import requests

from functions.lib.junit_formatter import AllureHelper


def test_allure_passed(report_path):
    report = AllureHelper(report_path)
    case_list = report.test_cases
    contains_pass = False

    for case in case_list:
        if case['name'] == 'should pass if an element is not supposed to exist and is missing #integrationSuite' \
                and case['status'] == 'passed':
            contains_pass = True
    assert contains_pass


def test_allure_failed(report_path):
    report = AllureHelper(report_path)
    case_list = report.test_cases
    contains_fail = False

    for case in case_list:
        if case['name'] == "should fail if an element is not supposed to exist but is found #integrationSuite" \
                and case['status'] == 'failed':
            contains_fail = True
    assert contains_fail


def test_allure_skipped(report_path):
    report = AllureHelper(report_path)
    case_list = report.test_cases
    contains_skip = False

    for case in case_list:
        if case['name'] == "can be skipped if we want them to #integrationSuite" and case['status'] == 'skipped':
            contains_skip = True
    assert contains_skip


def test_allure_disabled(report_path):
    report = AllureHelper(report_path)
    case_list = report.test_cases
    contains_disabled = False

    for case in case_list:
        if case['name'] == "can be disabled and hidden from the Jasmine reporter #integrationSuite" \
                and case['status'] == 'unknown':
            contains_disabled = True
    assert contains_disabled


@pytest.mark.xfail(run=False, reason="Artifacts are no longer exposed this way, these need to be downloaded instead")
def test_allure_video_artifact(report_path):
    report = AllureHelper(report_path)
    case_list = report.test_cases
    has_video = False

    for case in case_list:
        if case['status'] == "passed":
            for link in case['links']:
                if link['name'] == 'Test Video':
                    vid = requests.get(link['url'])
                    assert vid.status_code == 200
                    assert vid.headers['content-type'] == "video/mp4"
            has_video = True

    assert has_video


@pytest.mark.xfail(run=False, reason="Artifacts are no longer exposed this way, these need to be downloaded instead")
def test_allure_chrome_log_artifact(report_path):
    report = AllureHelper(report_path)
    case_list = report.test_cases
    has_log = False

    for case in case_list:
        if case['status'] == "passed":
            for link in case['links']:
                if link['name'] == 'Chrome Log':
                    log = requests.get(link['url'])
                    assert log.status_code == 200
                    assert log.headers['content-type'] == "text/plain; charset=UTF-8"
                    has_log = True

    assert has_log


@pytest.mark.xfail(run=False, reason="Artifacts are no longer exposed this way, these need to be downloaded instead")
def test_allure_chromedriver_log_artifact(report_path):
    report = AllureHelper(report_path)
    case_list = report.test_cases
    has_log = False

    for case in case_list:
        if case['status'] == "passed":
            for link in case['links']:
                if link['name'] == 'Chrome Driver Log':
                    log = requests.get(link['url'])
                    assert log.status_code == 200
                    assert log.headers['content-type'] == "text/plain; charset=UTF-8"
                    has_log = True

    assert has_log


@pytest.mark.xfail(run=False, reason="Artifacts are no longer exposed this way, these need to be downloaded instead")
def test_allure_console_log_artifact(report_path):
    report = AllureHelper(report_path)
    case_list = report.test_cases
    has_log = False

    for case in case_list:
        if case['status'] == "passed":
            for link in case['links']:
                if link['name'] == 'Console Log':
                    log = requests.get(link['url'])
                    assert log.status_code == 200
                    assert log.headers['content-type'] == "text/plain; charset=UTF-8"
                    has_log = True

    assert has_log


def test_allure_retry(report_path):
    report = AllureHelper(report_path)
    case_list = report.test_cases
    has_retry = False

    for case in case_list:
        try:
            if case['fullName'] == "Protractor sync test cases can retry if they fail when configured #integrationSuite" \
                    and case['status'] == 'passed' and case['statusDetails']['flaky']:
                has_retry = True
        except KeyError:
            if case['fullName'] == "Protractor sync test cases can retry if they fail when configured #integrationSuite" \
                    and case['status'] == 'passed' and case['flaky']:
                has_retry = True

    assert has_retry


