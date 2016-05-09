from nose.tools import assert_raises

from benchmark.utils.command_line_util import get_command_line_parser


def test_invalid_mode():
    parser = get_command_line_parser([])
    assert_raises(SystemExit, parser.parse_args, ['invalid'])


def test_mode_check():
    parser = get_command_line_parser([])
    result = parser.parse_args(['check'])
    assert result.subprocess == 'check'


def test_mode_checkout():
    parser = get_command_line_parser([])
    result = parser.parse_args(['checkout'])
    assert result.subprocess == 'checkout'


def test_fails_without_miner():
    parser = get_command_line_parser([])
    assert_raises(SystemExit, parser.parse_args, ['detect'])


def test_detect_with_miner():
    parser = get_command_line_parser(['valid-detector'])
    result = parser.parse_args(['detect', 'valid-detector'])
    assert result.detector == 'valid-detector'


def test_detect_only_empty_list_fails():
    parser = get_command_line_parser(['valid-detector'])
    assert_raises(SystemExit, parser.parse_args, ['detect', 'valid-detector', '--only'])


def test_detect_only():
    parser = get_command_line_parser(['valid-detector'])
    white_list = ['a', 'b', 'c']
    result = parser.parse_args(['detect', 'valid-detector', '--only'] + white_list)
    assert result.white_list == white_list


def test_detect_only_default():
    parser = get_command_line_parser(['valid-detector'])
    result = parser.parse_args(['detect', 'valid-detector'])
    assert result.white_list == [""]


def test_detect_ignore_empty_list_fails():
    parser = get_command_line_parser(['valid-detector'])
    assert_raises(SystemExit, parser.parse_args, ['detect', 'valid-detector', '--ignore'])


def test_detect_ignore():
    parser = get_command_line_parser(['valid-detector'])
    black_list = ['a', 'b', 'c']
    result = parser.parse_args(['detect', 'valid-detector', '--ignore'] + black_list)
    assert result.black_list == black_list


def test_detect_ignore_default():
    parser = get_command_line_parser(['valid-detector'])
    result = parser.parse_args(['detect', 'valid-detector'])
    assert result.black_list == []


def test_detect_timeout():
    parser = get_command_line_parser(['valid-detector'])
    value = '100'
    result = parser.parse_args(['detect', 'valid-detector', '--timeout', value])
    assert result.timeout == int(value)


def test_detect_timeout_default_none():
    parser = get_command_line_parser(['valid-detector'])
    result = parser.parse_args(['detect', 'valid-detector'])
    assert result.timeout is None


def test_detect_timeout_non_int_fails():
    parser = get_command_line_parser(['valid-detector'])
    assert_raises(SystemExit, parser.parse_args, ['detect', 'valid-detector', '--timeout', 'string'])


def test_detect_fails_for_invalid_detector():
    parser = get_command_line_parser(['valid-detector'])
    assert_raises(SystemExit, parser.parse_args, ['detect', 'invalid-detector'])


def test_eval_fails_without_detector():
    parser = get_command_line_parser([])
    assert_raises(SystemExit, parser.parse_args, ['eval'])


def test_eval():
    parser = get_command_line_parser(['valid-detector'])
    result = parser.parse_args(['eval', 'valid-detector'])
    assert result.detector == 'valid-detector'
