# coding=utf-8
from os.path import join, exists
from tempfile import mkdtemp
from typing import Iterable

from nose.tools import assert_equals, assert_raises

from benchmark.data.misuse import Misuse
from benchmark.subprocesses.result_processing.visualize_results import Visualizer, Grouping
from benchmark.utils.io import remove_tree, safe_write


# noinspection PyAttributeOutsideInit
class TestVisualizer:
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-visualize-test_")
        self.results_base_dir = join(self.temp_dir, "results")
        self.reviewed_detector_result = "reviewed-result.csv"
        self.visualize_result_file = "result.csv"
        self.data_path = join(self.temp_dir, "data")
        self.uut = Visualizer(self.results_base_dir, self.reviewed_detector_result, self.visualize_result_file,
                              self.data_path)

    def teardown(self):
        remove_tree(self.temp_dir)

    def exits_if_result_folder_doesnt_exist(self):
        self.uut = Visualizer("non-existent-dir", self.reviewed_detector_result, self.visualize_result_file, "")
        assert_raises(SystemExit, self.uut.create)

    def exits_if_no_results_are_found(self):
        assert_raises(SystemExit, self.uut.create)

    def test_generates_result_for_one_detector(self):
        test_result = "Misuse1, 0\nMisuse2, 1\nMisuse3, 0"
        self.create_detector_result("Detector1", test_result)

        self.uut.create()

        visualize_result_file = join(self.results_base_dir, self.visualize_result_file)
        assert exists(visualize_result_file)
        with open(visualize_result_file) as actual_file:
            actual_result = actual_file.read()

        expected_result = "Detector,Misuse1,Misuse2,Misuse3\nDetector1, 0, 1, 0\n"
        assert_equals(expected_result, actual_result)

    def test_generates_result_for_multiple_detectors(self):
        test_result1 = "Misuse1, 0\nMisuse2, 1"
        test_result2 = "Misuse2, 1\nMisuse3, 0"
        self.create_detector_result("Detector1", test_result1)
        self.create_detector_result("Detector2", test_result2)

        self.uut.create()

        visualize_result_file = join(self.results_base_dir, self.visualize_result_file)
        assert exists(visualize_result_file)
        with open(visualize_result_file) as actual_file:
            actual_result = actual_file.read()

        expected_result = "Detector,Misuse1,Misuse2,Misuse3\nDetector1, 0, 1,\nDetector2,, 1, 0\n"
        assert_equals(expected_result, actual_result)

    def test_group_results(self):
        source_file = join(self.results_base_dir, self.visualize_result_file)
        target_file = 'test-grouping.csv'

        # Detector  MU1 MU2 MU3 MU4
        # Det1      0   0   0   1
        # Det2      1   0   1   1
        safe_write("Detector,MU1,MU2,MU3,MU4\nDet1,0,0,0,1\nDet2,1,0,1,1", source_file, append=False)
        # Assuming MU1/MU2 and MU3/MU4 belong to the same groups we expect:
        # Detector  Group1  Group2
        # Det1      0.0     0.5
        # Det2      0.5     1.0
        expected = "Detector,Group1,Group2\nDet1,0.0,0.5\nDet2,0.5,1.0\n"

        ismisuse_orig = Misuse.ismisuse
        try:
            Misuse.ismisuse = lambda path: any(name in path for name in ["MU1", "MU2", "MU3", "MU4"])

            class GroupingTestImpl(Grouping):
                def get_groups(self, misuse: Misuse) -> Iterable[str]:
                    return ["Group1" if misuse.name in ["MU1", "MU2"] else "Group2"]

            self.uut.group('test-grouping.csv', GroupingTestImpl())
        finally:
            Misuse.ismisuse = ismisuse_orig

        with open(join(self.results_base_dir, target_file)) as actual_file:
            actual = actual_file.read()

        assert_equals(expected, actual)

    def create_detector_result(self, detector, content):
        detector_result_file = join(self.results_base_dir, detector, self.reviewed_detector_result)
        safe_write(content, detector_result_file, append=False)


class TestGrouping:
    class GroupingTestImpl(Grouping):
        def get_groups(self, misuse: Misuse) -> Iterable[str]:
            return ['']

    def test_get_available_groupings(self):
        actual = Grouping.get_available_groupings()
        assert TestGrouping.GroupingTestImpl in actual

    def test_get_available_grouping_names(self):
        actual = Grouping.get_available_grouping_names()
        assert "GroupingTestImpl" in actual

    def test_get_by_name(self):
        assert_equals(TestGrouping.GroupingTestImpl, Grouping.get_by_name("GroupingTestImpl"))

