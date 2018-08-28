from functions.lib.manifest import JasmineManifest


def test_get_all_tests():
    # Test: pass 'glob' filePatterns to directory with 1 matching file and 5 tests; Expect: jasmine_test_list to contain 5 items
    five_jasmine_tests = JasmineManifest(['./test_resources/five_tests.ts'], [], [])
    assert len(five_jasmine_tests.jasmine_tests) == 5

    # Test: pass 'glob' filePatterns to directory containing no files with matching pattern'; Expect: empty jasmine_test_list
    does_not_contain_jasmine_tests = JasmineManifest(['./test_resources/*.py'], [], [])
    assert len(does_not_contain_jasmine_tests.jasmine_tests) == 0


def test_get_jasmine_file_list():
    # Test: Pass No files to method; Expect: Empty list of tests (no objects)
    no_jasmine_files = JasmineManifest(['./test_resources/*.py'], [], [])
    assert len(no_jasmine_files.jasmine_tests) == 0

    # Test: Pass more than 0 files to method; Expect: more than 0 Jasmin File Object
    test_resources_directory = JasmineManifest(['./test_resources/*.ts'], [], [])
    assert len(test_resources_directory.jasmine_tests) > 0


def test_is_runnable():
    # Test: pass no test name; expect False
    no_test = JasmineManifest([], [], [])
    assert not no_test.is_runnable('')

    # Test: pass filepath with runnable tests; Expect True
    runnable = JasmineManifest(['./test_resources/is_runnable_test.ts'], [], [])
    assert runnable.is_runnable('is_runnable')


def test_get_total_number_of_tests():
    # Test: Pass file with no tests; Expect return 0
    no_tests = JasmineManifest([], [], [])
    assert no_tests.get_total_number_tests() == 0

    # Test: Pass file path to recourses directory; Expected return more than 0
    more_tests = JasmineManifest(['./test_resources/*.ts'], [], [])
    assert more_tests.get_total_number_tests() > 0


def test_get_all_runnable_tests():
    # Test: Pass file with no tests; Expect return 0
    no_tests = JasmineManifest([], [], [])
    assert len(no_tests.get_all_runnable_tests()) == 0

    # Test: Pass file path to recourses directory; Expected return more than 0
    more_tests = JasmineManifest(['./test_resources/*.ts'], [], [])
    assert len(more_tests.get_all_runnable_tests()) > 0


def test_get_total_number_runnable():
    # Test: Pass file with No runnable tests; Expect return 0
    no_runnable = JasmineManifest([], [], [])
    assert no_runnable.get_total_number_runnable() == 0

    # Test: Pass file with runnable tests; Expect return > 0
    has_runnable = JasmineManifest(['./test_resources/*.ts'], [], [])
    assert has_runnable.get_total_number_runnable() > 0


def test_get_all_non_runnable_tests():
    # Test: Pass file with five non_runnable Tests: Expect return 5
    five_runnable = JasmineManifest(['./test_resources/five_tests.ts'], ['#include'], [])
    assert len(five_runnable.get_all_non_runnable_tests()) == 5

    # Test: Pass file with all runnable tests; Expect 0 return
    all_runnable = JasmineManifest(['./test_resources/five_tests.ts'], [], [])
    assert len(all_runnable.get_all_non_runnable_tests()) == 0


def test_get_total_number_not_runnable():
    # Test: pass file pattern with all runnable tests; Expect return 0
    all_runnable = JasmineManifest(['./test_resources/five_tests.ts'], [], [])
    assert all_runnable.get_total_number_not_runnable() == 0

    # Test: pass file pattern with 5 non-runnable tests; Expect: return 5
    five_non_runnable = JasmineManifest(['./test_resources/five_tests.ts'], ['#include'], [])
    assert five_non_runnable.get_total_number_not_runnable() == 5
