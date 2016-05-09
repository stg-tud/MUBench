from benchmark.detector_runner import DetectorRunner
from benchmark.nosetests.test_utils.test_env_util import TestEnv

test_env = None


def setup_module(module):
    module.test_env = TestEnv()
    assert len(test_env.DATA) > 0, "Test data is empty"


def teardown_module(module):
    module.test_env.tearDown()


def test_run():
    uut = DetectorRunner(test_env.DATA_PATH, test_env.DETECTOR, test_env.CHECKOUT_DIR, test_env.RESULTS_PATH,
                         test_env.TIMEOUT, white_list=[""], black_list=[], catch_errors=False)
    uut.run_detector_on_all_data()
    assert not test_env.RESULTS_PATH == []
