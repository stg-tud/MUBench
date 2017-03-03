from os.path import join

from nose.tools import assert_equals, assert_is_instance

from data.experiment import Experiment
from data.findings_filters import AllFindings
from data.pattern import Pattern
from data.run import Run
from data.detector_execution import MineAndDetectExecution, DetectOnlyExecution
from tests.data.stub_detector import StubDetector
from tests.test_utils.data_util import create_project, create_version, create_misuse


class TestExperiment:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.detector = StubDetector()
        self.project = create_project("-project-")
        self.version = create_version("-version-", project=self.project)

    def test_provided_patterns_run(self):
        self.version._MISUSES = [create_misuse("-1-", project=self.project, patterns=[Pattern("-base-", "-P1-")])]

        experiment = Experiment(Experiment.PROVIDED_PATTERNS, self.detector, "-findings_path-")

        run = experiment.get_run(self.version)

        assert_is_instance(run, Run)
        assert_equals(1, len(run.executions))
        assert_is_instance(run.executions[0], DetectOnlyExecution)

    def test_provided_patterns_run_no_patterns(self):
        self.version._MISUSES = [create_misuse("-1-", project=self.project, patterns=[])]

        experiment = Experiment(Experiment.PROVIDED_PATTERNS, self.detector, "-findings_path-")

        run = experiment.get_run(self.version)

        assert_is_instance(run, Run)
        assert_equals(0, len(run.executions))

    def test_top_findings_run(self):
        experiment = Experiment(Experiment.TOP_FINDINGS, self.detector, "-findings_path-", 42)

        run = experiment.get_run(self.version)

        assert_is_instance(run, Run)
        assert_equals(1, len(run.executions))
        assert_is_instance(run.executions[0], MineAndDetectExecution)
        assert_is_instance(run.executions[0].findings_filter, AllFindings)
        assert_equals(42, run.executions[0].findings_filter.limit)

    def test_benchmark_run(self):
        experiment = Experiment(Experiment.BENCHMARK, self.detector, "-findings_path-")

        run = experiment.get_run(self.version)

        assert_is_instance(run, Run)
        assert_equals(1, len(run.executions))
        assert_is_instance(run.executions[0], MineAndDetectExecution)
