import os
from os.path import join, exists
from shutil import rmtree
from tempfile import mkdtemp
from unittest.mock import MagicMock

from nose.tools import assert_equals, assert_raises

from benchmark.data.detector import DefaultDetector
from benchmark.data.experiment import Experiment
from benchmark.data.pattern import Pattern
from benchmark.data.run import Run
from benchmark.subprocesses.tasks.base.project_task import Response
from benchmark.subprocesses.tasks.implementations.detect import Detect, DetectorMode
from benchmark.utils.io import write_yaml
from benchmark_tests.test_utils.data_util import create_project, create_version, create_misuse


# noinspection PyAttributeOutsideInit
class TestDetect:
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-detect-test_')
        self.compiles_path = join(self.temp_dir, "checkout")
        self.findings_path = join(self.temp_dir, "findings")

        os.chdir(self.temp_dir)

        self.detector = DefaultDetector("path", "detector")
        self.experiment = Experiment(Experiment.TOP_FINDINGS, self.detector, self.findings_path, "")
        self.uut = Detect(self.compiles_path, self.experiment, None, [], False)

        self.last_invoke = None

        # mock command-line invocation
        def mock_invoke_detector(detect, absolute_misuse_detector_path: str, detector_args: str):
            self.last_invoke = absolute_misuse_detector_path, detector_args

        self.orig_invoke_detector = Detect._invoke_detector
        Detect._invoke_detector = mock_invoke_detector

    def teardown(self):
        Detect._invoke_detector = self.orig_invoke_detector
        rmtree(self.temp_dir, ignore_errors=True)

    def test_invokes_detector(self):
        project = create_project("project")
        version = create_version("0", project=project)

        self.uut.process_project_version(project, version)

        assert_equals(self.last_invoke[0], self.detector.jar_path)

    def test_passes_detect_only_paths(self):
        project = create_project("project")
        misuse = create_misuse("misuse", project=project)
        misuse._PATTERNS = [Pattern("", "")]
        version = create_version("0", misuses=[misuse])
        self.experiment.id = Experiment.PROVIDED_PATTERNS

        self.uut.process_project_version(project, version)

        compile = version.get_compile(self.compiles_path)
        self.assert_last_invoke_path_equals(self.uut.key_training_src_path, compile.pattern_sources_base_path)
        self.assert_last_invoke_path_equals(self.uut.key_training_classpath, compile.pattern_classes_base_path)
        self.assert_last_invoke_path_equals(self.uut.key_target_src_path, compile.misuse_source_path)
        self.assert_last_invoke_path_equals(self.uut.key_target_classpath, compile.misuse_classes_path)

    def test_passes_mine_and_detect_paths(self):
        project = create_project("project")
        version = create_version("0")
        self.experiment.id = Experiment.TOP_FINDINGS

        self.uut.process_project_version(project, version)

        compile = version.get_compile(self.compiles_path)
        self.assert_arg_not_in_last_invoke(self.uut.key_training_src_path)
        self.assert_arg_not_in_last_invoke(self.uut.key_training_classpath)
        self.assert_last_invoke_path_equals(self.uut.key_target_src_path, compile.original_sources_path)
        self.assert_last_invoke_path_equals(self.uut.key_target_classpath, compile.original_classes_path)

    def test_passes_findings_file(self):
        project = create_project("project")
        version = create_version("0", project=project)

        self.uut.process_project_version(project, version)

        self.assert_last_invoke_path_equals(self.uut.key_findings_file,
                                            self.experiment.get_run(version).findings_file_path)

    def test_invokes_detector_with_mode(self):
        project = create_project("project")
        version = create_version("0", project=project)
        self.uut.detector_mode = DetectorMode.mine_and_detect

        self.uut.process_project_version(project, version)

        self.assert_last_invoke_path_equals(self.uut.key_detector_mode, '0')

    def test_passes_run_file(self):
        project = create_project("project")
        version = create_version("0", project=project)

        self.uut.process_project_version(project, version)

        self.assert_last_invoke_path_equals(self.uut.key_run_file,
                                            self.experiment.get_run(version).run_file_path)

    def test_writes_results(self):
        project = create_project("project")
        version = create_version("0", project=project)

        self.uut.process_project_version(project, version)

        assert exists(self.experiment.get_run(version).run_file_path)

    def test_skips_detect_if_previous_run_succeeded(self):
        project = create_project("project")
        version = create_version("0", project=project)
        write_yaml({"result": "success"}, file=self.experiment.get_run(version).run_file_path)
        self.uut._invoke_detector = MagicMock(side_effect=UserWarning)

        self.uut.process_project_version(project, version)

    def test_skips_detect_if_previous_run_was_error(self):
        project = create_project("project")
        version = create_version("0", project=project)
        write_yaml({"result": "error"}, file=self.experiment.get_run(version).run_file_path)
        self.uut._invoke_detector = MagicMock(side_effect=UserWarning)

        self.uut.process_project_version(project, version)

    def test_force_detect_on_new_detector(self):
        project = create_project("project")
        version = create_version("0", project=project)
        write_yaml({"result": "success"}, file=self.experiment.get_run(version).run_file_path)
        self.uut._new_detector_available = lambda x: True
        self.uut._invoke_detector = MagicMock(side_effect=UserWarning)

        assert_raises(UserWarning, self.uut.process_project_version, project, version)

    def test_skips_detect_only_if_no_patterns_are_available(self):
        project = create_project("project")
        version = create_version("0", project=project)
        self.experiment.id = Experiment.PROVIDED_PATTERNS
        self.uut._invoke_detector = MagicMock(side_effect=UserWarning)

        response = self.uut.process_project_version(project, version)

        assert_equals(Response.skip, response)

    def assert_last_invoke_path_equals(self, key, value):
        self.assert_arg_value_equals(self.last_invoke[1], key, '"' + value + '"')

    def assert_arg_not_in_last_invoke(self, key):
        assert key not in self.last_invoke[1]

    @staticmethod
    def assert_arg_value_equals(args, key, value):
        assert key in args, "{} not in {}".format(key, args)
        for i, arg in enumerate(args):
            if arg is key:
                assert_equals(args[i + 1], value)


class TestDetectorDownload:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-detect-test_')
        self.compiles_path = join(self.temp_dir, "checkout")
        self.findings_file = "findings.yml"
        self.run_file = Run.RUN_FILE
        self.findings_path = join(self.temp_dir, "results")

        detector = DefaultDetector("path", "detector")
        self.uut = Detect(self.compiles_path, Experiment(Experiment.PROVIDED_PATTERNS, detector, self.findings_path, ""),
                          None, [], False)
        self.uut._download = MagicMock(return_value=True)

    def test_downloads_detector_if_not_available(self):
        self.uut._detector_available = MagicMock(return_value=False)

        self.uut.start()

        self.uut._download.assert_called_with()
