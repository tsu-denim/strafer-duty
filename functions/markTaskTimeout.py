from __future__ import print_function

import datetime
import json
import os

import boto3
from dateutil import relativedelta

from functions.lib.binary_service import clear_tmp
from functions.lib.utilities import get_sdb_record_attribute


def handler(event, context):
    print('Event: ')
    print(json.dumps(event, sort_keys=False))

    job_id = event['executionName']
    batch_size = int(event['batchSize'])
    sdb_domain = os.environ['SDBDOMAIN']

    clear_tmp()

    # Read db for job metadata
    query = """select * from `{}` where itemName() like '%{}%' and testStart is not null and testFinish is null"""
    query_formatted = query.format(sdb_domain, job_id)
    print(query_formatted)
    sdb = boto3.client('sdb')
    paginator = sdb.get_paginator('select')
    page_iterator = paginator.paginate(SelectExpression=query_formatted, PaginationConfig={
        'MaxItems': batch_size
    })

    expired_tasks_found = 0

    if 'expiredTasksFound' in event:
        expired_tasks_found = int(event['expiredTasksFound'])

    if page_iterator:
        for query_result in page_iterator:
            if "Items" in query_result:
                for record in query_result["Items"]:
                    now = datetime.datetime.now()
                    test_message_date_string = get_sdb_record_attribute(record, "testStart")
                    test_message_date = datetime.datetime.strptime(test_message_date_string, "%y-%m-%d-%H-%M-%f")
                    difference = relativedelta.relativedelta(now, test_message_date)
                    minutes = difference.minutes
                    if minutes >= 6:
                        expired_time = str(now.strftime("%y-%m-%d-%H-%M-%f"))
                        dbresponse = sdb.put_attributes(
                            DomainName=sdb_domain,
                            ItemName=record["Name"],
                            Attributes=[
                                {
                                    'Name': 'testExpiration',
                                    'Value': expired_time,
                                    'Replace': True
                                },
                            ],
                        )
                        print(dbresponse)
                        expired_tasks_found = expired_tasks_found + 1

    return expired_tasks_found
