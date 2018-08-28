# Merges the Lambda and #onlycontainer tagged (non-Lambda) test results
import getopt
import glob
import json
import os
import sys
import time
import uuid
import xml.etree.ElementTree as XMLTree
from decimal import *
from xml.dom import minidom

import functions.lib.manifest


class TCase:

    def __init__(self, name, suite_name, test_index, job_id, test_id, is_expired, is_failed, is_passed, is_skipped,
                 is_retried, is_broken, is_unknown):
        self.name = name
        self.suite_name = suite_name
        self.test_index = test_index
        self.job_id = job_id
        self.test_id = test_id
        self.base_url = "https://allure-reports.dev.bbpd.io/test-runner/artifacts/"
        self.video_link = self.base_url + self.test_index + "/" + self.job_id + "/" + self.test_id + ".mp4"
        self.console_log_link = self.base_url + self.test_index + "/" + self.job_id + "/" + self.test_id + ".console.log"
        self.chrome_log_link = self.base_url + self.test_index + "/" + self.job_id + "/" + self.test_id + ".log"
        self.chromedriver_log_link = self.base_url + self.test_index + "/" + self.job_id + "/" + self.test_id + ".chromedriver.log"
        self.is_expired = is_expired
        self.is_failed = is_failed
        self.is_passed = is_passed
        self.is_skipped = is_skipped
        self.is_retried = is_retried
        self.is_broken = is_broken
        self.is_unknown = is_unknown

    def is_match(self, name_to_check):
        is_match = False
        if self.name == name_to_check:
            is_match = True
        return is_match


class TestRetry:

    def __init__(self, test_name, attempt_number, error_msg):
        self.name = test_name
        self.attempt_number = attempt_number
        self.error_msg = error_msg

    def is_match(self, name_to_check):
        is_match = False
        if self.name == name_to_check:
            is_match = True
        return is_match


class RetryCombine:

    def __init__(self, retry_glob):
        self.retry_glob = retry_glob

    def has_retries(self):
        has_retry = False
        files = glob.glob(self.retry_glob)
        if len(files) > 0:
            has_retry = True
            print("Retries found: " + str(len(files)))
        return has_retry

    def get_retries(self):
        test_retries = []
        for retry in glob.glob(self.retry_glob):
            data = json.load(open(retry, encoding='utf-8'))
            retry_data = TestRetry(data['name'], str(data['attemptNumber']), data['errorMessage'])
            test_retries.append(retry_data)
        return test_retries

    def has_matching_retry(self, test_name):
        has_match = False
        for retry in self.get_retries():
            if retry.is_match(test_name):
                has_match = True
                break;
        return has_match

    def get_matching_retries(self, test_name):
        retries = []
        for retry in self.get_retries():
            if retry.is_match(test_name):
                retries.append(retry)
        return retries


class JunitHelper:

    def __init__(self, junit_report_path):
        self.junit_report_path = junit_report_path
        junit_report_tree = XMLTree.parse(self.junit_report_path)
        self.junit_report = junit_report_tree.getroot()
        test_elements = []
        for test_case in self.junit_report.findall("./testsuite/testcase"):
            test_elements.append(test_case)
        self.test_elements = test_elements

    def get_test_attributes(self):
        test_case_list = []
        for test_case in self.junit_report.findall("./testsuite/testcase"):
            test_data = TCase(str(test_case.get("name")), test_case.get("classname"), test_case.get("testindex"),
                              test_case.get("jobId"),
                              test_case.get("testid"), test_case.get("isexpired"), test_case.get("isfailed"),
                              test_case.get("ispassed"), test_case.get("isskipped"), test_case.get("isretried"),
                              False, False)
            test_case_list.append(test_data)
        return test_case_list

    def get_test_names(self):
        test_case_list = []
        for test_case in self.junit_report.findall("./testsuite/testcase"):
            test_data = str(test_case.get("name"))
            test_case_list.append(test_data)
        return test_case_list

    def get_test_elements_except(self, test_names):
        element_list = []

        for item in self.test_elements:
            test_name = str(item.get("name"))
            if test_name not in test_names:
                element_list.append(item)
        return element_list

    def get_runnable_test_elements(self, jasmine_manifest):

        element_list = []

        for item in self.test_elements:
            test_name = str(item.get("name"))
            test_is_runnable = jasmine_manifest.is_runnable(test_name)
            if test_is_runnable:
                element_list.append(item)
        return element_list

    def is_runnable_test_missing(self, test_name, jasmine_manifest):
        test_missing = True
        for each_test in self.get_test_names():
            tn = each_test.replace('\\', "").replace("'", "").replace('"', '')
            tn1 = test_name.replace('\\', "").replace("'", "").replace('"', '')
            if tn == tn1:
                if jasmine_manifest.is_runnable(each_test):
                    test_missing = False
                    break

        return test_missing

    def get_elements_for_missing_tests(self, jasmine_manifest):
        element_list = []

        for each_test in jasmine_manifest.get_all_runnable_tests():
            if self.is_runnable_test_missing(each_test.test_name, jasmine_manifest):
                test_case = XMLTree.Element('testcase')
                test_case.set('name', each_test.test_name)
                test_case.set('classname', 'DISABLED.' + each_test.test_class_name)
                test_case.set('time', '0')
                skipped = XMLTree.Element('skipped')
                test_case.append(skipped)
                element_list.append(test_case)
        return element_list


