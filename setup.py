from setuptools import setup, find_packages
import subprocess
import os


def get_branch_name():
    # Grab the branch name from git
    git_command = 'git describe --contains --all HEAD'

    call_git_command = subprocess.check_output(git_command
                                               , stderr=subprocess.STDOUT
                                               , shell=True
                                               , preexec_fn=os.setsid)

    # Format branch name so it can be used as a CloudFormation stack name
    branch_name_stripped = call_git_command.decode('utf-8').replace('remotes/origin/', '').replace('/', '').rstrip(
        "\n\r").lstrip("\n\r").replace('-', '')

    return branch_name_stripped


setup(
    name='straferduty-manual',
    version=1,
    package_dir={'':'functions'},
    packages=find_packages(),
    package_data={
        '': [
            '*.py',
            '*.gz',
            '*.xsl'
        ]
    },
    install_requires=[
        'boto3',
        'requests'
    ],
    entry_points={
        'console_scripts': ['artifact-slurper=functions.lib.shell_transform_test_artifacts:main',
                            'strafer-duty=functions.lib.shell_task_runner:main']
    }
)
