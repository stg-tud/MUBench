from os.path import join

from nose.tools import assert_equals

from benchmark.data.detector import Detector
from benchmark.data.experiment import Experiment
from benchmark.data.run import Run
from benchmark_tests.test_utils.data_util import create_project, create_version, create_misuse


class TestExperiment:
    def test_detector_run_mode(self):
        experiment = Experiment(Experiment.PROVIDED_PATTERNS, Detector("", ""), "", "")

        assert_equals(experiment.detector_mode, Experiment.RUN_MODES[Experiment.PROVIDED_PATTERNS])

    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.detector = Detector("", "-detector-")
        self.project = create_project("-project-")
        self.version = create_version("-version-", project=self.project)

    def test_run(self):
        experiment = Experiment(Experiment.BENCHMARK, self.detector, "-findings_path-", "")

        run = experiment.get_run(self.version)

        assert_equals(run.findings_path,
                      join("-findings_path-", "mine_and_detect", "-detector-", "-project-", "-version-"))

    def test_review_path_top_findings(self):
        experiment = Experiment(Experiment.TOP_FINDINGS, self.detector, "", "-reviews_path-")

        review_path = experiment.get_review_path(self.version)

        assert_equals(review_path,
                      join("-reviews_path-", Experiment.TOP_FINDINGS, "-detector-", "-project-", "-version-"))

    def test_review_path_benchmark(self):
        experiment = Experiment(Experiment.BENCHMARK, self.detector, "", "-reviews_path-")
        misuse = create_misuse("-misuse-", project=self.project)

        review_path = experiment.get_review_path(self.version, misuse)

        assert_equals(review_path,
                      join("-reviews_path-", Experiment.BENCHMARK, "-detector-", "-project-", "-version-", "-misuse-"))
