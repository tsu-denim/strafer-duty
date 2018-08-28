import getopt
import os
import sys
import datetime

from functions.lib.test_utilities import get_branch_name, get_sts_credentials, get_step_function_name, \
    get_config_dict_from_json, upload_tarball_to_s3, create_expired_test, execute_test_runner, monitor_state_machine, \
    get_stack_name_from_branch, get_simple_db_domain, put_manifest_sdb, get_bucket_name, get_artifacts


def main():
    # Parse any possible configuration options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "",
                                   ['roleToAssume=',
                                    'jsonConfigPath=',
                                    'tarPath=',
                                    'outputReportName=',
                                    'releaseBranchName=',
                                    'mockExpiredTest',
                                    'ciMode',
                                    'excludeTags=',
                                    'includeTags=',
                                    'targetUrl=',
                                    'testBranchJobIdentifier=',
                                    'timestampForTestMetrics='])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        sys.exit(2)

    role_to_assume = ''
    json_config_path = ''
    tar_path = ''
    output_report_name = ''
    release_branch_name = ''
    include_tags = []
    exclude_tags = []
    target_url = ''
    test_branch_job_identifier = ''
    timestamp_for_test_metrics = ''

    role_to_assume_found = False
    json_config_path_found = False
    tar_path_found = False
    output_report_name_found = False
    release_branch_name_found = False
    mock_expired_test_found = False
    ci_mode_found = False
    include_tags_found = False
    exclude_tags_found = False
    target_url_found = False
    test_branch_job_identifier_found = False
    timestamp_for_test_metrics_found = False

    for o, a in opts:
        if o == "--roleToAssume":
            role_to_assume = a
            print("Found option: " + o + " with value: " + a)
            role_to_assume_found = True
        elif o == "--jsonConfigPath":
            json_config_path = a
            print("Found option: " + o + " with value: " + a)
            json_config_path_found = True
        elif o == "--tarPath":
            tar_path = a
            print("Found option: " + o + " with value: " + a)
            tar_path_found = True
        elif o == "--outputReportName":
            output_report_name = a
            print("Found option: " + o + " with value: " + a)
            output_report_name_found = True
        elif o == "--releaseBranchName":
            release_branch_name = a
            print("Found option: " + o + " with value: " + a)
            release_branch_name_found = True
        elif o == "--mockExpiredTest":
            print("Found option: " + o)
            mock_expired_test_found = True
        elif o == "--ciMode":
            print("Found option: " + o)
            ci_mode_found = True
        elif o == "--excludeTags":
            print("Found option: " + o + " with value: " + a)
            if a == "":
                exclude_tags = []
            else:
                exclude_tags = "".join(a).split(",")
            exclude_tags_found = True
        elif o == "--includeTags":
            print("Found option: " + o + " with value: " + a)
            if a == "":
                include_tags = []
            else:
                include_tags = "".join(a).split(",")
            include_tags_found = True
        elif o == "--targetUrl":
            print("Found option: " + o + " with value: " + a)
            target_url = a
            target_url_found = True
        elif o == "--testBranchJobIdentifier":
            print("Found option: " + o + " with value: " + a)
            test_branch_job_identifier = a
            test_branch_job_identifier_found = True
        elif o == "--timestampForTestMetrics":
            print("Found option: " + o + " with value: " + a)
            timestamp_for_test_metrics = a
            timestamp_for_test_metrics_found = True
        else:
            assert False, "unhandled option"

    # Run against custom release branch
    if role_to_assume_found \
            and json_config_path_found \
            and tar_path_found \
            and output_report_name_found \
            and release_branch_name_found \
            and exclude_tags_found \
            and include_tags_found \
            and target_url_found \
            and test_branch_job_identifier_found \
            and timestamp_for_test_metrics_found:
        print("Running UIA tests in AWS Lambda...")

        tar_abs_path = os.path.abspath(tar_path)

        stack_name = get_stack_name_from_branch(release_branch_name)

        sts_creds = get_sts_credentials(role_to_assume)

        sdb_domain = get_simple_db_domain(stack_name, sts_creds)

        bucket_name = get_bucket_name(stack_name, sts_creds)

        test_runner_arn = get_step_function_name(stack_name, sts_creds)

        config_dict = get_config_dict_from_json(json_config_path, tar_abs_path)

        # Override config defaults
        config_dict['excludeTags'] = exclude_tags
        config_dict['includeTags'] = include_tags
        config_dict['serverUrl'] = target_url
        config_dict['testBranchJobIdentifier'] = test_branch_job_identifier
        config_dict['timestampForTestMetrics'] = timestamp_for_test_metrics

        upload_tarball_to_s3(config_dict, sts_creds, bucket_name)

        put_manifest_sdb(sts_creds, sdb_domain, config_dict)

        execution_id = execute_test_runner(config_dict, sts_creds, test_runner_arn)

        monitor_state_machine(sts_creds, execution_id)

        get_artifacts(bucket_name, sts_creds, output_report_name, config_dict)

        # Run against branch of execution and spoof an expired test, used for testing in strafer-duty build pipeline
    elif role_to_assume_found \
            and json_config_path_found \
            and tar_path_found \
            and output_report_name_found \
            and mock_expired_test_found \
            and ci_mode_found:
        print("CI Mode: Running UIA tests in AWS Lambda with a mocked expired test!")

        tar_abs_path = os.path.abspath(tar_path)

        stack_name = get_branch_name()

        sts_creds = get_sts_credentials(role_to_assume)

        test_runner_arn = get_step_function_name(stack_name, sts_creds)

        sdb_domain = get_simple_db_domain(stack_name, sts_creds)

        bucket_name = get_bucket_name(stack_name, sts_creds)

        config_dict = get_config_dict_from_json(json_config_path, tar_abs_path)

        # Override config defaults
        config_dict['excludeTags'] = exclude_tags
        config_dict['includeTags'] = include_tags

        upload_tarball_to_s3(config_dict, sts_creds, bucket_name)

        now = datetime.datetime.now()
        create_expired_test(sts_creds, config_dict['executionName'], now, stack_name, bucket_name)

        put_manifest_sdb(sts_creds, sdb_domain, config_dict)

        execution_id = execute_test_runner(config_dict, sts_creds, test_runner_arn)

        monitor_state_machine(sts_creds, execution_id)

        get_artifacts(bucket_name, sts_creds, output_report_name, config_dict)

    # Run against branch of execution, used for testing in strafer-duty build pipeline
    elif role_to_assume_found \
            and json_config_path_found \
            and tar_path_found \
            and output_report_name_found \
            and ci_mode_found:
        print("CI Mode: Running UIA tests in AWS Lambda")

        tar_abs_path = os.path.abspath(tar_path)

        stack_name = get_branch_name()

        sts_creds = get_sts_credentials(role_to_assume)

        test_runner_arn = get_step_function_name(stack_name, sts_creds)

        sdb_domain = get_simple_db_domain(stack_name, sts_creds)

        bucket_name = get_bucket_name(stack_name, sts_creds)

        config_dict = get_config_dict_from_json(json_config_path, tar_abs_path)

        # Override config defaults
        config_dict['excludeTags'] = exclude_tags
        config_dict['includeTags'] = include_tags

        upload_tarball_to_s3(config_dict, sts_creds, bucket_name)

        put_manifest_sdb(sts_creds, sdb_domain, config_dict)

        execution_id = execute_test_runner(config_dict, sts_creds, test_runner_arn)

        monitor_state_machine(sts_creds, execution_id)

        get_artifacts(bucket_name, sts_creds, output_report_name, config_dict)

    # Raise error if required arguments are missing
    else:
        if role_to_assume_found is not True:
            raise ValueError(
                'Argument for AWS role missing! Run command with --roleToAssume arn:aws:iam::############:role/myRole')
        if json_config_path_found is not True:
            raise ValueError(
                'Argument for Json Config Path Missing! Run command with --jsonConfigPath my_config.json !')
        if tar_path_found is not True:
            raise ValueError(
                'Argument for Gzipped Tar Path Missing! Run command with --tarPath myProtractorSyncTar.tar.gz !')
        if output_report_name is not True:
            raise ValueError(
                'Argument for Output Report Name Missing! Run command with --outputReportName my_report.xml !')
        if ci_mode_found is not True and target_url_found is not True:
            raise ValueError('Missing target url. Run command with --targetUrl some.url.bbpd.io')
        if ci_mode_found is not True or release_branch_name_found is not True:
            raise ValueError(
                'Release target flag missing! Run command with --ciMode to target git branch this tool is executing '
                'from or specify a target with --releaseBranchName= release/x-x!')
        if ci_mode_found is not True and timestamp_for_test_metrics_found is not True:
            raise ValueError('Missing --timeStampForTestMetrics option! ')
        if ci_mode_found is not True and test_branch_job_identifier_found is not True:
            raise ValueError('Missing --testBranchJobIdentifier option! ')


if __name__ == "__main__":
    main()
