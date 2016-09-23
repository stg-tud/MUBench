from nose.tools import assert_equals
from os.path import join

from benchmark.data.experiment import DetectorMode, Experiment
from benchmark_tests.test_utils.data_util import create_project, create_version, create_misuse


class TestExperiment:
    def test_detect_only_for_provided_patterns(self):
        assert_equals(DetectorMode.detect_only, Experiment(Experiment.PROVIDED_PATTERNS, "", "").detector_mode)

    def test_mine_and_detect_for_top_findings(self):
        assert_equals(DetectorMode.mine_and_detect, Experiment(Experiment.TOP_FINDINGS, "", "").detector_mode)

    def test_mine_and_detect_for_benchmark(self):
        assert_equals(DetectorMode.mine_and_detect, Experiment(Experiment.BENCHMARK, "", "").detector_mode)

    def test_review_path_top_findings(self):
        project = create_project("-project-")
        version = create_version("-version-", project=project)
        experiment = Experiment(Experiment.TOP_FINDINGS, "", "-reviews_path-")

        review_path = experiment.get_review_path(version)

        assert_equals(review_path, join("-reviews_path-", Experiment.TOP_FINDINGS, "-project-", "-version-"))

    def test_review_path_benchmark(self):
        project = create_project("-project-")
        version = create_version("-version-", project=project)
        misuse = create_misuse("-misuse-", project=project)
        experiment = Experiment(Experiment.BENCHMARK, "", "-reviews_path-")

        review_path = experiment.get_review_path(version, misuse)

        assert_equals(review_path, join("-reviews_path-", Experiment.BENCHMARK, "-project-", "-version-", "-misuse-"))
