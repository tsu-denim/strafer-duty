import getopt
import glob
import json
import sys

from functions.lib.manifest import JasmineManifest
from functions.lib.junit_formatter import RetryCombine, AllureTweaker, JunitMerger, strip_escape, write_native_allure_results



def main():
    allure_results_glob = ''
    junit_results_glob = ''
    retry_glob = ''
    output_report_name = ''
    report_type = 'runnable'
    include_tags = []
    exclude_tags = []
    # Set default test spec paths, override with --testSpecGlobs option
    test_spec_globs = [
        'build/test/test/e2e/uia/spec/**/**/*_test.js',
        'build/test/test/e2e/uia/spec/**/*_test.js',
        'build/test/test/e2e/setup/spec/*_test.js'
    ]

    # Parse any possible configuration options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "",
                                   ["allureGlob=", "junitGlob=", "retryGlob=", "outputReportName=",
                                    "reportType=", "includeTags=", "excludeTags=", "testSpecGlobs="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        sys.exit(2)

    allure_results_glob_found = False
    junit_glob_found = False
    retry_glob_found = False
    output_report_name_found = False

    for o, a in opts:
        if o == "--allureGlob":
            allure_results_glob = a
            allure_results_glob_found = True
        elif o == "--junitGlob":
            junit_results_glob = a
            junit_glob_found = True
        elif o == "--retryGlob":
            retry_glob = a
            retry_glob_found = True
        elif o == "--outputReportName":
            output_report_name = a
            output_report_name_found = True
        elif o == "--reportType":
            report_type = a
        elif o == "--excludeTags":
            if a == "":
                exclude_tags = []
            else:
                exclude_tags = "".join(a).split(",")
        elif o == "--includeTags":
            if a == "":
                include_tags = []
            else:
                include_tags = "".join(a).split(",")
        elif o == "--testSpecGlobs":
            test_spec_globs = "".join(a).split(",")
        else:
            assert False, "unhandled option"

    jasmine_manifest = JasmineManifest(test_spec_globs, include_tags,
                                       exclude_tags)
    print("Total tests: " + str(jasmine_manifest.get_total_number_tests()))

    # Create runnable report
    if junit_glob_found and output_report_name_found and not retry_glob_found and report_type == 'runnable':
        output_file = output_report_name
        output_file_missing = output_report_name.replace('.xml', '-missing.xml')
        runnable = JunitMerger(junit_results_glob, output_file, jasmine_manifest)
        print("Total runnable tests: " + str(runnable.non_runnable_manifest.get_total_number_runnable()))
        print("Creating runnable tests report...")
        runnable.create_runnable_report()
        print("Creating disabled runnable tests report...")
        missing = JunitMerger(junit_results_glob, output_file_missing, jasmine_manifest)
        missing.create_missing_report()
        runnable.remove_old_files()

    # Create non_runnable report
    elif output_report_name_found and not retry_glob_found and report_type == 'non_runnable':
        output_file = output_report_name
        non_runnable = JunitMerger('', output_file, jasmine_manifest)
        print("Total non_runnable tests: " + str(
            non_runnable.non_runnable_manifest.get_total_number_not_runnable()))
        print("Creating non_runnable tests report...")
        non_runnable.create_non_runnable_report()

    # Tweak allure reports if --allureGlob and --junitGlob options are passed in
    elif junit_glob_found and allure_results_glob:
        allure_report = AllureTweaker(junit_results_glob, allure_results_glob)
        allure_report.update_results()

    # Process test retries if --retryGlob is passed in
    elif retry_glob_found and junit_glob_found and output_report_name_found:
        print("Processing test retries and merging reports")
        output_file = output_report_name
        retry_helper = RetryCombine(retry_glob)
        merger = JunitMerger(junit_results_glob, output_file, jasmine_manifest)
        merger.create_report(retry_helper)
        merger.remove_old_files()

    # Write skipped test with native allure formatting
    elif report_type == 'non_runnable_allure' and output_report_name_found:
        print('Writing Allure skipped results to: ' + output_report_name)
        manifest = JasmineManifest(test_spec_globs, [], [])
        test_list = {}

        for test in manifest.get_all_tests():
            test_class_name = strip_escape(test.test_class_name)
            test_name = strip_escape(test.test_name)
            full_name = test_class_name + ' ' + test_name

            test_list[full_name] = {
                'class': test_class_name,
                'name': test_name,
                'found': False
            }

        for file_glob in glob.glob(output_report_name + '/*-result.json'):
            test_result = json.loads(open(file_glob).read())
            test_list[strip_escape(test_result['historyId'])]['found'] = True

        write_native_allure_results(test_list)

    else:
        # Raise error if required allure report arguments are missing
        if output_report_name_found is not True:
            raise ValueError(
                'Argument for Junit Report Missing! Run command with --outputReportName my_report.xml !')
        if allure_results_glob_found is not True:
            raise ValueError(
                'Argument for Allure Glob Missing! Run command with --allureGlob or -g! I.e. -g folder/myglob*.json')

if __name__ == "__main__":
    main()