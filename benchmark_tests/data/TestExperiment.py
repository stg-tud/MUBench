from nose.tools import assert_equals

from benchmark.data.experiment import DetectorMode, Experiment


class TestExperiment:
    def test_detect_only_for_provided_patterns(self):
        assert_equals(DetectorMode.detect_only, Experiment(Experiment.PROVIDED_PATTERNS).detector_mode)

    def test_mine_and_detect_for_top_findings(self):
        assert_equals(DetectorMode.mine_and_detect, Experiment(Experiment.TOP_FINDINGS).detector_mode)

    def test_mine_and_detect_for_benchmark(self):
        assert_equals(DetectorMode.mine_and_detect, Experiment(Experiment.BENCHMARK).detector_mode)
