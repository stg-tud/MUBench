import sys
from nose.tools import assert_raises, assert_equals, nottest

from utils.config_util import _get_command_line_parser


def setup_module():
    sys.stderr = sys.stdout


def teardown_module():
    sys.stderr = sys.__stderr__


def test_invalid_mode():
    parser = _get_command_line_parser([], [], [])
    assert_raises(SystemExit, parser.parse_args, ['invalid'])


def test_mode_check():
    parser = _get_command_line_parser([], [], [])
    result = parser.parse_args(['check'])
    assert result.task == 'check'


def test_checkout():
    parser = _get_command_line_parser([], [], [])
    result = parser.parse_args(['checkout'])
    assert result.task == 'checkout'


def test_run_fails_without_detector():
    parser = _get_command_line_parser([], [], [])
    assert_raises(SystemExit, parser.parse_args, ['run', 'ex1'])


def test_run_fails_without_experiment():
    parser = _get_command_line_parser(['valid-detector'], [], [])
    assert_raises(SystemExit, parser.parse_args, ['run', 'valid-detector'])


def test_run_valid():
    parser = _get_command_line_parser(['valid-detector'], [], [])
    result = parser.parse_args(['run', 'ex1', 'valid-detector'])
    assert result.detector == 'valid-detector'


def test_detect_only_empty_list_fails():
    parser = _get_command_line_parser(['valid-detector'], [], [])
    assert_raises(SystemExit, parser.parse_args, ['run', 'ex1', 'valid-detector', '--only'])


def test_detect_only():
    parser = _get_command_line_parser(['valid-detector'], [], [])
    white_list = ['a', 'b', 'c']
    result = parser.parse_args(['run', 'ex1', 'valid-detector', '--only'] + white_list)
    assert result.white_list == white_list


def test_run_only_default():
    parser = _get_command_line_parser(['valid-detector'], [], [])
    result = parser.parse_args(['run', 'ex1', 'valid-detector'])
    assert result.white_list == []


def test_run_ignore_empty_list_fails():
    parser = _get_command_line_parser(['valid-detector'], [], [])
    assert_raises(SystemExit, parser.parse_args, ['run', 'ex1', 'valid-detector', '--skip'])


def test_run_ignore():
    parser = _get_command_line_parser(['valid-detector'], [], [])
    black_list = ['a', 'b', 'c']
    result = parser.parse_args(['run', 'ex1', 'valid-detector', '--skip'] + black_list)
    assert result.black_list == black_list


def test_run_ignore_default():
    parser = _get_command_line_parser(['valid-detector'], [], [])
    result = parser.parse_args(['run', 'ex1', 'valid-detector'])
    assert result.black_list == []


def test_run_timeout():
    parser = _get_command_line_parser(['valid-detector'], [], [])
    value = '100'
    result = parser.parse_args(['run', 'ex1', 'valid-detector', '--timeout', value])
    assert result.timeout == int(value)


def test_timeout_default_none():
    parser = _get_command_line_parser(['valid-detector'], [], [])
    result = parser.parse_args(['run', 'ex1', 'valid-detector'])
    assert result.timeout is None


def test_timeout_non_int_fails():
    parser = _get_command_line_parser(['valid-detector'], [], [])
    assert_raises(SystemExit, parser.parse_args, ['run', 'ex1', 'valid-detector', '--timeout', 'string'])


@nottest
def test_run_fails_for_invalid_detector():
    parser = _get_command_line_parser(['valid-detector'], [], [])
    assert_raises(SystemExit, parser.parse_args, ['run', 'ex1', 'invalid-detector'])


def test_java_options():
    parser = _get_command_line_parser(['valid-detector'], [], [])
    result = parser.parse_args(['run', 'ex1', 'valid-detector', '--java-options', 'Xmx6144M', 'd64'])
    assert_equals(['Xmx6144M', 'd64'], result.java_options)


def test_java_options_default_empty():
    parser = _get_command_line_parser(['valid-detector'], [], [])
    result = parser.parse_args(['run', 'ex1', 'valid-detector'])
    assert_equals([], result.java_options)


def test_script_is_case_insensitive():
    parser = _get_command_line_parser([], ['GENERAL'], [])
    parser.parse_args(['stats', 'general'])


def test_dataset():
    parser = _get_command_line_parser(['Dummy'], [], ['valid-dataset'])
    result = parser.parse_args(['run', 'ex1', 'Dummy', '--dataset', 'valid-dataset'])
    assert_equals('valid-dataset', result.dataset)


def test_fails_for_invalid_dataset():
    parser = _get_command_line_parser(['valid-detector'], [], ['valid-dataset'])
    assert_raises(SystemExit, parser.parse_args, ['run', 'ex1', 'valid-detector', '--dataset', 'invalid-dataset'])


def test_release():
    parser = _get_command_line_parser(['valid-detector'], [], [])
    result = parser.parse_args(['run', 'ex1', 'valid-detector', '--tag', 'FSE17'])
    assert_equals('FSE17', result.requested_release)


def test_release_default():
    parser = _get_command_line_parser(['valid-detector'], [], [])
    result = parser.parse_args(['run', 'ex1', 'valid-detector'])
    assert_equals(None, result.requested_release)


def test_dataset_check():
    parser = _get_command_line_parser([], [], [])
    result = parser.parse_args(['dataset-check'])
    assert_equals('dataset-check', result.task)
