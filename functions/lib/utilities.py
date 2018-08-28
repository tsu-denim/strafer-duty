import datetime
import os
import time

import boto3
import botocore

from functions.lib.manifest import JasmineManifest


def get_sdb_paginator_for_test_results(sdb_domain, job_id):
    query = """select * from `{}` where itemName() like '%{}%' """
    query_formatted = query.format(sdb_domain, job_id)
    print("SDB Query: " + query_formatted)
    client = boto3.client('sdb')
    paginator = client.get_paginator('select')
    page_iterator = paginator.paginate(SelectExpression=query_formatted)
    return page_iterator


def get_sdb_paginator_for_expired_tests(sdb_domain, job_id):
    expired_query = """select * from `{}` where itemName() like '%{}%' and testExpiration is not null"""
    expired_query_formatted = expired_query.format(sdb_domain, job_id)
    print("SDB Query: " + expired_query_formatted)
    client = boto3.client('sdb')
    expired_paginator = client.get_paginator('select')
    expired_page_iterator = expired_paginator.paginate(SelectExpression=expired_query_formatted)
    return expired_page_iterator


def download_test_reports(page_iterator, artifact_s3_prefix, artifact_s3_bucket, tmp_directory, s3_client):
    print("Downloading junit reports...")
    for query_result in page_iterator:
        if "Items" in query_result:
            for record in query_result["Items"]:

                artifact_s3_path = artifact_s3_prefix + record["Name"]
                junit_s3_source_path = artifact_s3_path + "/" + record["Name"].replace("/", "-") + ".xml"
                junit_destination_path = tmp_directory + "/artifacts/" + record["Name"].replace("/", "-") + ".xml"
                try:
                    s3_client.Bucket(artifact_s3_bucket).download_file(junit_s3_source_path, junit_destination_path)
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "404":
                        print("The junit report- " + junit_s3_source_path + " -does not exist.")
                    else:
                        raise


def get_expired_test_list(expired_page_iterator, tmp_directory):
    expired_test_list = []
    print("Querying for expired tests...")
    for query_result in expired_page_iterator:
        if "Items" in query_result:
            for record in query_result["Items"]:
                test_id = record["Name"].replace("/", "-")
                junit_destination_path = tmp_directory + "/artifacts/" + test_id + ".xml"
                if not os.path.isfile(junit_destination_path):
                    report_template = '''
<testsuite>
<testcase awsrequestid="{}" classname="E2E.Expired" jobId="{}" loggroupid="{}" logstreamname="{}" name="{}" testid="{}" testindex="{}" time="0">
</testcase>
</testsuite>
'''
                    report = report_template.format(get_sdb_record_attribute(record, "requestId"),
                                                    get_sdb_record_attribute(record, "jobId"),
                                                    get_sdb_record_attribute(record, "logStreamGroup"),
                                                    get_sdb_record_attribute(record, "logStreamName"),
                                                    get_sdb_record_attribute(record, "testName"),
                                                    get_sdb_record_attribute(record, "testId"),
                                                    get_sdb_record_attribute(record, "testIndex"))
                    with open(junit_destination_path, "w+", encoding='utf-8') as f:
                        f.write(report)
                        f.close()
                        print("Created report for expired test: " + junit_destination_path)
                        print("REPORT CONTENTS")
                        print(report)

                expired_test_list.append(test_id)
                print("Added expired test to list: " + test_id)
    return expired_test_list


def get_sdb_record_attribute(record, attribute_name):
    record_value = ""
    for attrib in record["Attributes"]:
        if attrib["Name"] == attribute_name:
            record_value = attrib["Value"]
            break

    return record_value