class JunitMerger:

    def __init__(self, target_file_glob, destination_path, runnable_manifest):
        self.destination_path = destination_path
        self.target_file_glob = target_file_glob
        self.runnable_manifest = runnable_manifest
        self.non_runnable_manifest = functions.lib.manifest.JasmineManifest(runnable_manifest.test_globs, [], runnable_manifest.excluded_tags)

    def __get_runnable_elements(self):
        element_list = []
        for junit_file in glob.glob(self.target_file_glob):
            target_helper = JunitHelper(junit_file)
            element_list = element_list + target_helper.get_runnable_test_elements(self.runnable_manifest)
        element_list = list(set(element_list))
        return element_list

    def __get_non_runnable_test_elements(self):

        element_list = []

        for item in self.non_runnable_manifest.get_all_non_runnable_tests():
            test_case = XMLTree.Element('testcase')
            test_case.set('name', item.test_name)
            test_case.set('classname', 'FILTERED.' + item.test_class_name)
            test_case.set('time', '0')
            skipped = XMLTree.Element('skipped')
            test_case.append(skipped)
            element_list.append(test_case)
        return element_list

    def __get_missing_runnable_elements(self):
        element_list = []
        for junit_file in glob.glob(self.target_file_glob):
            target_helper = JunitHelper(junit_file)
            element_list = element_list + target_helper.get_elements_for_missing_tests(self.runnable_manifest)
        element_list = list(set(element_list))
        return element_list

    def __get_distinct_class_names(self, tests_elements: list):
        class_names = []
        for item in tests_elements:
            cname = str(item.get("classname"))
            class_names.append(cname)
        class_names = list(set(class_names))
        return class_names

    def __add_test_retries(self, test_cases, test_retries):
        return_list = []

    def create_report(self, retry_combine=None):
        test_cases = self.__get_runnable_elements()
        test_classes = self.__get_distinct_class_names(test_cases)

        if retry_combine is not None:
            updated_cases = []
            for case in test_cases:
                test_name = case.get('classname').replace('E2E.', '') + ' ' + case.get('name')
                if retry_combine.has_matching_retry(test_name):
                    case.set('isretried', 'true')
                    for retry in retry_combine.get_matching_retries(test_name):
                        print("Test retry found, adding failedretry element...")
                        failed_retry = XMLTree.Element('rerunFailure')
                        failed_retry.set('attemptnumber', retry.attempt_number)
                        failed_retry.set('message', retry.error_msg)
                        case.append(failed_retry)
                else:
                    case.set('isretried', 'false')
                updated_cases.append(case)
            test_cases = updated_cases

        self.write_report(test_cases, test_classes)

    def create_runnable_report(self):
        test_cases = self.__get_runnable_elements()
        test_classes = self.__get_distinct_class_names(test_cases)

        self.write_report(test_cases, test_classes)

    def create_non_runnable_report(self):
        test_cases = self.__get_non_runnable_test_elements()
        test_classes = self.__get_distinct_class_names(test_cases)

        self.write_report(test_cases, test_classes)

    def create_missing_report(self):
        test_cases = self.__get_missing_runnable_elements()
        test_classes = self.__get_distinct_class_names(test_cases)

        self.write_report(test_cases, test_classes)

    def write_report(self, test_cases, test_classes):
        # Start building final test report document
        final_test_report = XMLTree.Element("testsuites")  # Create root xml element
        for string_class in test_classes:  # add test suite elements as child of root
            test_suite = XMLTree.Element('testsuite')
            test_suite.set("name", string_class)
            total_time = Decimal("0.0")
            for case in test_cases:
                case_class = case.get('classname')
                test_time = Decimal(case.get('time'))
                if case_class == string_class:
                    total_time = total_time + test_time
                    test_suite.append(case)
            test_suite.set("time", str(total_time))
            final_test_report.append(test_suite)

        # Create 'fake' root node
        output_header = XMLTree.Element(None)

        # Create xml processing instruction for xml style sheet
        pi = XMLTree.PI("xml-stylesheet", "type='text/xsl' href='stylesheet.xsl'")
        pi.tail = "\n"
        output_header.append(pi)
        output_header.append(final_test_report)
        output_tree = XMLTree.ElementTree(output_header)
        # Write the completed junit report
        output_tree.write(self.destination_path, encoding="UTF-8", xml_declaration=True)
        xml_string = minidom.parse(self.destination_path).toprettyxml()
        xml_string = xml_string.replace('    at', '&#10;    at').replace('\n&#10;    at', '&#10;    at').replace(
            ' === Pre',
            '&#10; === Pre').replace(
            '=== Error', '===&#10;Error')
        with open(self.destination_path, "w") as f:
            f.write(xml_string)

    def remove_old_files(self):
        for report_file in glob.glob(self.target_file_glob):
            os.remove(report_file)


