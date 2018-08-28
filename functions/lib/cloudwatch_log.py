import os
import uuid

url = 'https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logEventViewer:group=/aws/lambda/%s;filter="%s"'


class CloudWatchLogs:

    def __init__(self):
        self.log_marker = 'Test Start Locator: ' + str(uuid.uuid4())

    def print_marker(self):
        print(self.log_marker)

    def get_allure_link(self):
        return {
            'name': 'Lambda Cloudwatch Logs',
            'url': url % (os.environ['AWS_LAMBDA_FUNCTION_NAME'], self.log_marker),
            'type': 'text/html'
        }
