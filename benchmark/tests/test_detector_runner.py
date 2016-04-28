import unittest
from os import listdir

import detector_runner
from tests.test_utils.test_env_util import TestEnvironment


class DetectorRunnerTest(unittest.TestCase):
    def setUp(self):
        self.test_env = TestEnvironment()

        self.uut = detector_runner.DetectorRunner(self.test_env.DATA_PATH,
                                                  self.test_env.DETECTOR,
                                                  self.test_env.CHECKOUT_DIR,
                                                  self.test_env.RESULTS_PATH,
                                                  self.test_env.TIMEOUT,
                                                  catch_errors=False)

    def tearDown(self):
        self.test_env.tearDown()

    def test_run(self):
        self.assertGreater(len(self.test_env.DATA), 0, "Test data is empty")
        self.uut.run_detector_on_all_data()
        self.assertFalse(listdir(self.test_env.RESULTS_PATH) == [])


if __name__ == '__main__':
    unittest.main()
