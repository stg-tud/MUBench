import sys

from nose.tools import assert_raises, assert_equals, nottest

from data.detector import Detector
from utils.config_util import _get_command_line_parser


def setup_module():
    sys.stderr = sys.stdout


def teardown_module():
    sys.stderr = sys.__stderr__


def test_invalid_mode():
    parser = _get_command_line_parser([], [], [])
    assert_raises(SystemExit, parser.parse_args, ['invalid'])


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
    result = parser.parse_args(['run', 'ex1', 'Dummy', '--datasets', 'valid-dataset'])
    assert_equals(['valid-dataset'], result.datasets)


def test_multiple_datasets():
    parser = _get_command_line_parser(['Dummy'], [], ['valid-dataset', 'other-valid-dataset'])
    result = parser.parse_args(['run', 'ex1', 'Dummy', '--datasets', 'valid-dataset', 'other-valid-dataset'])
    assert_equals(['valid-dataset', 'other-valid-dataset'], result.datasets)


def test_fails_for_invalid_dataset():
    parser = _get_command_line_parser(['valid-detector'], [], ['valid-dataset'])
    assert_raises(SystemExit, parser.parse_args, ['run', 'ex1', 'valid-detector', '--datasets', 'invalid-dataset'])


def test_release():
    parser = _get_command_line_parser(['valid-detector'], [], [])
    result = parser.parse_args(['run', 'ex1', 'valid-detector', '--tag', 'FSE17'])
    assert_equals('fse17', result.requested_release)


def test_release_default():
    parser = _get_command_line_parser(['valid-detector'], [], [])
    result = parser.parse_args(['run', 'ex1', 'valid-detector'])
    assert_equals(Detector.DEFAULT_RELEASE, result.requested_release)


def test_dataset_check():
    parser = _get_command_line_parser([], [], [])
    result = parser.parse_args(['check', 'dataset'])
    assert_equals('check', result.task)
    assert_equals('dataset', result.sub_task)


def test_setup_check():
    parser = _get_command_line_parser([], [], [])
    result = parser.parse_args(['check', 'setup'])
    assert_equals('check', result.task)
    assert_equals('setup', result.sub_task)


def test_fails_without_run_subtask():
    parser = _get_command_line_parser([], [], [])
    assert_raises(SystemExit, parser.parse_args, ['run'])


def test_fails_without_publish_subtask():
    parser = _get_command_line_parser([], [], [])
    assert_raises(SystemExit, parser.parse_args, ['publish'])


def test_allow_zero_limit():
    parser = _get_command_line_parser(['DemoDetector'], [], [])
    assert_equals(0, parser.parse_args(['publish', 'ex2', 'DemoDetector', '-s', 'site', '-u', 'user', '--limit', '0']).limit)


def test_fails_on_negative_limit():
    parser = _get_command_line_parser(['DemoDetector'], [], [])
    assert_raises(SystemExit, parser.parse_args, ['publish', 'ex2', 'DemoDetector', '-s', 'site', '--limit', '-1'])


def test_requires_review_site_username():
    parser = _get_command_line_parser(['DemoDetector'], [], [])
    assert_raises(SystemExit, parser.parse_args, ['publish', 'ex2', 'DemoDetector', '-s'])
