from os.path import join

from nose.tools import assert_equals, assert_is_instance

from benchmark.data.experiment import Experiment
from benchmark.data.findings_filters import AllFindings
from benchmark.data.run import Run
from benchmark.data.detector_execution import MineAndDetectExecution, DetectOnlyExecution
from benchmark_tests.test_utils.data_util import create_project, create_version, create_misuse
from detectors.Dummy.Dummy import Dummy


class TestExperiment:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.detector = Dummy("-detectors-")
        self.project = create_project("-project-")
        self.version = create_version("-version-", project=self.project)

    def test_provided_patterns_run(self):
        experiment = Experiment(Experiment.PROVIDED_PATTERNS, self.detector, "-findings_path-")

        run = experiment.get_run(self.version)

        assert_is_instance(run, Run)
        assert_equals(1, len(run.executions))
        assert_is_instance(run.executions[0], DetectOnlyExecution)

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
