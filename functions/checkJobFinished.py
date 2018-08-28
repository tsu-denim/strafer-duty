import json
import os

import boto3


def handler(event, context):
    print('Event: ')
    print(json.dumps(event, sort_keys=False))

    json_data = json.dumps(event, indent=2)
    job_id = event["executionName"]
    sdb_domain = os.environ['SDBDOMAIN']
    print(json_data)
    query = """select count(*) from `{}` where (testFinish is null and testExpiration is null) and itemName() like '%{}%' """
    query_formatted = query.format(sdb_domain, job_id)
    print(query_formatted)
    client = boto3.client('sdb')
    response = client.select(
        SelectExpression=query_formatted,
        ConsistentRead=True)
    count = response['Items'][0]['Attributes'][0]['Value']
    print('Tasks still working: ' + count)
    if count == "0":
        return 'jobComplete'
    else:
        return 'jobWorking'
