from os.path import join
from tempfile import mkdtemp
from shutil import rmtree

from benchmark.detect import Detect

from nose.tools import assert_equals
from benchmark.nosetests.test_misuse import TMisuse
from benchmark.nosetests.test_utils.subprocess_util import run_on_misuse

from benchmark.pattern import Pattern


# noinspection PyUnusedLocal
class TestDetect:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-detect-test_')
        self.checkout_base = join(self.temp_dir, "checkout")
        self.findings_file = "findings.yml"
        self.results_path = join(self.temp_dir, "results")

        self.src_normal_subdir = "src-normal"
        self.classes_normal_subdir = "classes-normal"
        self.src_patterns_subdir = "src-patterns"
        self.classes_patterns_subdir = "classes-patterns"

        self.uut = Detect("detector", self.findings_file, self.checkout_base, self.src_normal_subdir,
                          self.classes_normal_subdir, self.src_patterns_subdir, self.classes_patterns_subdir,
                          self.results_path, None, [])

        # mock command-line invocation
        def mock_invoke_detector(detect, absolute_misuse_detector_path: str, detector_args: str, out_log, error_log):
            self.last_invoke = absolute_misuse_detector_path, detector_args

        self.last_invoke = None

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
        run_on_misuse(self.uut, TMisuse("project.id", {}))

        assert_equals(self.last_invoke[0], "detector.jar")

    def test_passes_project_src(self):
        run_on_misuse(self.uut, TMisuse("project.id", {"build": {"src": "", "classes": "", "commands": []}}))

        self.assert_last_invoke_arg_value_equals(self.uut.key_src_project,
                                                 join(self.checkout_base, "project", self.src_normal_subdir))

    def test_passes_project_classes_path(self):
        run_on_misuse(self.uut, TMisuse("project.id", {"build": {"classes": "", "src": "", "commands": []}}))

        self.assert_last_invoke_arg_value_equals(self.uut.key_classes_project,
                                                 join(self.checkout_base, "project", self.classes_normal_subdir))

    def test_passes_findings_files(self):
        run_on_misuse(self.uut, TMisuse("project.id", {}))

        self.assert_last_invoke_arg_value_equals(self.uut.key_findings_file,
                                                 join(self.results_path, "project.id", self.findings_file))

    def test_invokes_detector_without_patterns_paths_without_patterns(self):
        run_on_misuse(self.uut, TMisuse("project.id", {"build": {"src": "", "classes": "", "commands": []}}))
        self.assert_arg_not_in_last_invoke(self.uut.key_src_patterns)
        self.assert_arg_not_in_last_invoke(self.uut.key_classes_patterns)

    def test_invokes_detector_with_patterns_src_path(self):
        @property
        def patterns_mock(detect):
            return Pattern("a")

        orig_patterns = TMisuse.patterns
        try:
            TMisuse.patterns = patterns_mock

            run_on_misuse(self.uut, TMisuse("project.id", {"build": {"src": "", "classes": "", "commands": []}}))
            self.assert_last_invoke_arg_value_equals(self.uut.key_src_patterns,
                                                     join(self.checkout_base, "project", self.src_patterns_subdir))
        finally:
            TMisuse.patterns = orig_patterns

    def test_invokes_detector_with_patterns_class_path(self):
        @property
        def patterns_mock(detect):
            return Pattern("a")

        orig_patterns = TMisuse.patterns
        try:
            TMisuse.patterns = patterns_mock

            run_on_misuse(self.uut, TMisuse("project.id", {"build": {"src": "", "classes": "", "commands": []}}))
            self.assert_last_invoke_arg_value_equals(self.uut.key_classes_patterns,
                                                     join(self.checkout_base, "project", self.classes_patterns_subdir))
        finally:
            TMisuse.patterns = orig_patterns

    def assert_last_invoke_arg_value_equals(self, key, value):
        self.assert_arg_value_equals(self.last_invoke[1], key, value)

    def assert_arg_not_in_last_invoke(self, key):
        assert key not in self.last_invoke[1]

    @staticmethod
    def assert_arg_value_equals(args, key, value):
        assert key in args
        for i, arg in enumerate(args):
            if arg is key:
                assert_equals(args[i + 1], value)
