from nose.tools import assert_raises, assert_equals, nottest

from utils.command_line_util import get_command_line_parser


def test_invalid_mode():
    parser = get_command_line_parser([], [])
    assert_raises(SystemExit, parser.parse_args, ['invalid'])


def test_mode_check():
    parser = get_command_line_parser([], [])
    result = parser.parse_args(['check'])
    assert result.task == 'check'


def test_checkout():
    parser = get_command_line_parser([], [])
    result = parser.parse_args(['checkout'])
    assert result.task == 'checkout'


def test_detect_fails_without_detector():
    parser = get_command_line_parser([], [])
    assert_raises(SystemExit, parser.parse_args, ['detect'])


def test_detect_fails_without_experiment():
    parser = get_command_line_parser(['valid-detector'], [])
    assert_raises(SystemExit, parser.parse_args, ['detect', 'valid-detector'])


def test_detect_valid():
    parser = get_command_line_parser(['valid-detector'], [])
    result = parser.parse_args(['detect', 'valid-detector', '1'])
    assert result.detector == 'valid-detector'


def test_detect_only_empty_list_fails():
    parser = get_command_line_parser(['valid-detector'], [])
    assert_raises(SystemExit, parser.parse_args, ['detect', 'valid-detector', '--only'])


def test_detect_only():
    parser = get_command_line_parser(['valid-detector'], [])
    white_list = ['a', 'b', 'c']
    result = parser.parse_args(['detect', 'valid-detector', '1', '--only'] + white_list)
    assert result.white_list == white_list


def test_detect_only_default():
    parser = get_command_line_parser(['valid-detector'], [])
    result = parser.parse_args(['detect', 'valid-detector', '1'])
    assert result.white_list == []


def test_detect_ignore_empty_list_fails():
    parser = get_command_line_parser(['valid-detector'], [])
    assert_raises(SystemExit, parser.parse_args, ['detect', 'valid-detector', '--skip'])


def test_detect_ignore():
    parser = get_command_line_parser(['valid-detector'], [])
    black_list = ['a', 'b', 'c']
    result = parser.parse_args(['detect', 'valid-detector', '1', '--skip'] + black_list)
    assert result.black_list == black_list


def test_detect_ignore_default():
    parser = get_command_line_parser(['valid-detector'], [])
    result = parser.parse_args(['detect', 'valid-detector', '1'])
    assert result.black_list == []


def test_detect_timeout():
    parser = get_command_line_parser(['valid-detector'], [])
    value = '100'
    result = parser.parse_args(['detect', 'valid-detector', '1', '--timeout', value])
    assert result.timeout == int(value)


def test_detect_experiment_is_int():
    parser = get_command_line_parser(['valid-detector'], [])
    result = parser.parse_args(['detect', 'valid-detector', '1'])
    assert_equals(int, type(result.experiment))


def test_timeout_default_none():
    parser = get_command_line_parser(['valid-detector'], [])
    result = parser.parse_args(['detect', 'valid-detector', '1'])
    assert result.timeout is None


def test_timeout_non_int_fails():
    parser = get_command_line_parser(['valid-detector'], [])
    assert_raises(SystemExit, parser.parse_args, ['detect', 'valid-detector', '1', '--timeout', 'string'])


@nottest
def test_detect_fails_for_invalid_detector():
    parser = get_command_line_parser(['valid-detector'], [])
    assert_raises(SystemExit, parser.parse_args, ['detect', 'invalid-detector'])


def test_java_options():
    parser = get_command_line_parser(['valid-detector'], [])
    result = parser.parse_args(['detect', 'valid-detector', '1', '--java-options', 'Xmx6144M', 'd64'])
    assert_equals(['Xmx6144M', 'd64'], result.java_options)


def test_java_options_default_empty():
    parser = get_command_line_parser(['valid-detector'], [])
    result = parser.parse_args(['detect', 'valid-detector', '1'])
    assert_equals([], result.java_options)


def test_script_is_case_insensitive():
    parser = get_command_line_parser([], ['GENERAL'])
    parser.parse_args(['stats', 'general'])


def test_dataset():
    parser = get_command_line_parser(['Dummy'], [])
    result = parser.parse_args(['detect', 'Dummy', '1', '--dataset', 'crypto'])
    assert_equals('crypto', result.dataset)
