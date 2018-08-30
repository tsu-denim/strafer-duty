import datetime
import gc
import json
import os
import pathlib
import signal
import subprocess
import time
import uuid
import xml.etree.ElementTree as XMLTree
from xml.dom import minidom
import botocore
from functions.lib.allure_formatter import create_missing_allure_result, upload_allure_result, get_host_labels,\
    create_link, allure_results_directory_exists, allure_results_directory_contains_files, get_json_results,\
    create_retry_allure_results
from functions.lib.binary_service import kill_leftover_processes, clear_tmp
from functions.lib.cloudwatch_log import CloudWatchLogs
from functions.lib.manifest import JasmineManifest
from functions.lib.junit_formatter import RetryCombine, JunitMerger
from functions.lib.utilities import current_time_milli, get_simple_db_client, sdb_put_test_start, get_s3_resource, \
    put_attributes


def handler(event, context):
    print('Event: ')
    print(json.dumps(event, sort_keys=False))

    setup_start_time = current_time_milli()

    gc.collect()

    cloud_watch_logs = CloudWatchLogs()
    cloud_watch_logs.print_marker()

    server_login = event["Records"][0]["Sns"]["MessageAttributes"]["ServerLogin"]["Value"]
    print("Server Login: " + server_login)

    server_password = event["Records"][0]["Sns"]["MessageAttributes"]["ServerPassword"]["Value"]
    print("Server Password: " + server_password)

    server_url = event["Records"][0]["Sns"]["MessageAttributes"]["ServerUrl"]["Value"]
    print("Server URL: " + server_url)

    test_id = event["Records"][0]["Sns"]["MessageAttributes"]["TestId"]["Value"]
    print("TestID: " + test_id)

    test_name = event["Records"][0]["Sns"]["MessageAttributes"]["TestName"]["Value"]
    print("TestName: " + test_name)

    test_class_name = event["Records"][0]["Sns"]["MessageAttributes"]["TestClassName"]["Value"]
    print("TestClassName: " + test_class_name)

    test_file_path = event["Records"][0]["Sns"]["MessageAttributes"]["TestFilePath"]["Value"]
    print("Test File Path: " + test_file_path)

    tarball_s3_bucket = event["Records"][0]["Sns"]["MessageAttributes"]["TarballS3Bucket"]["Value"]
    print("Tarball S3 Bucket: " + tarball_s3_bucket)

    node_runtime_s3_path = event["Records"][0]["Sns"]["MessageAttributes"]["NodeRuntimeS3Path"]["Value"]
    print("Node Runtime S3 Path: " + node_runtime_s3_path)

    xvfb_s3_path = event["Records"][0]["Sns"]["MessageAttributes"]["XvfbS3Path"]["Value"]
    print("Xvfb S3 path: " + xvfb_s3_path)

    system_libs_s3_path = event["Records"][0]["Sns"]["MessageAttributes"]["SystemLibsS3Path"]["Value"]
    print("System Libs S3 Path: " + system_libs_s3_path)

    protractor_tarball_s3_path = event["Records"][0]["Sns"]["MessageAttributes"]["ProtractorTarballS3Path"]["Value"]
    print("Protractor Tarball S3 Path: " + protractor_tarball_s3_path)

    run_test_command = event["Records"][0]["Sns"]["MessageAttributes"]["RunTestCommand"]["Value"]
    print("Bash command for running tests: " + run_test_command)

    job_id = event["Records"][0]["Sns"]["Message"]
    print("SNS Message Body " + job_id)

    assumable_role = event["Records"][0]["Sns"]["MessageAttributes"]["AssumeRoleBoolean"]["Value"]
    print("Assume different AWS Role?: " + assumable_role)

    assumable_role_arn = event["Records"][0]["Sns"]["MessageAttributes"]["AssumableRoleArn"]["Value"]
    print("Assume different AWS Role?: " + assumable_role_arn)

    artifact_s3_bucket = os.environ['TASKRUNNERBUCKET']
    print("Test Artifact Destination Bucket: " + artifact_s3_bucket)

    artifact_s3_path = "test-runner/artifacts/" + job_id
    print("Test Artifact Destination Path: " + artifact_s3_path)

    junit_report_s3_path = artifact_s3_path + "/" + job_id.replace("/", "-") + ".xml"
    print("Test Report Path: " + junit_report_s3_path)

    test_branch_job_identifier = event["Records"][0]["Sns"]["MessageAttributes"]["TestBranchId"]["Value"]
    print("Test Branch Job ID: " + test_branch_job_identifier)

    timestamp_for_test_metrics = event["Records"][0]["Sns"]["MessageAttributes"]["MetricsId"]["Value"]
    print("Metrics Timestamp ID: " + timestamp_for_test_metrics)

    clear_tmp()

    sdb_domain = os.environ['SDBDOMAIN']
    print("SDBDOMAIN: " + sdb_domain)

    test_start = str(datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%f"))
    test_start_milli = current_time_milli()
    print("Marking test start in database with the following stamp: " + test_start)
    sdb = get_simple_db_client(assumable_role, assumable_role_arn)

    sdb_put_test_start(sdb, sdb_domain, job_id, test_start, test_id, artifact_s3_bucket, artifact_s3_path, context)

    kill_leftover_processes()

    s3 = get_s3_resource(assumable_role, assumable_role_arn)
    try:

        # TODO: https://stackoverflow.com/questions/6028000/how-to-read-a-static-file-from-inside-a-python-package
        decompress_xvfb = subprocess.check_output(
            ["tar", "-xf", "/var/task/functions/xvfb.tar.gz", "-C", "/tmp", "--warning=no-unknown-keyword"])
        print(decompress_xvfb)

        print('Untarring Chrome...')
        chrome_tar_location = '/var/task/functions/' + os.environ['CHROME_VERSION'] + '.tar.gz'
        decompress_chrome = subprocess.check_output(["tar",
                                                     "-xf",
                                                     chrome_tar_location,
                                                     "-C",
                                                     "/tmp",
                                                     "--warning=no-unknown-keyword"])

        # Rename chrome directory
        chrome_location = '/tmp/' + os.environ['CHROME_VERSION']
        os.rename(chrome_location, '/tmp/chrome-lambda')

        print(decompress_chrome)

        print('Downloading protractor payload from s3...')
        s3.Bucket(tarball_s3_bucket).download_file(protractor_tarball_s3_path, '/tmp/payload.tar.gz')
        decompress_protractor = subprocess.check_output(["tar",
                                                         "-xf",
                                                         "/tmp/payload.tar.gz",
                                                         "-C",
                                                         "/tmp",
                                                         "--warning=no-unknown-keyword"])

        rm_protractor = subprocess.check_output(["cd /tmp && rm -rf payload.tar.gz && df -h /tmp"],
                                                stderr=subprocess.STDOUT,
                                                shell=True)
        print(decompress_protractor)
        print(rm_protractor)

        print("Attempting to start chrome driver...")
        chromedriver = subprocess.Popen(
            "/tmp/chrome-lambda/chromedriver --verbose --log-path=/tmp/chromedriver.log",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            preexec_fn=os.setsid)

        for stdout_line in chromedriver.stdout:
            line = str(stdout_line, 'UTF-8').strip()
            print(line)
            if "Only local connections are allowed." in line:
                print('Chromedriver successfully started')
                break

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

    remove_old_test_logs = subprocess.check_output(["rm", "-rf", "/tmp/lambda_protractor/test/build/"])
    pathlib.Path("/tmp/lambda_protractor/build/test/test/e2e/retry_attempts/").mkdir(parents=True, exist_ok=True)
    print(remove_old_test_logs)

    new_env = os.environ.copy()
    new_env[
        'LD_LIBRARY_PATH'] = '/lib64:/usr/lib64:/var/runtime:/var/runtime/lib:/var/task:/var/task/lib:/tmp/xvfb-1/libs'
    start_xvfb = subprocess.Popen(
        "/tmp/xvfb-1/xvfb :99 -ac -screen 0 1920x1080x24 -nolisten tcp -dpi 96 +extension RANDR &",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        preexec_fn=os.setsid,
        env=new_env)

    for stdout_line in start_xvfb.stdout:
        line = str(stdout_line, 'UTF-8').strip()
        print(line)
        if "Errors from xkbcomp are not fatal to the X server" in line \
                or "Cannot establish any listening sockets - Make sure an X server isn't already running(EE)" in line:
            print('Xvfb successfully started')
            break

    record_vid = subprocess.Popen(
        "/var/task/ffmpeg -video_size 1920x1080 -framerate 1 -f x11grab -i :99.0 -pix_fmt yuv420p -vcodec libx264 "
        "/tmp/videoFile.mp4 ",
        stdin=subprocess.PIPE,
        shell=True,
        preexec_fn=os.setsid)

    print('Running Test...')
    protractor_template = run_test_command

    # Format test name to prevent issues with protractor grep option
    test_name_chars = list(test_name)

    for index, char in enumerate(test_name_chars):
        if not char.isalnum() and not char.isspace() and char not in "\\":
            new_char = "\\" + char
            test_name_chars[index] = new_char

    shell_safe_test_name = "".join(test_name_chars)

    print('Setup time: ' + str(current_time_milli() - setup_start_time))

    # Format final protractor command
    protractor_cmd = protractor_template.format(test_file_path, server_url, server_login, server_password,
                                                shell_safe_test_name)

    time_remaining_after_test_timeout = 30  # Seconds
    test_timeout = int(context.get_remaining_time_in_millis() / 1000) - time_remaining_after_test_timeout
    print('Remaining seconds: ' + str(test_timeout))
    print(protractor_cmd)

    test_timed_out = False

    console_output = '/tmp/console.log'

    # TODO: Pass custom environment vars to prevent task from accessing anything sensitive
    run_test = subprocess.Popen(protractor_cmd,
                                stderr=subprocess.STDOUT,
                                stdout=open(console_output, 'w'),
                                shell=True)
    try:
        run_test.wait(test_timeout)
    except:
        print('Test timed out')
        test_timed_out = True
        run_test.terminate()

    test_stop_milli = current_time_milli()

    print("###UIA TEST OUTPUT###")
    print(run_test)

    time.sleep(3)
    check_space = subprocess.check_output(["df", "-h", "/tmp"])
    print(check_space)

    cleanup_junk = subprocess.check_output(
        'rm -rf /tmp/homedir/* && rm -rf /tmp/user-data/* && rm -rf /tmp/cache-dir/*; exit 0',
        stderr=subprocess.STDOUT,
        shell=True)

    time.sleep(3)
    check_space_again = subprocess.check_output(["df", "-h", "/tmp"])
    print(check_space_again)

    print(cleanup_junk)
    print('...Finished Running Test!')

    allure_results_s3_path = 'artifacts/' \
                             + test_branch_job_identifier \
                             + '/' \
                             + timestamp_for_test_metrics \
                             + '/allure-results/'

    allure_links_s3_path = 'artifacts/' \
                             + test_branch_job_identifier \
                             + '/' \
                             + timestamp_for_test_metrics \
                             + '/allure-artifacts/'

    test_error_screenshot_s3_path = allure_links_s3_path + '/' + job_id.replace("/", "-") + ".mp4"
    chrome_log_path = allure_links_s3_path + '/' + job_id.replace("/", "-") + ".log"
    chrome_driver_log_path = allure_links_s3_path + '/' + job_id.replace("/", "-") + ".chromedriver.log"
    console_log_path = allure_links_s3_path + '/' + job_id.replace("/", "-") + ".console.log"

    test_error_screenshot_s3_path_link = 'artifacts/' + job_id.replace("/", "-") + ".mp4"
    chrome_log_path_link = 'artifacts/' + job_id.replace("/", "-") + ".log"
    chrome_driver_log_path_link = 'artifacts/' + job_id.replace("/", "-") + ".chromedriver.log"
    console_log_path_link = 'artifacts/' + job_id.replace("/", "-") + ".console.log"

    allure_links = [
        create_link('Test Video', test_error_screenshot_s3_path_link, 'video/mp4'),
        create_link('Chrome Log', chrome_log_path_link),
        create_link('Chrome Driver Log', chrome_driver_log_path_link),
        create_link('Console Log', console_log_path_link),
        cloud_watch_logs.get_allure_link()
    ]

    # Search for allure test result and upload specific test execution
    allure_test_case_found = False
    if allure_results_directory_exists() and allure_results_directory_contains_files():
        for json_result in get_json_results():
            result = open(json_result).read()
            data = json.loads(result)
            found_name = ''.join(e for e in data['name'] if e.isalnum())
            expected_name = ''.join(e for e in test_name if e.isalnum())
            
            if found_name == expected_name:
                print('Allure result found: ' + json_result)
                allure_test_case_found = True
                data['links'].extend(allure_links)
                data['labels'].extend(get_host_labels())
                key = allure_results_s3_path + str(uuid.uuid4()) + '-result.json'
                upload_allure_result(s3, artifact_s3_bucket, key, data)
            else:
                print('Looking for: ' + expected_name)
                print('Found: ' + found_name)

    # Generate skipped result if the test execution is not found
    if allure_test_case_found is False:
        print('Allure Test Case Not Found, marking as disabled / skipped / timed out!')
        key = allure_results_s3_path + str(uuid.uuid4()) + '-result.json'
        skipped_result = create_missing_allure_result(test_name,
                                                      test_class_name,
                                                      test_start_milli,
                                                      test_stop_milli,
                                                      allure_links,
                                                      test_timed_out)
        upload_allure_result(s3, artifact_s3_bucket, key, skipped_result)

    # chuck artifacts in s3 within someBucketName/test-runner/jobId/junit.xml, console.txt, error.png
    retry_glob = '/tmp/lambda_protractor/build/test/test/e2e/retry_attempts/*.json'
    junit_glob = '/tmp/lambda_protractor/build/test/test/e2e/results/*.xml'
    retry_helper = RetryCombine(retry_glob)

    if retry_helper.has_retries():
        start_retry = test_start_milli + 1
        stop_retry = start_retry + 1
        full_test_name = test_class_name.replace('E2E.', '') + ' ' + test_name
        for retry in retry_helper.get_matching_retries(full_test_name):
            result = create_retry_allure_results(test_name,
                                                 test_class_name,
                                                 start_retry,
                                                 stop_retry,
                                                 retry.error_msg,
                                                 retry.attempt_number,
                                                 allure_links)
            retry_key = allure_results_s3_path + str(uuid.uuid4()) + '-result.json'
            upload_allure_result(s3, artifact_s3_bucket, retry_key, result)
            start_retry = start_retry + 1
            stop_retry = stop_retry + 1
        
    jasmine_manifest = JasmineManifest([test_file_path], [], [])
    merger = JunitMerger(junit_glob, '/tmp/combined_retry.xml', jasmine_manifest)
    merger.create_report(retry_helper)

    report_file = '/tmp/combined_retry.xml'
    root = XMLTree.parse(report_file)
    test_case_found = False
    test_case_element = XMLTree.Element('testsuite')
    for test_case in root.findall('/testsuite/testcase'):
        name = test_case.get('name').replace("'", "").replace('"', '')
        tn = test_name.replace('\\', "").replace("'", "").replace('"', '')
        if name == tn:
            print("Matching test case found...")
            test_case_found = True
            test_case.set('loggroupid', context.log_group_name)
            test_case.set('logstreamname', context.log_stream_name)
            test_case.set('awsrequestid', context.aws_request_id)
            test_case_element.append(test_case)

    if test_case_found is not True:
        print("Could not find test report, marking as disabled / skipped / timed out!'")
        new_test_case = XMLTree.Element('testcase')
        fixed_name = test_name.replace('\\', "").replace("'", "").replace('"', '')
        new_test_case.set('name', fixed_name)
        new_test_case.set('loggroupid', context.log_group_name)
        new_test_case.set('logstreamname', context.log_stream_name)
        new_test_case.set('awsrequestid', context.aws_request_id)
        new_test_case.set('time', str(test_start_milli - test_stop_milli))
        new_test_case.set('isretried', '0')
        if test_timed_out:
            failure = XMLTree.Element('failed')
            failure.set("message", "Exceeded Timeout in AWS Lambda, see cloudwatch log!")
            failure.set("type", "AWS_TIMEOUT")
            new_test_case.set('classname', 'E2E.Expired')
            new_test_case.set("isexpired", "true")
            new_test_case.set("isfailed", "true")
            new_test_case.append(failure)
        else:
            new_test_case.set('classname', 'E2E.Disabled')
            new_test_case.append(XMLTree.Element('skipped'))
        test_case_element.append(new_test_case)

    # Write the completed junit report
    xmlstr = minidom.parseString(XMLTree.tostring(test_case_element)).toprettyxml()
    with open('/tmp/report.xml', "w") as f:
        f.write(xmlstr)

    print('Modified Test report found, attempting to upload /tmp/report.xml to S3 destination ' + junit_report_s3_path)
    s3.Object(artifact_s3_bucket, junit_report_s3_path).put(Body=open('/tmp/report.xml', 'rb'))

    record_vid.communicate("q".encode())  # stop recording
    # kill chromedriver
    os.killpg(os.getpgid(chromedriver.pid), signal.SIGTERM)
    # kill  xvfb
    os.killpg(os.getpgid(start_xvfb.pid), signal.SIGTERM)

    try:
        s3.Object(artifact_s3_bucket, test_error_screenshot_s3_path).put(Body=open('/tmp/videoFile.mp4', 'rb'),
                                                                         ContentType='video/mp4',
                                                                         ContentDisposition='inline')
    except:
        print('Unable to upload video file')

    try:
        s3.Object(artifact_s3_bucket, chrome_log_path).put(Body=open('/tmp/chrome_debug.log', 'rb'),
                                                           ContentType='text/plain; charset=UTF-8',
                                                           ContentDisposition='inline')
    except:
        print('Unable to upload chrome debug log')

    try:
        s3.Object(artifact_s3_bucket, chrome_driver_log_path).put(Body=open('/tmp/chromedriver.log', 'rb'),
                                                                  ContentType='text/plain; charset=UTF-8',
                                                                  ContentDisposition='inline')
    except:
        print('Unable to upload chromedriver log')

    try:
        s3.Object(artifact_s3_bucket, console_log_path).put(Body=open(console_output, 'rb'),
                                                            ContentType='text/plain; charset=UTF-8',
                                                            ContentDisposition='inline')
    except:
        print('Unable to upload console log')

    test_finish = str(datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%f"))
    print("Marking test finish in database with the following stamp: " + test_finish)
    put_attributes(sdb, sdb_domain, job_id, "testFinish", test_finish)
