from os.path import join
from tempfile import mkdtemp
from shutil import rmtree

from benchmark.detect import Detect

from nose.tools import assert_equals
from benchmark.nosetests.test_misuse import TMisuse

# noinspection PyAttributeOutsideInit
class TestDetect:
    
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-detect-test_')
        self.checkout_base = join(self.temp_dir, "checkout")
        self.findings_file = join(self.temp_dir, "findings.yml")
        self.results_path = join(self.temp_dir, "results")
        
        self.uut = Detect("detector", self.findings_file, self.checkout_base, self.results_path, None, [])
        
        # mock command-line invocation
        def mock_invoke_detector(detect, absolute_misuse_detector_path: str, detector_args: str, out_log, error_log):
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
        self.uut.run_detector(TMisuse("project.id", {}))
        
        assert_equals(self.last_invoke, ("detector.jar", [join(self.checkout_base, "project"), self.findings_file]))
        
    def test_invokes_detector_with_patterns(self):
        @property
        def mock_pattern(self):
            return ["p1", "p2"]
        
        misuse = TMisuse("project", {})
        orig_pattern = TMisuse.pattern
        try:
            TMisuse.pattern = mock_pattern
            self.uut.run_detector(misuse)
            
            assert_equals(self.last_invoke, ("detector.jar", [join(self.checkout_base, "project"), self.findings_file, "p1", "p2"]))
        finally:
            TMisuse.pattern = orig_pattern
