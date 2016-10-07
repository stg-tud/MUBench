from os.path import join

from nose.tools import assert_equals, assert_is_instance

from benchmark.data.experiment import Experiment
from benchmark.data.run import Run
from benchmark.data.detector_execution import MineAndDetectExecution, DetectOnlyExecution
from benchmark_tests.test_utils.data_util import create_project, create_version, create_misuse
from detectors.dummy.dummy import DummyDetector


class TestExperiment:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.detector = DummyDetector("-detectors-")
        self.project = create_project("-project-")
        self.version = create_version("-version-", project=self.project)

    def test_provided_patterns_run(self):
        experiment = Experiment(Experiment.PROVIDED_PATTERNS, self.detector, "-findings_path-", "-reviews-path-")

        run = experiment.get_run(self.version)

        assert_is_instance(run, Run)
        assert_equals(1, len(run.executions))
        assert_is_instance(run.executions[0], DetectOnlyExecution)

    def test_top_findings_run(self):
        experiment = Experiment(Experiment.TOP_FINDINGS, self.detector, "-findings_path-", "-reviews-path-")

        run = experiment.get_run(self.version)

        assert_is_instance(run, Run)
        assert_equals(1, len(run.executions))
        assert_is_instance(run.executions[0], MineAndDetectExecution)

    def test_benchmark_run(self):
        experiment = Experiment(Experiment.BENCHMARK, self.detector, "-findings_path-", "-reviews-path-")

        run = experiment.get_run(self.version)

        assert_is_instance(run, Run)
        assert_equals(1, len(run.executions))
        assert_is_instance(run.executions[0], MineAndDetectExecution)

    def test_review_path_top_findings(self):
        experiment = Experiment(Experiment.TOP_FINDINGS, self.detector, "", "-reviews_path-")

        review_path = experiment.get_review_path(self.version)

        assert_equals(review_path, join("-reviews_path-", Experiment.TOP_FINDINGS, "dummy", "-project-", "-version-"))

    def test_review_path_benchmark(self):
        experiment = Experiment(Experiment.BENCHMARK, self.detector, "", "-reviews_path-")
        misuse = create_misuse("-misuse-", project=self.project)

        review_path = experiment.get_review_path(self.version, misuse)

        assert_equals(review_path,
                      join("-reviews_path-", Experiment.BENCHMARK, "dummy", "-project-", "-version-", "-misuse-"))
