import os
from os.path import join, exists
from shutil import rmtree
from tempfile import mkdtemp
from unittest.mock import MagicMock

from nose.tools import assert_equals, assert_raises

from benchmark.data.pattern import Pattern
from benchmark.subprocesses.tasks.implementations.detect import Detect
from benchmark.utils.io import write_yaml
from benchmark_tests.test_utils.data_util import create_misuse, create_project, create_version


# noinspection PyAttributeOutsideInit
class TestDetect:
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-detect-test_')
        self.checkout_base = join(self.temp_dir, "checkout")
        self.findings_file = "findings.yml"
        self.results_path = join(self.temp_dir, "results")

        os.chdir(self.temp_dir)

        self.uut = Detect("detector", self.findings_file, self.checkout_base, self.results_path, None, [], False)

        self.last_invoke = None

        # mock command-line invocation
        def mock_invoke_detector(detect, absolute_misuse_detector_path: str, detector_args: str):
            self.last_invoke = absolute_misuse_detector_path, detector_args

        self.orig_invoke_detector = Detect._invoke_detector
        Detect._invoke_detector = mock_invoke_detector

        # mock path resolving
        def mock_get_misuse_detector_path(detector: str):
            self.last_detector = detector
            return detector + ".jar"

        self.orig_get_misuse_detector_path = Detect._Detect__get_misuse_detector_path
        Detect._Detect__get_misuse_detector_path = mock_get_misuse_detector_path

    def teardown(self):
        Detect._invoke_detector = self.orig_invoke_detector
        Detect._Detect__get_misuse_detector_path = self.orig_get_misuse_detector_path
        rmtree(self.temp_dir, ignore_errors=True)

    def test_invokes_detector(self):
        project = create_project("project")
        version = create_version("0", project=project)

        self.uut.process_project_version(project, version)

        assert_equals(self.last_invoke[0], "detector.jar")

    def test_passes_project_src(self):
        project = create_project("project")
        version = create_version("0")

        self.uut.process_project_version(project, version)

        self.assert_last_invoke_arg_value_equals(
            self.uut.key_src_project,
            '"' + version.get_compile(self.checkout_base).original_sources_path + '"')

    def test_passes_misuse_src(self):
        project = create_project("project")
        version = create_version("0")

        self.uut.process_project_version(project, version)

        self.assert_last_invoke_arg_value_equals(
            self.uut.key_src_misuse,
            '"' + version.get_compile(self.checkout_base).misuse_source_path + '"')

    def test_passes_project_classes_path(self):
        project = create_project("project")
        version = create_version("0", meta={"build": {"commands": [":any:"]}}, project=project)

        self.uut.process_project_version(project, version)

        self.assert_last_invoke_arg_value_equals(
            self.uut.key_classes_project,
            '"' + version.get_compile(self.checkout_base).original_classes_path + '"')

    def test_passes_misuse_classes_path(self):
        project = create_project("project")
        version = create_version("0", meta={"build": {"commands": [":any:"]}}, project=project)

        self.uut.process_project_version(project, version)

        self.assert_last_invoke_arg_value_equals(
            self.uut.key_classes_misuse,
            '"' + version.get_compile(self.checkout_base).misuse_classes_path + '"')

    def test_passes_findings_file(self):
        project = create_project("project")
        version = create_version("0", project=project)

        self.uut.process_project_version(project, version)

        self.assert_last_invoke_arg_value_equals(self.uut.key_findings_file,
                                                 '"' + join(self.results_path, "project", "0", self.findings_file) + '"')

    def test_invokes_detector_without_patterns_paths_without_patterns(self):
        project = create_project("project")
        version = create_version("0")

        self.uut.process_project_version(project, version)

        self.assert_arg_not_in_last_invoke(self.uut.key_src_patterns)
        self.assert_arg_not_in_last_invoke(self.uut.key_classes_patterns)

    def test_invokes_detector_with_patterns_src_path(self):
        project = create_project("project")
        version = create_version("0", meta={"build": {"commands": [":any:"]}}, project=project)
        version._PATTERNS = [Pattern("", "a")]

        self.uut.process_project_version(project, version)

        self.assert_last_invoke_arg_value_equals(
            self.uut.key_src_patterns,
            '"' + version.get_compile(self.checkout_base).pattern_sources_path + '"')

    def test_invokes_detector_with_patterns_class_path(self):
        project = create_project("project")
        version = create_version("0", meta={"build": {"commands": {":any:"}}}, project=project)
        version._PATTERNS = [Pattern("", "a")]

        self.uut.process_project_version(project, version)

        self.assert_last_invoke_arg_value_equals(
            self.uut.key_classes_patterns,
            '"' + version.get_compile(self.checkout_base).pattern_classes_path + '"')

    def test_writes_results(self):
        project = create_project("project")
        version = create_version("0", project=project)

        self.uut.process_project_version(project, version)

        assert exists(join(self.results_path, version.project_id, version.version_id, "result.yml"))

    def test_skips_detect_if_previous_run_succeeded(self):
        project = create_project("project")
        version = create_version("0", project=project)
        write_yaml({"result": "success"},
                   file=join(self.results_path, version.project_id, version.version_id, "result.yml"))
        self.uut._invoke_detector = MagicMock(side_effect=UserWarning)

        self.uut.process_project_version(project, version)

    def test_repeats_detection_if_previous_run_failed(self):
        project = create_project("project")
        version = create_version("0", project=project)
        write_yaml({"result": "error"},
                   file=join(self.results_path, version.project_id, version.version_id, "result.yml"))
        self.uut._invoke_detector = MagicMock(side_effect=UserWarning)

        assert_raises(UserWarning, self.uut.process_project_version, project, version)

    def test_force_detect_on_new_detector(self):
        project = create_project("project")
        version = create_version("0", project=project)
        write_yaml({"result": "success"},
                   file=join(self.results_path, version.project_id, version.version_id, "result.yml"))
        self.uut._new_detector_available = lambda x: True
        self.uut._invoke_detector = MagicMock(side_effect=UserWarning)

        assert_raises(UserWarning, self.uut.process_project_version, project, version)

    def assert_last_invoke_arg_value_equals(self, key, value):
        self.assert_arg_value_equals(self.last_invoke[1], key, value)

    def assert_arg_not_in_last_invoke(self, key):
        assert key not in self.last_invoke[1]

    @staticmethod
    def assert_arg_value_equals(args, key, value):
        assert key in args, "{} not in {}".format(key, args)
        for i, arg in enumerate(args):
            if arg is key:
                assert_equals(args[i + 1], value)


class TestDetectDownload:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-detect-test_')
        self.checkout_base = join(self.temp_dir, "checkout")
        self.findings_file = "findings.yml"
        self.results_path = join(self.temp_dir, "results")

        self.uut = Detect("detector", self.findings_file, self.checkout_base, self.results_path, None, [], False)
        self.uut._download = MagicMock(return_value=True)

    def test_downloads_detector_if_not_available(self):
        self.uut._detector_available = MagicMock(return_value=False)

        self.uut.start()

        self.uut._download.assert_called_with()
