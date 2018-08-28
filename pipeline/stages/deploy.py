import os
import subprocess
import boto3

from functions.lib.test_utilities import get_branch_name

# The calls to AWS STS AssumeRole must be signed with the access key ID
# and secret access key of an existing IAM user or by using existing temporary
# credentials such as those from another role. (You cannot call AssumeRole
# with the access key for the root account.) The credentials can be in
# environment variables or in a configuration file and will be discovered
# automatically by the boto3.client() function. For more information, see the
# Python SDK documentation:
# http://boto3.readthedocs.io/en/latest/reference/services/sts.html#client

# create an STS client object that represents a live connection to the
# STS service
sts_client = boto3.client('sts')

# Call the assume_role method of the STSConnection object and pass the role
# ARN and a role session name.
role_to_assume = os.environ['PIPELINE_ROLE']
branch_name_stripped = "straferduty-manual"
# branch_name_stripped = get_branch_name()
chrome_version = os.environ['CHROME_VERSION']

credential_object = sts_client.assume_role(
    RoleArn=role_to_assume,
    RoleSessionName="AssumeRoleSession1"
)

# Create temporary shell environment with AWS creds from STS
new_env = os.environ.copy()
new_env['AWS_ACCESS_KEY_ID'] = credential_object['Credentials']['AccessKeyId']
new_env['AWS_SECRET_ACCESS_KEY'] = credential_object['Credentials']['SecretAccessKey']
new_env['AWS_SESSION_TOKEN'] = credential_object['Credentials']['SessionToken']
new_env['AWS_DEFAULT_REGION'] = 'us-east-1'

# Package the runTest function
package_command = 'aws cloudformation package --template template.yml --s3-bucket ' \
                  'strafer-duty-build-pipeline --output-template ' \
                  'template-export.yml'

call_package_command = subprocess.Popen(package_command
                                        , stderr=subprocess.STDOUT
                                        , shell=True
                                        , preexec_fn=os.setsid
                                        , env=new_env)

call_package_command.wait()

print("### Deploying CloudFormation Stack: " + branch_name_stripped)

# Format aws cli cloudformation deploy command to use branch name for the stack name
deploy_command = 'aws cloudformation deploy --stack-name {} --template template-export.yml ' \
                 '--tags StraferDutyBranchName={} ' \
                 '--capabilities CAPABILITY_IAM ' \
                 '--parameter-overrides ' \
                 'ChromeVersion={}'

deploy_command_formatted = deploy_command.format(branch_name_stripped,
                                                 branch_name_stripped,
                                                 chrome_version)

print(deploy_command_formatted)

# Execute cloudformation deploy command and wait for it to finish
call_aws_command = subprocess.Popen(deploy_command_formatted
                                    , stderr=subprocess.STDOUT
                                    , shell=True
                                    , preexec_fn=os.setsid
                                    , env=new_env)
call_aws_command.wait()

# Call list_stack_resources using STS, check deploy status then save sdb domain and sns topic arns
cloud_formation_client = boto3.client('cloudformation', region_name='us-east-1',
                                      aws_access_key_id=credential_object['Credentials']['AccessKeyId'],
                                      aws_secret_access_key=credential_object['Credentials']['SecretAccessKey'],
                                      aws_session_token=credential_object['Credentials']['SessionToken'], )

# Check if the stack was deployed successfully
print("### Checking state of CloudFormation stack " + branch_name_stripped + " deployment...")
is_deploy_successful = False
stack_status_summary = cloud_formation_client.describe_stacks(StackName=branch_name_stripped)
stack_name = stack_status_summary["Stacks"][0]["StackName"]
stack_status = stack_status_summary["Stacks"][0]["StackStatus"]

# Compare current state to the acceptable values
if stack_name == branch_name_stripped and stack_status in ("CREATE_COMPLETE", "UPDATE_COMPLETE"):
    is_deploy_successful = True

# Raise an error if deployment is in a bad state, which fails the build in Jenkins
if is_deploy_successful is False:
    raise ValueError("...ERROR! CloudFormation stack " + branch_name_stripped +
                     " had a problem with deployment! Investigate in the CloudFormation console!")
else:
    print("...SUCCESS! CloudFormation stack " + branch_name_stripped + " was deployed properly.")
