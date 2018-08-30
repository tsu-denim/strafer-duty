import datetime
import hashlib
import json
import os
import pathlib
import re
import subprocess
import time
import glob
import boto3
from functions.lib.manifest import JasmineManifest
from functions.lib.junit_formatter import AllureHelper


def get_branch_name():

    print('###################################################')
    print("#################### WARNING! #####################")
    print("BRANCH NAME IS HARDCODED TO BE 'straferduty-manual'")
    print('###################################################')

    branch_name_stripped = 'straferduty-manual'
    # TODO: Update this to work in Github
    # Grab the branch name from git

    # git_command = 'git describe --contains --all HEAD'
    #
    # call_git_command = subprocess.check_output(git_command,
    #                                            stderr=subprocess.STDOUT,
    #                                            shell=True,
    #                                            preexec_fn=os.setsid)
    #
    # # Format branch name so it can be used as a CloudFormation stack name
    # branch_name_stripped = call_git_command.decode('utf-8').replace('remotes/origin/', '').replace('/', '-').rstrip(
    #     "\n\r").lstrip("\n\r")
    # branch_name_stripped = re.sub(r'/', '-', branch_name_stripped)
    # branch_name_stripped = re.sub(r'_', '-', branch_name_stripped)
    return branch_name_stripped


def get_stack_name_from_branch(branch_name):
    # Format branch name so it can be used as a CloudFormation stack name

    branch_name_stripped = branch_name.replace('remotes/origin/', '').replace('/', '-').rstrip("\n\r").lstrip("\n\r")
    branch_name_stripped = re.sub(r'/', '-', branch_name_stripped)
    branch_name_stripped = re.sub(r'_', '-', branch_name_stripped)
    return branch_name_stripped


def get_step_function_name(stack_name, credential_object):
    cloud_formation_client = boto3.client('cloudformation', region_name='us-east-1',
                                          aws_access_key_id=credential_object['Credentials']['AccessKeyId'],
                                          aws_secret_access_key=credential_object['Credentials']['SecretAccessKey'],
                                          aws_session_token=credential_object['Credentials']['SessionToken'], )
    stack_resource_list = cloud_formation_client.list_stack_resources(StackName=stack_name)
    is_step_function_found = False
    step_function = ''
    # Find the Step Function name for running the tests later
    for item in stack_resource_list["StackResourceSummaries"]:
        if item["ResourceType"] == "AWS::StepFunctions::StateMachine" and "TaskRunner" in \
                item["LogicalResourceId"]:
            step_function = item["PhysicalResourceId"]
            print("### STEP FUNCTION FOUND IN CLOUDFORMATION STACK: " + step_function)
            is_step_function_found = True
            break
    if is_step_function_found is False:
        raise ("Step Function was not found in cloud formation stack: " + stack_name)
    return step_function


def get_simple_db_domain(stack_name, credential_object):
    cloud_formation_client = boto3.client('cloudformation', region_name='us-east-1',
                                          aws_access_key_id=credential_object['Credentials']['AccessKeyId'],
                                          aws_secret_access_key=credential_object['Credentials']['SecretAccessKey'],
                                          aws_session_token=credential_object['Credentials']['SessionToken'], )
    stack_resource_list = cloud_formation_client.list_stack_resources(StackName=stack_name)
    is_domain_found = False
    sdb_domain = ''
    # Find the Step Function name for running the tests later
    for item in stack_resource_list["StackResourceSummaries"]:
        if item["ResourceType"] == "AWS::SDB::Domain" and "TaskRunnerDomain" in item["LogicalResourceId"]:
            sdb_domain = item["PhysicalResourceId"]
            print("### SIMPLE DB DOMAIN FOUND IN CLOUDFORMATION STACK: " + sdb_domain)
            is_domain_found = True
            break
    if is_domain_found is False:
        raise ("Step Function was not found in cloud formation stack: " + stack_name)
    return sdb_domain