class AllureTweaker:

    def __init__(self, junit_report_path, allure_results_glob):
        self.junit_helper = JunitHelper(junit_report_path)
        self.allure_results_glob = allure_results_glob

    def __get_json(self, file_path):
        with open(file_path, "r", encoding="utf-8") as jsonFileRead:
            return json.load(jsonFileRead)

    def __set_json(self, file_path, json_data: dict):
        with open(file_path, 'w', encoding="utf-8") as jsonFileWrite:
            json.dump(json_data, jsonFileWrite, ensure_ascii=False)

    def __get_test_links(self, test: TCase):
        links = [
            {"name": "Video Recording", "url": test.video_link, "type": "video/mp4"},
            {"name": "Console Log", "url": test.console_log_link, "type": "text/plain"},
            {"name": "Chrome Log", "url": test.chrome_log_link, "type": "text/plain"},
            {"name": "Chromedriver Log", "url": test.chromedriver_log_link, "type": "text/plain"}
        ]

        return links

    def update_results(self):
        for allure_result in glob.glob(self.allure_results_glob):
            self.__update_result(allure_result)

    def __update_result(self, result_path):
        json_data = self.__get_json(result_path)
        for test in self.junit_helper.get_test_attributes():
            if test.is_match(json_data["name"]):
                json_data["links"] = self.__get_test_links(test)
                self.__set_json(result_path, json_data)


