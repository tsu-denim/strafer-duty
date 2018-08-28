import glob
import os
import re


class JasmineTest:

    def __init__(self, test_name, test_class_name, test_path, included_tags: list, excluded_tags: list):
        self.test_name = test_name
        self.test_class_name = test_class_name
        self.test_path = test_path
        self.included_tags = included_tags
        self.excluded_tags = excluded_tags

    def is_runnable(self):
        # Return true if test matches include tags and does not match exclude tags
        should_run = False

        if self.is_included():
            should_run = True

        if self.is_excluded():
            should_run = False

        return should_run

    def has_ptid(self):
        ptid_exists = re.search('PTID\=\d*', self.test_name)  # Check for a ptid

        return ptid_exists

    def is_included(self):
        # Return true if test matches all include tags
        has_match = False

        tags = self.get_included_tags()

        if len(tags) > 0:
            has_match = True

        if len(self.included_tags) == 0:
            has_match = True

        return has_match

    def get_included_tags(self):
        # Return matching include tags

        found_tags = []

        for tag in self.included_tags:
            if tag == '':
                break
            # Tags should always start with a '#', but lib should accept list entries with or without it
            tag_stripped = tag.replace('#', '')  # Strip '#' in case it is there
            tag_fixed = '#' + tag_stripped
            if re.search(tag_fixed, self.test_name):  # Add '#' back to the tag entry and check for it
                found_tags.append(tag_fixed)

        return found_tags

    def is_excluded(self):
        # Return true if test has matching exclude tags
        has_match = False

        tags = self.get_excluded_tags()

        if len(tags) > 0:
            has_match = True

        return has_match

    def get_excluded_tags(self):
        # Return matching exclude tags

        found_tags = []

        for tag in self.excluded_tags:
            # Tags should always start with a '#', but lib should accept list entries with or without it
            tag_stripped = tag.replace('#', '')  # Strip '#' in case it is there
            tag_fixed = '#' + tag_stripped
            if re.search(tag_fixed, self.test_name):  # Add '#' back to the tag entry and check for it
                found_tags.append(tag_fixed)

        return found_tags


class JasmineFile:

    def __init__(self, file_name, file_path, included_tags: list, excluded_tags: list):
        self.file_name = file_name
        self.file_path = file_path
        self.included_tags = included_tags
        self.excluded_tags = excluded_tags
        self.jasmine_tests = self.get_matching_tests()

    def has_tests(self):
        # Return true if it contains tests
        tests_found = False

        if len(self.jasmine_tests) > 0:
            tests_found = True

        return tests_found

    def get_matching_tests(self):
        # Return collection of test objects
        jasmine_test_list = []

        lines = [line.rstrip('\n') for line in open(self.file_path)]

        default_test_class_name = self.file_name.replace('.', '_')
        test_class_name = default_test_class_name

        for line in lines:
            it_blocks = re.findall(r'\bit\(.*\'', line)

            if 'describe(' in line:
                # Set current describe block for matching tests
                test_class_name = re.search('(\')(.*)(\')', line).group(2)
            if len(it_blocks) > 0:
                try:
                    test_name = re.search('(\')(.*)(\')', line).group(2)
                    jasmine_test = JasmineTest(test_name, test_class_name, self.file_path, self.included_tags,
                                               self.excluded_tags)
                    jasmine_test_list.append(jasmine_test)
                except:
                    # If the regex does not match, ignore that line
                    pass

        return jasmine_test_list


class JasmineManifest:

    def __init__(self, test_globs: list, included_tags: list, excluded_tags: list):
        # Setup constructor
        self.test_globs = test_globs
        self.included_tags = included_tags
        self.excluded_tags = excluded_tags
        self.jasmine_tests = self.get_all_tests()

    def get_all_tests(self):

        # For each test glob, find and return the list of matching files
        test_files = []
        for file_glob in self.test_globs:
            print("Checking for matches with the following glob path: " + file_glob)
            matching_files = glob.glob(file_glob)
            amount_found = str(len(matching_files))
            print("Count of matching files found: " + amount_found)
            test_files = test_files + matching_files

        # Make a collection of JasmineFile objects and call their get_matching_tests method
        jasmine_file_list = self.get_jasmine_file_list(test_files)

        # Append matching tests to a collection
        jasmine_test_list = []
        for jasmine_file in jasmine_file_list:
            for each_test in jasmine_file.jasmine_tests:
                jasmine_test_list.append(each_test)

        # Return collection of JasmineTest objects
        return jasmine_test_list

    def get_jasmine_file_list(self, file_paths: list):
        jasmine_file_list = []
        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            jasmine_file = JasmineFile(file_name, file_path, self.included_tags, self.excluded_tags)
            jasmine_file_list.append(jasmine_file)

        return jasmine_file_list

    def is_runnable(self, test_name):
        runnable = False
        for each_test in self.get_all_runnable_tests():
            tn = each_test.test_name.replace('\\', "").replace("'", "").replace('"', '')
            tn1 = test_name.replace('\\', "").replace("'", "").replace('"', '')
            if tn == tn1:
                if each_test.is_runnable():
                    runnable = True
                    break
        return runnable

    def get_total_number_tests(self):
        total = len(self.jasmine_tests)
        return total

    def get_all_runnable_tests(self):
        # Return list of runnable tests
        runnable_list = []
        for each_test in self.jasmine_tests:
            if each_test.is_runnable():
                runnable_list.append(each_test)

        return runnable_list

    def get_total_number_runnable(self):
        # Return total number of tests that should be ran
        total = len(self.get_all_runnable_tests())
        return total

    def get_all_non_runnable_tests(self):
        # return list of non runnable tests
        non_runnable_list = []
        for each_test in self.jasmine_tests:
            if not each_test.is_runnable():
                non_runnable_list.append(each_test)

        return non_runnable_list

    def get_total_number_not_runnable(self):
        # Return total number of tests that should not be ran
        total = len(self.get_all_non_runnable_tests())
        return total