def get_bucket_name(stack_name, credential_object):
    cloud_formation_client = boto3.client('cloudformation', region_name='us-east-1',
                                          aws_access_key_id=credential_object['Credentials']['AccessKeyId'],
                                          aws_secret_access_key=credential_object['Credentials']['SecretAccessKey'],
                                          aws_session_token=credential_object['Credentials']['SessionToken'], )
    stack_resource_list = cloud_formation_client.list_stack_resources(StackName=stack_name)
    is_bucket_found = False
    bucket_name = ''
    # Find the Step Function name for running the tests later
    for item in stack_resource_list["StackResourceSummaries"]:
        if item["ResourceType"] == "AWS::S3::Bucket" and "TaskStore" in item["LogicalResourceId"]:
            bucket_name = item["PhysicalResourceId"]
            print("### BUCKET NAME FOUND IN CLOUDFORMATION STACK: " + bucket_name)
            is_bucket_found = True
            break
    if is_bucket_found is False:
        raise ("Step Function was not found in cloud formation stack: " + stack_name)
    return bucket_name


def put_manifest_task_simple_db(sdb, domain, item, job_id, test_index, file_location, test_name, test_class_name):
    response = sdb.put_attributes(
        DomainName=domain,
        ItemName=item,
        Attributes=[
            {
                'Name': 'jobId',
                'Value': job_id,
                'Replace': True
            },
            {
                'Name': 'testIndex',
                'Value': test_index,
                'Replace': True
            },
            {
                'Name': 'fileLocation',
                'Value': file_location,
                'Replace': True
            },
            {
                'Name': 'testName',
                'Value': test_name,
                'Replace': True
            },
            {
                'Name': 'testClassName',
                'Value': test_class_name,
                'Replace': True
            },
        ],
    )
    print(response)


def put_manifest_sdb(creds, sdb_domain, config_dict):
    sdb_client = boto3.client('sdb', region_name='us-east-1',
                              aws_access_key_id=creds['Credentials']['AccessKeyId'],
                              aws_secret_access_key=creds['Credentials']['SecretAccessKey'],
                              aws_session_token=creds['Credentials']['SessionToken'], )
    local_source_root = config_dict['localSourceRoot']
    lambda_source_root = config_dict['lambdaSourceRoot']

    manifest = JasmineManifest(config_dict['testGlobs'], config_dict['includeTags'], config_dict['excludeTags'])

    every_test = manifest.get_all_runnable_tests()
    tests = every_test

    test_index = 1
    job_id = config_dict['executionName']

    for test in tests:
        db_key = str(test_index) + '/' + job_id
        test_path = test.test_path.replace(local_source_root, lambda_source_root)
        put_manifest_task_simple_db(sdb_client,
                                    sdb_domain,
                                    db_key,
                                    job_id,
                                    str(test_index).zfill(8),
                                    test_path,
                                    test.test_name,
                                    test.test_class_name)
        if config_dict["maxTestsToRun"] == "1":
            print("RUNNING JOB IN SMOKE MODE! ONLY SCHEDULING ONE TASK IN DB")
            break
        test_index = test_index + 1


