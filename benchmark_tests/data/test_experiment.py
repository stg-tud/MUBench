from os.path import join

from nose.tools import assert_equals

from benchmark.data.detector import Detector
from benchmark.data.experiment import Experiment
from benchmark_tests.test_utils.data_util import create_project, create_version, create_misuse


class TestExperiment:
    def test_detector_run_mode(self):
        experiment = Experiment(Experiment.PROVIDED_PATTERNS, Detector("", ""), "", "")

        assert_equals(experiment.detector_mode, Experiment.RUN_MODES[Experiment.PROVIDED_PATTERNS])

    def test_run_path(self):
        detector = Detector("", "-detector-")
        experiment = Experiment(Experiment.BENCHMARK, detector, "-findings_path-", "")
        project = create_project("-project-")
        version = create_version("-version-", project=project)

        run = experiment.get_run(version)

        assert_equals(run._Run__path, join("-findings_path-", "0", "-detector-", "-project-", "-version-"))

    def test_review_path_top_findings(self):
        detector = Detector("", "-detector-")
        experiment = Experiment(Experiment.TOP_FINDINGS, detector, "", "-reviews_path-")
        project = create_project("-project-")
        version = create_version("-version-", project=project)

        review_path = experiment.get_review_path(version)

        assert_equals(review_path,
                      join("-reviews_path-", Experiment.TOP_FINDINGS, "-detector-", "-project-", "-version-"))

    def test_review_path_benchmark(self):
        detector = Detector("", "-detector-")
        experiment = Experiment(Experiment.BENCHMARK, detector, "", "-reviews_path-")
        project = create_project("-project-")
        version = create_version("-version-", project=project)
        misuse = create_misuse("-misuse-", project=project)

        review_path = experiment.get_review_path(version, misuse)

        assert_equals(review_path,
                      join("-reviews_path-", Experiment.BENCHMARK, "-detector-", "-project-", "-version-", "-misuse-"))
