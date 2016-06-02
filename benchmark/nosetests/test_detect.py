from os.path import join
from tempfile import mkdtemp
from shutil import rmtree

from benchmark.detect import Detect

from nose.tools import assert_equals
from benchmark.nosetests.test_misuse import TMisuse

from benchmark.pattern import Pattern


class TestDetect:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-detect-test_')
        self.checkout_base = join(self.temp_dir, "checkout")
        self.findings_file = "findings.yml"
        self.results_path = join(self.temp_dir, "results")

        self.uut = Detect("detector", self.findings_file, self.checkout_base, self.results_path, None, [])

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
        self.uut.run_detector(TMisuse("project.id", {}))

        assert_equals(self.last_invoke[0], "detector.jar")

    def test_passes_project_src(self):
        src_path = "src/java/"
        self.uut.run_detector(TMisuse("project.id", {"build": {"src": src_path, "classes": "", "commands": []}}))

        assert_equals(self.last_invoke[1][0], join(self.checkout_base, "project", src_path))

    def test_passes_classes_path(self):
        classes_path = "target/classes/"
        self.uut.run_detector(TMisuse("project.id", {"build": {"classes": classes_path, "src": "", "commands": []}}))

        assert_equals(self.last_invoke[1][1], join(self.checkout_base, "project", classes_path))

    def test_passes_findings_files(self):
        self.uut.run_detector(TMisuse("project.id", {}))

        assert_equals(self.last_invoke[1][2], join(self.results_path, "project.id", self.findings_file))

    def test_invokes_detector_with_patterns(self):
        @property
        def mock_patterns(self):
            return [Pattern("p1"), Pattern("p2")]

        misuse = TMisuse("project", {})
        orig_pattern = TMisuse.patterns
        try:
            TMisuse.patterns = mock_patterns
            self.uut.run_detector(misuse)

            assert_equals(["p1", "p2"], self.last_invoke[1][3:])
        finally:
            TMisuse.patterns = orig_pattern