def schedule_tests(page_iterator, test_delay_in_seconds, event, sdb, sdb_domain, bucket_name):
    sns = boto3.client('sns')
    sns_topic = os.environ['SNSTOPIC']

    assumable_role = os.environ['ASSUMABLEROLE']
    assume_role = "false"
    run_with_vpc = event['runTestWithVpc']

    if run_with_vpc == "true":
        print("Setting SNS Topic to External Account")
        sns_topic = os.environ['SNSEXTERNALTOPIC']
        assume_role = "true"

    for query_result in page_iterator:
        if "Items" in query_result:
            for record in query_result["Items"]:
                if test_delay_in_seconds > 0:
                    time.sleep(test_delay_in_seconds)
                test_index = get_sdb_record_attribute(record, "testIndex")
                test_name = get_sdb_record_attribute(record, "testName")
                test_class_name = get_sdb_record_attribute(record, "testClassName")
                test_file_path = get_sdb_record_attribute(record, "fileLocation")
                # More temp documentation
                print('Test Index is: ' + test_index)
                print('Test name is: ' + test_name)
                print('testFilePath is: ' + test_file_path)
                sns.publish(
                    TopicArn=sns_topic,
                    Subject='SNS Test Execution',
                    Message=record["Name"],
                    MessageAttributes={
                        "ServerLogin": {
                            "DataType": "String",
                            "StringValue": event['serverLogin']
                        },
                        "ServerPassword": {
                            "DataType": "String",
                            "StringValue": event['serverPassword']
                        },
                        "ServerUrl": {
                            "DataType": "String",
                            "StringValue": event['serverUrl']
                        },
                        "TestId": {
                            "DataType": "String",
                            "StringValue": test_index
                        },
                        "TestName": {
                            "DataType": "String",
                            "StringValue": test_name
                        },
                        "TestClassName": {
                            "DataType": "String",
                            "StringValue": test_class_name
                        },
                        "TestFilePath": {
                            "DataType": "String",
                            "StringValue": test_file_path
                        },
                        "TarballS3Bucket": {
                            "DataType": "String",
                            "StringValue": bucket_name
                        },
                        "NodeRuntimeS3Path": {
                            "DataType": "String",
                            "StringValue": event['nodeRuntimeS3Path']
                        },
                        "SystemLibsS3Path": {
                            "DataType": "String",
                            "StringValue": event['systemLibsS3Path']
                        },
                        "XvfbS3Path": {
                            "DataType": "String",
                            "StringValue": event['xvfbS3Path']
                        },
                        "ProtractorTarballS3Path": {
                            "DataType": "String",
                            "StringValue": event['protractorTarballS3Path']
                        },
                        "AssumeRoleBoolean": {
                            "DataType": "String",
                            "StringValue": assume_role
                        },
                        "AssumableRoleArn": {
                            "DataType": "String",
                            "StringValue": assumable_role
                        },
                        "RunTestCommand": {
                            "DataType": "String",
                            "StringValue": event['runTestCommand']
                        },
                        "TestBranchId": {
                            "DataType": "String",
                            "StringValue": event['testBranchJobIdentifier']
                        },
                        "MetricsId": {
                            "DataType": "String",
                            "StringValue": event['timestampForTestMetrics']
                        }
                    }
                )
                now = datetime.datetime.now()
                message_time = str(now.strftime("%y-%m-%d-%H-%M-%f"))
                db_response = sdb.put_attributes(
                    DomainName=sdb_domain,
                    ItemName=record["Name"],
                    Attributes=[
                        {
                            'Name': 'messageTime',
                            'Value': message_time,
                            'Replace': True
                        },
                    ],
                )
                print(db_response)


def get_number_of_tests_to_schedule(batch_size, parallel_tests_running_count):
    print("Checking open test slots...")
    total_slots_filled =  parallel_tests_running_count
    print("Total Slots Full: " + str(total_slots_filled))
    number_of_open_slots = 0
    if batch_size > total_slots_filled:
        number_of_open_slots = batch_size - total_slots_filled
    print("Total Remaining Slots: " + str(number_of_open_slots))

    number_of_parallel_slots_open = number_of_open_slots
    number_of_parallel_slots_to_schedule = 0

    if number_of_parallel_slots_open > 0:
        number_of_parallel_slots_to_schedule = number_of_parallel_slots_open
    print("Number of Parallel Slots Open: " + str(number_of_parallel_slots_to_schedule))
    return number_of_parallel_slots_to_schedule


def get_simple_db_client(assume_role, role_arn):
    if assume_role == "true":
        print("Attempting to assume AWS role " + role_arn)
        sts_client = boto3.client('sts')

        # Call the assume_role method of the STSConnection object and pass the role
        # ARN and a role session name.
        role_to_assume = role_arn

        credential_object = sts_client.assume_role(
            RoleArn=role_to_assume,
            RoleSessionName="AssumeRoleSdb"
        )

        return boto3.client('sdb', region_name='us-east-1',
                            aws_access_key_id=credential_object['Credentials']['AccessKeyId'],
                            aws_secret_access_key=credential_object['Credentials']['SecretAccessKey'],
                            aws_session_token=credential_object['Credentials']['SessionToken'], )
    return boto3.client('sdb')


def get_s3_resource(assume_role, role_arn):
    if assume_role == "true":
        print("Attempting to assume AWS role " + role_arn)
        sts_client = boto3.client('sts')

        # Call the assume_role method of the STSConnection object and pass the role
        # ARN and a role session name.
        role_to_assume = role_arn

        credential_object = sts_client.assume_role(
            RoleArn=role_to_assume,
            RoleSessionName="AssumeRoleSdb"
        )

        return boto3.resource('s3', region_name='us-east-1',
                              aws_access_key_id=credential_object['Credentials']['AccessKeyId'],
                              aws_secret_access_key=credential_object['Credentials']['SecretAccessKey'],
                              aws_session_token=credential_object['Credentials']['SessionToken'], )

    return boto3.resource('s3')


def put_attributes(sdb, domain, item, att_name, att_val):
    response = sdb.put_attributes(
        DomainName=domain,
        ItemName=item,
        Attributes=[
            {
                'Name': att_name,
                'Value': att_val,
                'Replace': True
            },
        ],
    )
    print(response)


def sdb_put_test_start(sdb, sdb_domain, job_id, test_start, test_id, artifact_s3_bucket, artifact_s3_path, context):
    sdb_response = sdb.put_attributes(
        DomainName=sdb_domain,
        ItemName=job_id,
        Attributes=[
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
                'Value': artifact_s3_bucket,
                'Replace': True
            },
            {
                'Name': "artifactS3Path",
                'Value': artifact_s3_path,
                'Replace': True
            },
            {
                'Name': "logStreamGroup",
                'Value': context.log_group_name,
                'Replace': True
            },
            {
                'Name': "logStreamName",
                'Value': context.log_stream_name,
                'Replace': True
            },
            {
                'Name': "requestId",
                'Value': context.aws_request_id,
                'Replace': True
            }
        ],
    )
    print(sdb_response)


def current_time_milli():
    return int(round(time.time() * 1000))
