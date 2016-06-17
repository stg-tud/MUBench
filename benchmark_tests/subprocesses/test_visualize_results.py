# coding=utf-8
from os.path import join, exists
from tempfile import mkdtemp

from nose.tools import assert_equals, assert_raises

from benchmark.subprocesses.visualize_results import Visualizer
from benchmark.utils.io import remove_tree, safe_write


# noinspection PyAttributeOutsideInit
class TestVisualizer:
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-visualize-test_")
        self.results_base_dir = join(self.temp_dir, "results")
        self.reviewed_detector_result = "reviewed-result.csv"
        self.visualize_result_file = "result.csv"
        self.uut = Visualizer(self.results_base_dir, self.reviewed_detector_result, self.visualize_result_file)

    def teardown(self):
        remove_tree(self.temp_dir)

    def exits_if_result_folder_doesnt_exist(self):
        self.uut = Visualizer("non-existent-dir", self.reviewed_detector_result, self.visualize_result_file)
        assert_raises(SystemExit, self.uut.run)

    def exits_if_no_results_are_found(self):
        assert_raises(SystemExit, self.uut.run)

    def test_generates_result_for_one_detector(self):
        test_result = "Misuse1, 0\nMisuse2, 1\nMisuse3, 0"
        self.create_detector_result("Detector1", test_result)

        self.uut.run()

        visualize_result_file = join(self.results_base_dir, self.visualize_result_file)
        assert exists(visualize_result_file)
        with open(visualize_result_file) as actual_file:
            actual_result = actual_file.read()

        expected_result = "Detector,Misuse1,Misuse2,Misuse3\n\nDetector1, 0, 1, 0\n\n"
        assert_equals(expected_result, actual_result)

    def test_generates_result_for_multiple_detectors(self):
        test_result1 = "Misuse1, 0\nMisuse2, 1"
        test_result2 = "Misuse2, 1\nMisuse3, 0"
        self.create_detector_result("Detector1", test_result1)
        self.create_detector_result("Detector2", test_result2)

        self.uut.run()

        visualize_result_file = join(self.results_base_dir, self.visualize_result_file)
        assert exists(visualize_result_file)
        with open(visualize_result_file) as actual_file:
            actual_result = actual_file.read()

        expected_result = "Detector,Misuse1,Misuse2,Misuse3\n\nDetector1, 0, 1,\n\nDetector2,, 1, 0\n\n"
        assert_equals(expected_result, actual_result)

    def create_detector_result(self, detector, content):
        detector_result_file = join(self.results_base_dir, detector, self.reviewed_detector_result)
        safe_write(content, detector_result_file, append=False)
