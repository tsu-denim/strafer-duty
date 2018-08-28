import glob
import json
import os
import socket
import uuid

allure_results_dir = '/tmp/lambda_protractor/build/test/test/e2e/allure-results/'


def upload_allure_result(s3, bucket, key, allure_result):
    json_string = json.dumps(allure_result, sort_keys=True, indent=4)
    url = 'https://s3.console.aws.amazon.com/s3/object/' + bucket + '/' + key
    print('S3 URL for result: ' + url)
    s3.Object(bucket, key).put(
        Body=str.encode(json_string),
        ContentType='application/json',
        ContentDisposition='inline'
    )


def get_host_labels():
    return [
        {
            'name': 'host',
            'value': 'Lambda'
        },
        {
            'name': 'thread',
            'value': socket.gethostname()
        }
    ]


def create_missing_allure_result(test_name, test_class_name, start_time, stop_time, links, test_timed_out):
    full_name = test_class_name.replace('E2E.', '') + ' ' + test_name
    result = {
        'uuid': str(uuid.uuid4()),
        'fullName': full_name,
        'historyId': full_name,
        'name': test_name,
        'stage': 'finished',
        'status': 'unknown',
        'start': start_time,
        'stop': stop_time,
        'labels': get_host_labels(),
        'links': links,
        'parameters': [],
        'steps': [],
        'attachments': [],
        'statusDetails': {
            'message': 'Disabled, test was not attempted! This is usually intentional behavior due to either : '
                       '\n 1. Hidden by feature flag. It tests a feature that has not been enabled in the host config.'
                       '\n 2. Test case is manually commented out in the source code (if true, please fix).',
            'trace': '#MISSING_TEST_RESULT'
        }
    }

    if test_timed_out:
        result['status'] = 'broken'
        result['statusDetails'] = {
            'message': 'Test timed out! Please see video link to investigate.',
            'trace': '#TIME_LIMIT_REACHED'
        }

    result['labels'].append({
        'name': 'parentSuite',
        'value': test_class_name
    })
    return result


def create_retry_allure_results(test_name, test_class_name, start_time, stop_time, retry_message, attempt_number, links):
    full_name = test_class_name.replace('E2E.', '') + ' ' + test_name
    result = {
        'uuid': str(uuid.uuid4()),
        'fullName': full_name,
        'historyId': full_name,
        'name': test_name,
        'stage': 'finished',
        'status': 'failed',
        'start': start_time,
        'stop': stop_time,
        'labels': get_host_labels(),
        'links': links,
        'parameters': [],
        'steps': [],
        'attachments': [],
        'statusDetails': {
            'message': 'Attempt # ' + attempt_number + ' failed! Retrying...',
            'trace': '#FAILED_WITH_RETRY \n' + retry_message
        }
    }

    result['labels'].append({
        'name': 'parentSuite',
        'value': test_class_name
    })

    return result


def create_link(name, s3_path, mime_type='text/plain'):
    return {
        'name': name,
        'url': 'replace-me' + s3_path,
        'type': mime_type
    }


def allure_results_directory_exists():
    exists = os.path.exists(allure_results_dir)
    if exists:
        print('Allure results dir found')
    else:
        print('Unable to find allure results directory')
    return exists


def allure_results_directory_contains_files():
    contains_files = len(os.listdir(allure_results_dir)) > 0
    if contains_files:
        print('Found results in Allure directory')
    else:
        print('Unable to find results in allure results directory')
    return contains_files


def get_json_results():
    return glob.glob(os.path.join(allure_results_dir, '*-result.json'))