class AllureHelper:

    def __init__(self, allure_results_glob):
        self.allure_results_glob = allure_results_glob
        self.file_list = glob.glob(allure_results_glob)
        self.test_cases = self.__get_test_attributes()

    def __get_json(self, file_path):
        with open(file_path, "r", encoding="utf-8") as jsonFileRead:
            return json.load(jsonFileRead)

    def __set_json(self, file_path, json_data: dict):
        with open(file_path, 'w', encoding="utf-8") as jsonFileWrite:
            json.dump(json_data, jsonFileWrite, ensure_ascii=False)

    def __is_match(self, name_a, name_b):
        is_match = False
        if name_a == name_b:
            is_match = True
        return is_match

    def update_results(self, jasmine_manifest: functions.lib.manifest.JasmineManifest):
        for allure_result in self.file_list:
            self.__update_result_tags(allure_result, jasmine_manifest)

    def get_prepended_message(self, json, prepend_string):
        json_data = json
        if "message" in json_data["statusDetails"]:
            status_message = json_data["statusDetails"]["message"]
            json_data["statusDetails"]["message"] = prepend_string + status_message
        else:
            json_data["statusDetails"]["message"] = prepend_string
        return json_data

    def get_prepended_trace(self, json, prepend_string):
        json_data = json
        if "trace" in json_data["statusDetails"]:
            status_trace = json_data["statusDetails"]["trace"]
            json_data["statusDetails"]["trace"] = prepend_string + status_trace
        else:
            json_data["statusDetails"]["trace"] = prepend_string
        return json_data

    def is_failed_with_retry(self, json_data):
        retry = False
        if "trace" in json_data["statusDetails"]:
            if "FAILED_WITH_RETRY" in json_data["statusDetails"]["trace"]:
                retry = True
        return retry

    def __update_result_tags(self, result_path, jasmine_manifest: functions.lib.manifest.JasmineManifest):
        json_data = self.__get_json(result_path)
        for test in jasmine_manifest.jasmine_tests:
            if self.__is_match(json_data["name"], test.test_name) and len(test.get_included_tags()) > 0:
                tags = test.get_included_tags()
                tag_string = "Tags: " + ','.join(tags) + "\n"
                final_json = self.get_prepended_message(json_data, tag_string)
                self.__set_json(result_path, final_json)

    def __has_status_message(self):
        has_status = False

        return has_status

    def __get_test_attributes(self):
        test_case_list = []
        for allure_result in self.file_list:
            test_case = self.__get_json(allure_result)
            test_case_list.append(test_case)
        return test_case_list

    def get_result_test_names(self):
        name_list = []
        for result in self.test_cases:
            full_name = result['fullName']
            name_list.append(full_name)
        return name_list

    def get_unique_result_test_names(self):
        name_list = []
        for result in self.test_cases:
            full_name = result['fullName']
            name_list.append(full_name)
        name_list = list(set(name_list))
        return name_list

    def get_runnable_test_results(self, jasmine_manifest: functions.lib.manifest.JasmineManifest):

        runnable_results = []

        for result in self.test_cases:
            test_name = result["name"]
            test_is_runnable = jasmine_manifest.is_runnable(test_name)
            if test_is_runnable:
                runnable_results.append(result)
        return runnable_results

    def get_non_runnable_test_results(self, jasmine_manifest: functions.lib.manifest.JasmineManifest):

        runnable_results = []

        for result in self.test_cases:
            test_name = result["name"]
            test_is_runnable = jasmine_manifest.is_runnable(test_name)
            if test_is_runnable is not True:
                runnable_results.append(result)
        return runnable_results

    def is_runnable_test_missing(self, test_name, jasmine_manifest: functions.lib.manifest.JasmineManifest):
        test_missing = True
        for each_test in self.get_result_test_names():
            tn = each_test.replace('\\', "").replace("'", "").replace('"', '')
            tn1 = test_name.replace('\\', "").replace("'", "").replace('"', '')
            if tn == tn1:
                if jasmine_manifest.is_runnable(each_test):
                    test_missing = False
                    break

        return test_missing

    def get_results_for_missing_tests(self, jasmine_manifest: functions.lib.manifest.JasmineManifest):
        element_list = []

        for each_test in jasmine_manifest.get_all_runnable_tests():
            if self.is_runnable_test_missing(each_test.test_name):
                continue
                # test_case = TCase('', '', 0, 0, 0, False, False, False, False, False)
                #
                # element_list.append(test_case)
        return element_list


def write_native_allure_results(test_list):
    allure_results_directory = 'allure-results'
    os.makedirs(allure_results_directory, exist_ok=True)

    for key in test_list:
        test = test_list[key]
        if test['found'] is False:
            current_milli_time = int(round(time.time() * 1000))

            test_case_allure = {
                'fullName': key,
                'historyId': key,
                'labels': [{
                    'name': 'parentSuite',
                    'value': test['class']
                }],
                'name': test['name'],
                'stage': 'finished',
                'start': current_milli_time,
                'status': 'skipped',
                'stop': current_milli_time,
                'uuid': str(uuid.uuid4())
            }

            unique_name = str(uuid.uuid4()) + '-result.json'
            output_path = os.path.abspath(os.path.join(allure_results_directory, unique_name))

            print('Writing native allure result: ' + output_path)
            with open(output_path, 'w') as output_file:
                output_file.write(json.dumps(test_case_allure, sort_keys=True))


def strip_escape(string):
    return string.encode('utf-8').decode('unicode-escape')