def mock_expired_test_simple_db(sdb, domain, item, job_id, test_index, file_location, test_name, is_setup,
                                sequence_index,
                                message_time, test_start, test_id, bucket_name):
    response = sdb.put_attributes(
        DomainName=domain,
        ItemName=item,
        Attributes=[
            {
                'Name': 'jobId',
                'Value': job_id,
                'Replace': True
            },
            {
                'Name': 'testIndex',
                'Value': test_index,
                'Replace': True
            },
            {
                'Name': 'fileLocation',
                'Value': file_location,
                'Replace': True
            },
            {
                'Name': 'testName',
                'Value': test_name,
                'Replace': True
            },
            {
                'Name': 'isSetup',
                'Value': is_setup,
                'Replace': True
            },
            {
                'Name': 'sequenceIndex',
                'Value': sequence_index,
                'Replace': True
            },
            {
                'Name': 'messageTime',
                'Value': message_time,
                'Replace': True
            },
            {
                'Name': 'sequenceIndex',
                'Value': sequence_index,
                'Replace': True
            },
            {
                'Name': 'jobId',
                'Value': job_id,
                'Replace': True
            },
            {
                'Name': 'testIndex',
                'Value': test_index,
                'Replace': True
            },
            {
                'Name': 'fileLocation',
                'Value': file_location,
                'Replace': True
            },
            {
                'Name': 'testName',
                'Value': test_name,
                'Replace': True
            },
            {
                'Name': 'isSetup',
                'Value': is_setup,
                'Replace': True
            },
            {
                'Name': 'sequenceIndex',
                'Value': sequence_index,
                'Replace': True
            },
            {
                'Name': "testStart",
                'Value': test_start,
                'Replace': True
            },
            {
                'Name': "testId",
                'Value': test_id,
                'Replace': True
            },
            {
                'Name': "artifactS3Bucket",
                'Value': bucket_name,
                'Replace': True
            },
            {
                'Name': "artifactS3Path",
                'Value': "NA",
                'Replace': True
            },
            {
                'Name': "logStreamGroup",
                'Value': "NA",
                'Replace': True
            },
            {
                'Name': "logStreamName",
                'Value': "NA",
                'Replace': True
            },
            {
                'Name': "requestId",
                'Value': "NA",
                'Replace': True
            }
        ],
    )
    print(response)


def create_expired_test(credential_object, execution_name, current_date, stack_name, bucket_name):
    print("Simulating expired test in simple db...")
    sdb = boto3.client('sdb', region_name='us-east-1',
                       aws_access_key_id=credential_object['Credentials']['AccessKeyId'],
                       aws_secret_access_key=credential_object['Credentials']['SecretAccessKey'],
                       aws_session_token=credential_object['Credentials']['SessionToken'])

    domain = get_simple_db_domain(stack_name, credential_object)

    seven_minutes_ago = current_date - datetime.timedelta(minutes=7)
    six_minutes_ago = current_date - datetime.timedelta(minutes=6)

    test_index = "99"
    db_key = test_index + '/' + execution_name
    file_loc = "some/folder.js"
    test_nm = "Expired test is considered failed"
    test_id = "5"
    sequence_id = "0"
    msg_time = str(seven_minutes_ago.strftime("%y-%m-%d-%H-%M-%f"))
    test_st = str(six_minutes_ago.strftime("%y-%m-%d-%H-%M-%f"))
    is_setup = "false"

    mock_expired_test_simple_db(sdb, domain, db_key, execution_name, test_index, file_loc, test_nm, is_setup,
                                sequence_id, msg_time, test_st, test_id, bucket_name)


