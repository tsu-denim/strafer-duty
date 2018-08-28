from functions.lib.manifest import JasmineTest


def test_get_included_tags():
    # Test: when no Tag to search for is passed, return is empty list
    none_get_included_tags = JasmineTest('No tags passed (#include, #exclude) PTID = 0000', 'JasminTest', 'path', [],
                                         [])
    assert '#include' not in none_get_included_tags.get_included_tags()
    assert '#exclude' not in none_get_included_tags.get_included_tags()

    # Test: one passed Tag searched for and found, return in tag array
    one_get_included_tags = JasmineTest('One tag passed (#include, #exclude) PTID = 0000', 'JasminTest', 'path',
                                        ['#include'], [])
    assert '#include' in one_get_included_tags.get_included_tags()
    assert '#exclude' not in one_get_included_tags.get_included_tags()

    # Test: more than one passed Tag searched for and found, return in tag array
    more_get_included_tags = JasmineTest('2 tags passed (#include1, #include2, #exclude) PTID = 0000', 'JasminTest',
                                         'path', ['#include1', '#include2'], [])
    assert '#include1' in more_get_included_tags.get_included_tags()
    assert '#include2' in more_get_included_tags.get_included_tags()
    assert '#exclude' not in more_get_included_tags.get_included_tags()


def test_get_excluded_tags():
    # Test: when no Tag to search for is passed, return is empty list
    none_get_excluded_tags = JasmineTest('No tags passed (#include, #exclude) PTID = 0000', 'JasminTest', 'path', [],
                                         [])
    assert '#include' not in none_get_excluded_tags.get_excluded_tags()
    assert '#exclude' not in none_get_excluded_tags.get_excluded_tags()

    # Test: one passed Tag searched for and found, return in tag array
    one_get_excluded_tags = JasmineTest('One tag passed (#include, #exclude) PTID = 0000', 'JasminTest', 'path', [],
                                        ['#exclude'])
    assert '#exclude' in one_get_excluded_tags.get_excluded_tags()
    assert '#include' not in one_get_excluded_tags.get_excluded_tags()

    # Test: more than one passed Tag searched for and found, return in tag array
    more_get_excluded_tags = JasmineTest('2 tags passed (#include, #exclude1, #exclude2) PTID = 0000', 'JasminTest',
                                         'path', [], ['#exclude1', '#exclude2'], )
    assert '#exclude1' in more_get_excluded_tags.get_excluded_tags()
    assert '#exclude2' in more_get_excluded_tags.get_excluded_tags()
    assert '#include' not in more_get_excluded_tags.get_excluded_tags()


def test_is_included():
    # Test: No tags were passed to filter result, Expect True
    none_is_included = JasmineTest('No tags were passed to filter results (#include, #exclude) PTID = 0000',
                                   'JasminTest', 'path', [], [])

    assert none_is_included.is_included()

    # Test: One include tag passed to filter result, Expect True
    one_is_included = JasmineTest('One include tag passed to filter results (#include, #exclude) PTID = 0000',
                                  'JasminTest', 'path', ['#include'],
                                  [])
    assert one_is_included.is_included()


def test_is_excluded():
    # Test: No tags were passed to filter result, Expect False
    none_is_excluded = JasmineTest('No tags were passed to filter results (#include, #exclude) PTID = 0000',
                                   'JasminTest', 'path', [], [])
    assert not none_is_excluded.is_excluded()

    # Test: One exclude tag passed to filter result, Expect True
    one_is_excluded = JasmineTest('One exclude tag passed to filter results (#include, #exclude) PTID = 0000',
                                  'JasminTest', 'path', [],
                                  ['#exclude'])
    assert one_is_excluded.is_excluded()


def test_is_runnable():
    # Test: if (is_included = true && is_excluded = false), expect TRUE
    include_true_exclude_false = JasmineTest(
        'find one included tag, No exclude tag(#include1, #include2, #exclude1, #exclude2) PTID = 0000', 'JasminTest',
        'path', ['#include1'], [])
    assert include_true_exclude_false.is_runnable()

    # Test: (if is_included = false && is_excluded = false), expect FALSE
    include_false_exclude_false = JasmineTest(
        'include tag not found, exclude tag not found (#include1, #include2, #exclude1, #exclude2) PTID = 0000',
        'JasminTest', 'path', ['#includeNotFound'], ['#excludeNotFound'])
    assert not include_false_exclude_false.is_runnable()

    # Test: (if is_included = true && is_excluded = true), expect FALSE
    include_true_exclude_true = JasmineTest(
        'include tag found, exclude tag found(#include1, #include2, #exclude1, #exclude2) PTID = 0000', 'JasminTest',
        'path', ['#include1'], ['#exclude1'])
    assert not include_true_exclude_true.is_runnable()

    # Test: (Default)(if is_included = false && is_excluded = true), expect FALSE
    include_false_exclude_true = JasmineTest(
        'include tag not found, exclude tag found(#include1, #include2, #exclude1, #exclude2) PTID = 0000',
        'JasminTest', 'path', ['#includeNotFound'], ['#exclude1'])
    assert not include_false_exclude_true.is_runnable()


def test_has_ptid():
    # Test: create JasminTest Object with PTID, assert PTID exists
    with_has_ptid = JasmineTest('test_with_PTID PTID=1111', 'JasminTest', 'path', [], [])
    assert with_has_ptid.has_ptid()

    # create JasminTest Object witout PTID, assert PTID does not exist
    without_has_ptid = JasmineTest('test without ptid', 'JasminTest', 'path', [], [])
    assert not without_has_ptid.has_ptid()

