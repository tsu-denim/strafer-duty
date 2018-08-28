import os
from functions.lib.manifest import JasmineFile


def test_get_matching_tests():
    # get_matching_tests: returns a list of JasminTest Objects for every it('Block') in a passed file

    # Test: pass file to jasmineFile object containing no it blocks. Expect: return empty jasmin_test_list
    no_it_blocks = JasmineFile('Using file name: default_test_class_name', './test_resources/no_it_block.ts', [], [])
    assert len(no_it_blocks.jasmine_tests) == 0

    # Test: pass file containing one it block, Expect: return jasmin_test_list with one JasminTest Object
    one_it_blocks = JasmineFile('default_test_class_name', './test_resources/one_it_block.ts', [], [])
    assert len(one_it_blocks.jasmine_tests) == 1

    # Test: pass file containing more than one it block, Expect: return jasmin_test_list with more than one JasminTest Object
    multi_it_blocks = JasmineFile('default_test_class_name', './test_resources/multi_it_block.ts', [], [])
    assert len(multi_it_blocks.jasmine_tests) > 1


def test_get_test_class_name():
    # Test: check if default test name works, Expect: Object List with one JasminTest Obj, containing defualt test name member
    no_describe_block = JasmineFile('Test: default_test_name', './test_resources/no_describe_block.ts', [], [])
    assert no_describe_block.jasmine_tests[0].test_class_name == 'Test: default_test_name'

    # Test: Check if test_class_name properly assigned, Expect: JasminFile.jasmin_list.JasminTest Obj test_name member to match
    one_describe_block = JasmineFile('Test: default_test_name', './test_resources/one_describe_block.ts', [], [])
    assert one_describe_block.jasmine_tests[0].test_class_name == 'describeBlock1'

    # Test: Check if name properly chosen from multiple choices, Expect: JasminTest Obj test_name member to match first describe block
    multi_describe_block = JasmineFile('Test: default_test_name', './test_resources/multi_describe_block.ts', [], [])
    assert multi_describe_block.jasmine_tests[0].test_class_name == 'describeBlock1'


def test_get_test_name():
    # Test: check that no test name from itblock returns no objects in jasmin_list[], Expect: empty return
    no_it_block = JasmineFile('default_file_name', './test_resources/no_it_block.ts', [], [])
    assert len(no_it_block.jasmine_tests) == 0

    # Test: check that proper test name is parsed from itblock, Expect: proper test name assigned
    one_it_block = JasmineFile('default_file_name', './test_resources/one_it_block.ts', [], [])
    assert 'it_block_1' in one_it_block.jasmine_tests[0].test_name

    # Test: check that multiple it_blocks are turned into JasminTest Objects and properly named
    multi_it_block = JasmineFile('default_file_name', './test_resources/multi_it_block.ts', [], [])
    assert 'it_block_1' in multi_it_block.jasmine_tests[0].test_name
    assert 'it_block_2' in multi_it_block.jasmine_tests[1].test_name


def test_has_tests():
    # Expect True:, test method with one or more jasmine test objects
    multi_it_blocks = JasmineFile('default_file_name', './test_resources/multi_it_block.ts', [], [])
    assert len(multi_it_blocks.jasmine_tests) > 0

    # Expect False:, test method with no jasmine test objects
    no_it_block = JasmineFile('default_file_name', './test_resources/no_it_block.ts', [], [])
    assert len(no_it_block.jasmine_tests) == 0