# Produces a message digest, aka hash, for a given file
def md5_checksum(file_path):
    with open(file_path, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()


def get_config_dict_from_json(json_config_path, tar_path):
    configuration_values = json.load(open(json_config_path, encoding='utf-8'))

    # Hash the tarball
    file_name = md5_checksum(tar_path)
    prefix = configuration_values["s3KeyPrefix"]
    s3_key = prefix + file_name + ".tar.gz"
    configuration_values["protractorTarballS3Path"] = s3_key
    configuration_values["localTarPath"] = tar_path

    now = datetime.datetime.now()
    configuration_values["executionName"] = str(now.strftime("%y-%m-%d-%H-%M-%f"))
    configuration_values["timestampForTestMetrics"] = str(now.strftime("%Y%m%dT%H%M%S%f"))
    configuration_values["testBranchJobIdentifier"] = get_branch_name()

    return configuration_values


def upload_tarball_to_s3(config_dict, sts_creds, bucket_name):
    s3 = boto3.resource('s3', region_name='us-east-1',
                        aws_access_key_id=sts_creds['Credentials']['AccessKeyId'],
                        aws_secret_access_key=sts_creds['Credentials']['SecretAccessKey'],
                        aws_session_token=sts_creds['Credentials']['SessionToken'])

    bucket_name = str(bucket_name)
    print("Bucket name: " + bucket_name)
    bucket = s3.Bucket(bucket_name)
    s3_key = config_dict['protractorTarballS3Path']

    objs = list(bucket.objects.filter(Prefix=s3_key))
    if len(objs) > 0 and objs[0].key == s3_key:
        print("Exact tarball already exists in S3, skipping unnecessary upload.")
    else:
        file_to_upload = config_dict['localTarPath']
        file_handle = open(file_to_upload, 'rb')
        print("Uploading tarball into S3: " + file_to_upload)
        print("S3 Key of Upload: " + s3_key)
        s3.Object(bucket_name, s3_key).put(Body=file_handle)


def get_sts_credentials(role_arn_to_assume):
    sts_client = boto3.client('sts')
    credential_object = sts_client.assume_role(
        RoleArn=role_arn_to_assume,
        RoleSessionName="AssumeRoleSession1"
    )
    return credential_object


def execute_test_runner(config_dict, sts_creds, arn_of_state_machine):
    payload = json.dumps(config_dict)
    execution_name = config_dict['executionName']
    state_machine_client = boto3.client('stepfunctions', region_name='us-east-1',
                                        aws_access_key_id=sts_creds['Credentials']['AccessKeyId'],
                                        aws_secret_access_key=sts_creds['Credentials']['SecretAccessKey'],
                                        aws_session_token=sts_creds['Credentials']['SessionToken'])

    execution_response = state_machine_client.start_execution(
        stateMachineArn=arn_of_state_machine,
        name=execution_name,
        input=payload
    )

    execution_id = execution_response.get('executionArn')

    print("Job ID: " + execution_id)
    return execution_id


def get_test_result_metrics_list():
    metrics_test_results = []

    metric_file_directory = 'metrics-results'
    os.makedirs(metric_file_directory)

    for filename in glob.glob(os.path.join('allure-results', '*-result.json')):
        print('Path: ' + filename)
        json_data = open(filename).read()
        data = json.loads(json_data)
        metric_test_result = {
            'fullName': data['fullName'],
            'historyId': data['historyId'],
            'host': 'Lambda',
            'thread': 'thread',
            'name': data.get('name'),
            'stage': data.get('stage'),
            'start': data.get('start'),
            'status': data.get('status'),
            'stop': data.get('stop'),
            'uuid': data.get('uuid'),
            'branch': os.environ.get('GIT_BRANCH'),
            'job': os.environ.get('JOB_NAME'),
            'table': 'TEST_RESULT'
        }

        for label in data.get('labels'):
            # switch this back
            metric_test_result[label.get('name')] = label.get('value')

        if 'host' not in data:
            data['host'] = 'OnlyContainer'
            data['thread'] = 'OnlyContainer'

        metric_test_result['statusDetailMessage'] = data.get('statusDetails').get('message')
        metric_test_result['statusDetailTrace'] = data.get('statusDetails').get('trace')

        metric_test_result['feature'] = data.get('feature')
        metric_test_result['story'] = data.get('story')
        metric_test_result['epic'] = data.get('epic')
        metric_test_result['description'] = data.get('description')
        metric_test_result['descriptionHtml'] = data.get('descriptionHtml')
        metric_test_result['uniqueName'] = ''.join(e for e in data.get('fullName') if e.isalnum())

        metrics_test_results.append(metric_test_result)
        output_path = os.path.join(metric_file_directory, metric_test_result.get('uniqueName'))
        print('Output path: ' + output_path)
        with open(output_path, 'w') as output_file:
            output_file.write(json.dumps(metric_test_result, sort_keys=True))

    return metric_file_directory


def monitor_state_machine(sts_creds, execution_id):
    # Await state machine outcome
    state_machine_client = boto3.client('stepfunctions', region_name='us-east-1',
                                        aws_access_key_id=sts_creds['Credentials']['AccessKeyId'],
                                        aws_secret_access_key=sts_creds['Credentials']['SecretAccessKey'],
                                        aws_session_token=sts_creds['Credentials']['SessionToken'])

    machine_state = "RUNNING"
    timeout = time.time() + 60 * 45  # 45 minutes from now
    status_count = 1
    while machine_state == 'RUNNING':
        time_elapsed = ((status_count * 10) / 60)
        # TODO: Improve precision for number of minutes elapsed, currently prints fractions of minutes too long
        print("Time elapsed: " + str(time_elapsed))
        status_count = status_count + 1
        if time.time() > timeout:
            print("Test Execution Exceeding 30 minutes, something went wrong! Check AWS Logs...")
            break
        print('Checking task runner progress...')
        time.sleep(10)
        execution_state_response = state_machine_client.describe_execution(executionArn=execution_id)
        machine_state = execution_state_response.get('status')
        print('Current Status: ' + machine_state)

    if machine_state == 'SUCCEEDED':
        state_machine_output_json = state_machine_client.describe_execution(executionArn=execution_id).get('output')
        formatted_output = json.loads(state_machine_output_json)
        print("Final Job Status: " + machine_state)
        print("UIA Test Report: " + formatted_output.get('reportUrl'))
    else:
        error_message = 'AWS STEP FUNCTION ERROR! See AWS Step Function Console! Error Status: ' + machine_state
        print(error_message)
        raise RuntimeError(error_message)


def get_artifacts(bucket_name, sts_creds, report_destination_path, config_dict):
    s3 = boto3.resource('s3', region_name='us-east-1',
                        aws_access_key_id=sts_creds['Credentials']['AccessKeyId'],
                        aws_secret_access_key=sts_creds['Credentials']['SecretAccessKey'],
                        aws_session_token=sts_creds['Credentials']['SessionToken'])

    pathlib.Path('junit_results').mkdir(parents=True, exist_ok=True)
    test_report_bucket = bucket_name
    test_report_key = 'artifacts/' + config_dict['testBranchJobIdentifier'] + '/' + config_dict[
        'timestampForTestMetrics'] + '.xml'
    test_stylesheet_key = 'artifacts/' + config_dict['testBranchJobIdentifier'] + '/stylesheet.xsl'

    s3.Bucket(test_report_bucket).download_file(test_report_key, report_destination_path)
    stylesheet_path = str(pathlib.Path(report_destination_path).parent.joinpath('stylesheet.xsl'))
    s3.Bucket(test_report_bucket).download_file(test_stylesheet_key, stylesheet_path)

    # Create temporary shell environment with AWS creds from STS
    new_env = os.environ.copy()
    new_env['AWS_ACCESS_KEY_ID'] = sts_creds['Credentials']['AccessKeyId']
    new_env['AWS_SECRET_ACCESS_KEY'] = sts_creds['Credentials']['SecretAccessKey']
    new_env['AWS_SESSION_TOKEN'] = sts_creds['Credentials']['SessionToken']

    aws_command_template_results = 'aws s3 cp s3://{}/artifacts/' + config_dict['testBranchJobIdentifier'] + '/' \
                  + config_dict['timestampForTestMetrics'] + '/allure-results/ allure-results --recursive'
    aws_command_results = aws_command_template_results.format(bucket_name)

    aws_command_template_artifacts = 'aws s3 cp s3://{}/artifacts/' + config_dict['testBranchJobIdentifier'] + '/' \
                           + config_dict['timestampForTestMetrics'] + '/allure-artifacts/ artifacts --recursive'
    aws_command_artifacts = aws_command_template_artifacts.format(bucket_name)

    print('Running command: ' + aws_command_results)
    call_aws_command_results = subprocess.Popen(aws_command_results,
                                        stderr=subprocess.STDOUT,
                                        shell=True,
                                        preexec_fn=os.setsid,
                                        env=new_env)

    print('Running command: ' + aws_command_artifacts)
    call_aws_command_artifacts = subprocess.Popen(aws_command_artifacts,
                                        stderr=subprocess.STDOUT,
                                        shell=True,
                                        preexec_fn=os.setsid,
                                        env=new_env)

    call_aws_command_results.wait()
    call_aws_command_artifacts.wait()
    allure_helper = AllureHelper('allure-results/*.json')
    manifest = JasmineManifest(config_dict["testGlobs"], ["#quarantine", "#new", "#nobackendsupport", "#setup"], [])
    allure_helper.update_results(manifest)
