from os import makedirs
from os.path import join, exists
from tempfile import mkdtemp

from nose.tools import assert_equals

from benchmark.subprocesses.tasks.implementations.review.html_generators import detector_index
from benchmark.utils.io import remove_tree


class TestDetectorIndexGenerator:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-test-index-generator_')

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_creates_links_to_projects(self):
        detector_findings_folder = join(self.temp_dir, 'detector')

        makedirs(join(detector_findings_folder, 'project1'))
        makedirs(join(detector_findings_folder, 'project2'))
        makedirs(join(detector_findings_folder, 'project3'))

        detector_index.generate(self.temp_dir, detector_findings_folder)

        index_file = join(self.temp_dir, 'index.html')
        assert exists(index_file)

        with open(index_file) as file:
            actual_content = file.readlines()

        expected_content = ['<p><a href="project1/index.html">project1</a></p>\n',
                            '<p><a href="project2/index.html">project2</a></p>\n',
                            '<p><a href="project3/index.html">project3</a></p>\n']

        assert_equals(sorted(expected_content), sorted(actual_content))
