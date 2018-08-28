import json
import os

import boto3

from functions.lib.binary_service import clear_tmp
from functions.lib.utilities import get_number_of_tests_to_schedule, schedule_tests


def handler(event, context):
    print('Event: ')
    print(json.dumps(event, sort_keys=False))

    sdb = boto3.client('sdb')
    sdb_domain = os.environ['SDBDOMAIN']
    bucket_name = os.environ['TASKRUNNERBUCKET']

    job_id = event['executionName']
    batch_size = int(event['batchSize'])
    test_delay_in_seconds = int(event['testDelayInSeconds'])

    clear_tmp()

    # Read db for job metadata
    query_parallel_tests_not_run = """select * from `{}` where itemName() like '%{}%' 
    and messageTime is null """.format(sdb_domain, job_id)

    query_parallel_tests_still_running = """select count(*) from `{}` where itemName() like '%{}%'
    and messageTime is not null and `testFinish` is null and testExpiration is null 
    """.format(sdb_domain, job_id)

    print('Query for tests not yet executed: ' + query_parallel_tests_not_run)
    print('Query for tests still running: ' + query_parallel_tests_still_running)

    query_parallel_tests_running_response = sdb.select(
        SelectExpression=query_parallel_tests_still_running,
        ConsistentRead=True)

    parallel_tests_running_count = int(query_parallel_tests_running_response['Items'][0]['Attributes'][0]['Value'])

    number_of_parallel_slots_to_schedule = get_number_of_tests_to_schedule(batch_size, parallel_tests_running_count)

    paginator = sdb.get_paginator('select')

    parallel_tests_not_run_query_response = paginator.paginate(SelectExpression=query_parallel_tests_not_run,
                                                               PaginationConfig={
                                                                   'MaxItems': number_of_parallel_slots_to_schedule
                                                               })

    number_of_tasks_invoked = 0
    if 'totalTasksInvoked' in event:
        number_of_tasks_invoked = int(event['totalTasksInvoked'])

    if parallel_tests_not_run_query_response and number_of_parallel_slots_to_schedule > 0:
        schedule_tests(parallel_tests_not_run_query_response,
                       test_delay_in_seconds,
                       event,
                       sdb,
                       sdb_domain,
                       bucket_name)
        number_of_tasks_invoked = number_of_tasks_invoked + number_of_parallel_slots_to_schedule
    else:
        print("SLOTS ARE FULL! Not scheduling any parallel tests!")

    return number_of_tasks_invoked
