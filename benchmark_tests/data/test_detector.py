from nose.tools import assert_equals
from os.path import join

from benchmark.data.detector import Detector
from benchmark.data.experiment import Experiment
from benchmark_tests.test_utils.data_util import create_version, create_project


class TestDetector:
    def test_run_path(self):
        detector = Detector("-detectors_path-", "-detector-")
        experiment = Experiment("1", "-findings_path-", "")
        project = create_project("-project-")
        version = create_version("-version-", project=project)

        run = detector.get_run(experiment, version)

        assert_equals(run._Run__path, join("-findings_path-", "1", "-detector-", "-project-", "-version-"))
