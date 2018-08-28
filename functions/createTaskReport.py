import glob
import json
import logging
import os
import os.path
import xml.etree.ElementTree as XMLTree
from decimal import *
from xml.dom import minidom

import boto3

from functions.lib.binary_service import clear_tmp
from functions.lib.utilities import get_sdb_paginator_for_test_results, download_test_reports, \
    get_sdb_paginator_for_expired_tests, get_expired_test_list

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    print('Event: ')
    print(json.dumps(event, sort_keys=False))

    job_id = event["executionName"]
    test_branch_job_identifier = event["testBranchJobIdentifier"]
    timestamp_for_test_metrics = event["timestampForTestMetrics"]
    sdb_domain = os.environ['SDBDOMAIN']
    tmp_directory = "/tmp"
    artifact_s3_bucket = os.environ['TASKRUNNERBUCKET']
    artifact_s3_prefix = "test-runner/artifacts/"
    report_s3_destination = "artifacts/" + test_branch_job_identifier + "/"
    s3_destination_source = tmp_directory + "/upload/"

    s3 = boto3.resource('s3')

    clear_tmp()
    os.makedirs("/tmp/artifacts")
    os.makedirs("/tmp/upload")

    # Read db for job metadata
    page_iterator = get_sdb_paginator_for_test_results(sdb_domain, job_id)

    # Read through db results for test ids, download junit reports
    download_test_reports(page_iterator, artifact_s3_prefix, artifact_s3_bucket, tmp_directory, s3)

    # Read db for expired tests
    expired_page_iterator = get_sdb_paginator_for_expired_tests(sdb_domain, job_id)

    # Grab testIds of expired tests, create test report if missing
    expired_test_list = get_expired_test_list(expired_page_iterator, tmp_directory)

    # Get all of the downloaded junit files
    junit_glob_pattern = tmp_directory + "/artifacts/*.xml"
    file_list = glob.glob(junit_glob_pattern)
    class_list = []
    test_case_list = []
    failed_test_list = []
    skipped_test_list = []

    # Open all files, copy testcase elements and class names for consolidated report
    print("Number of files found: " + str(len(file_list)))
    for item in file_list:
        try:
            root = XMLTree.parse(item)
        except:
            print("XML PARSE ERROR! FILE NAME: " + str(item))
            # Skip because this file is screwed up, it will still get marked skipped by artifact-slurper
            continue
        # If file contains a failure or skip, add to failed/skipped list
        test_case_id = os.path.basename(item).replace(".xml", "")
        test_case_meta_data = test_case_id.split("-")
        test_index = test_case_meta_data[0]
        failed_list = root.findall("./testcase/failure")
        skipped_list = root.findall("./testcase/skipped")
        if len(failed_list) > 0:
            failed_test_list.append(test_case_id)
        elif len(skipped_list) > 0:
            skipped_test_list.append(test_case_id)
        # Grab all test cases
        for testcase in root.findall("./testcase"):  # xpath expression strips parent elements
            classname = testcase.get("classname")  # reads the xml attribute 'classname' from testcase element
            testcase.set("testid", test_case_id)
            testcase.set("testindex", test_index)
            testcase.set("jobId", job_id)
            testcase.set("isfailed", "false")
            testcase.set("isskipped", "false")
            testcase.set("ispassed", "false")
            testcase.set("isexpired", "false")
            if test_case_id in failed_test_list:
                testcase.set("isfailed", "true")
            elif test_case_id in skipped_test_list:
                testcase.set("isskipped", "true")
            elif test_case_id in expired_test_list:
                failure = XMLTree.Element('failure')
                failure.set("message", "Exceeded Timeout in AWS Lambda, see cloudwatch log!")
                failure.set("type", "AWS_TIMEOUT")
                testcase.set("isexpired", "true")
                testcase.set("isfailed", "true")
                testcase.append(failure)
            else:
                testcase.set("ispassed", "true")

            class_list.append(classname)  # Class name saved as string
            test_case_list.append(testcase)  # Test case saved as raw XML element

    class_list = list(set(class_list))  # Python hack to remove duplicates, these become parent testsuite elements

    # Start building final test report document
    final_test_report = XMLTree.Element("testsuites")  # Create root xml element
    for string_class in class_list:  # add test suite elements as child of root
        testsuite = XMLTree.Element('testsuite')
        testsuite.set("name", string_class)
        total_time = Decimal("0.0")
        for case in test_case_list:
            caseclass = case.get('classname')
            testtime = Decimal(case.get('time'))
            if caseclass == string_class:
                total_time = total_time + testtime
                testsuite.append(case)
        testsuite.set("time", str(total_time))
        final_test_report.append(testsuite)
    output_file = tmp_directory + "/upload/" + timestamp_for_test_metrics + ".xml"
    # Create 'fake' root node
    output_header = XMLTree.Element(None)

    # Create xml processing instruction for xml style sheet
    pi = XMLTree.PI("xml-stylesheet", "type='text/xsl' href='stylesheet.xsl'")
    pi.tail = "\n"
    output_header.append(pi)
    output_header.append(final_test_report)
    output_tree = XMLTree.ElementTree(output_header)
    # Write the completed junit report
    output_tree.write(output_file, encoding="UTF-8", xml_declaration=True)
    xml_str = minidom.parse(output_file).toprettyxml()
    xml_str = xml_str.replace('    at', '&#10;    at').replace('\n&#10;    at', '&#10;    at').replace(' === Pre',
                                                                                                       '&#10; === Pre').replace(
        '=== Error', '===&#10;Error')
    with open(output_file, "w") as f:
        f.write(xml_str)

    # Define a wildcard expression to grab paths of files to be uploaded
    source_glob_pattern = s3_destination_source + "*"
    files_to_upload = glob.glob(source_glob_pattern)

    for file_to_upload in files_to_upload:
        destination_key = report_s3_destination + os.path.basename(file_to_upload)
        content_type = "binary/octet-stream"
        if ".xml" in file_to_upload:
            content_type = "text/xml"
        logger.info("Uploading " + file_to_upload + " to S3 path " + artifact_s3_bucket + "/" + destination_key)
        s3.Object(artifact_s3_bucket, destination_key).put(Body=open(file_to_upload, 'rb'), ContentType=content_type,
                                                           ContentDisposition='inline')

    # Define and upload the xml style sheet
    # TODO: https://stackoverflow.com/questions/6028000/how-to-read-a-static-file-from-inside-a-python-package
    xsl_sheet = "/var/task/functions/stylesheet.xsl"
    xsl_destination = report_s3_destination + "stylesheet.xsl"
    logger.info("Uploading stylesheet.xsl to S3 path " + artifact_s3_bucket + "/" + xsl_destination)
    s3.Object(artifact_s3_bucket, xsl_destination).put(Body=open(xsl_sheet, 'rb'), ContentType='text/xml',
                                                       ContentDisposition='inline')

    # Create url for final test report and return
    return_url = report_s3_destination + timestamp_for_test_metrics + ".xml"
    return return_url
