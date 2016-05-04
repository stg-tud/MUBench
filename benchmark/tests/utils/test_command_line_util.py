import unittest

from utils import command_line_util

class InvalidModeTest(unittest.TestCase):
    def setUp(self):
        self.parser = command_line_util.get_command_line_parser([])

    def test_stops_on_invalid_mode(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['invalid'])


class CheckModeTest(unittest.TestCase):
    def setUp(self):
        self.parser = command_line_util.get_command_line_parser([])

    def test_mode_check(self):
        result = self.parser.parse_args(['check'])
        self.assertEqual('check', result.mode)


class CheckoutModeTest(unittest.TestCase):
    def setUp(self):
        self.parser = command_line_util.get_command_line_parser([])

    def test_mode_checkout(self):
        result = self.parser.parse_args(['checkout'])
        self.assertEqual('checkout', result.mode)


class MineModeTest(unittest.TestCase):
    def setUp(self):
        self.parser = command_line_util.get_command_line_parser([])

    def test_fails_without_miner(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['mine'])

    def test_with_miner(self):
        test_miner = 'dummy-miner'
        result = self.parser.parse_args(['mine', test_miner])
        self.assertEqual(test_miner, result.miner)


class EvalModeTest(unittest.TestCase):
    def setUp(self):
        self.detector = 'dummy-detector'
        self.parser = command_line_util.get_command_line_parser([self.detector])

    def test_fails_without_detector(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['eval'])

    def test_with_detector(self):
        test_detector = 'dummy-detector'
        result = self.parser.parse_args(['eval', test_detector])
        self.assertEqual(test_detector, result.detector)

    def test_only_empty_list_fails(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['eval', self.detector, '--only'])

    def test_only(self):
        white_list = ['a', 'b', 'c']
        result = self.parser.parse_args(['eval', self.detector, '--only'] + white_list)
        self.assertEqual(white_list, result.white_list)

    def test_only_default(self):
        result = self.parser.parse_args(['eval', self.detector])
        self.assertEqual([""], result.white_list)

    def test_ignore_empty_list_fails(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['eval', self.detector, '--ignore'])

    def test_ignore(self):
        black_list = ['a', 'b', 'c']
        result = self.parser.parse_args(['eval', self.detector, '--ignore'] + black_list)
        self.assertEqual(black_list, result.black_list)

    def test_ignore_default(self):
        result = self.parser.parse_args(['eval', self.detector])
        self.assertEqual([], result.black_list)

    def test_timeout(self):
        value = '100'
        result = self.parser.parse_args(['eval', self.detector, '--timeout', value])
        self.assertEqual(int(value), result.timeout)

    def test_timeout_default_none(self):
        result = self.parser.parse_args(['eval', self.detector])
        self.assertIsNone(result.timeout)

    def test_timeout_non_int_fails(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['eval', self.detector, '--timeout', 'string'])

    def test_fails_for_invalid_detector(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['eval', 'invalid-detector'])


if __name__ == '__main__':
    unittest.main()
