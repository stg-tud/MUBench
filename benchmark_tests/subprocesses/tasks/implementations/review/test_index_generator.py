from os import makedirs
from os.path import join, exists
from tempfile import mkdtemp

from nose.tools import assert_equals

from benchmark.subprocesses.tasks.implementations.review import index_generator
from benchmark.utils.io import remove_tree
from benchmark_tests.test_utils.data_util import create_project, create_version


class TestIndexGenerator:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-test-index-generator_')

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_creates_links_to_detectors(self):
        review_folder = join(self.temp_dir, 'reviews')

        makedirs(join(review_folder, 'detector1'))
        makedirs(join(review_folder, 'detector2'))
        makedirs(join(review_folder, 'detector3'))

        index_generator.generate_main_index(review_folder)

        index_file = join(review_folder, 'index.html')
        assert exists(index_file)

        with open(index_file) as file:
            actual_content = file.readlines()

        expected_content = ['<p><a href="detector1/index.html">detector1</a></p>\n',
                            '<p><a href="detector2/index.html">detector2</a></p>\n',
                            '<p><a href="detector3/index.html">detector3</a></p>\n']

        assert_equals(expected_content, actual_content)

    def test_creates_links_to_projects(self):
        detector_folder = join(self.temp_dir, 'detector')

        makedirs(join(detector_folder, 'project1'))
        makedirs(join(detector_folder, 'project2'))
        makedirs(join(detector_folder, 'project3'))

        index_generator.generate_detector_index(detector_folder)

        index_file = join(detector_folder, 'index.html')
        assert exists(index_file)

        with open(index_file) as file:
            actual_content = file.readlines()

        expected_content = ['<p><a href="project1/index.html">project1</a></p>\n',
                            '<p><a href="project2/index.html">project2</a></p>\n',
                            '<p><a href="project3/index.html">project3</a></p>\n']

        assert_equals(expected_content, actual_content)

    def test_creates_links_to_versions(self):
        project_folder = join(self.temp_dir, 'project')

        makedirs(join(project_folder, 'version1'))
        makedirs(join(project_folder, 'version2'))
        makedirs(join(project_folder, 'version3'))

        index_generator.generate_project_index(project_folder, create_project('project'))

        index_file = join(project_folder, 'index.html')
        assert exists(index_file)

        with open(index_file) as file:
            actual_content = file.readlines()

        expected_content = ['<p><a href="version1/index.html">version1</a></p>\n',
                            '<p><a href="version2/index.html">version2</a></p>\n',
                            '<p><a href="version3/index.html">version3</a></p>\n']

        assert_equals(expected_content, actual_content)

    def test_creates_links_to_review_files(self):
        version_folder = join(self.temp_dir, 'version')

        makedirs(join(version_folder, 'project.1'))
        makedirs(join(version_folder, 'project.2'))
        makedirs(join(version_folder, 'project.3'))

        index_generator.generate_version_index(version_folder, create_project('project'), create_version('version'))

        index_file = join(version_folder, 'index.html')
        assert exists(index_file)

        with open(index_file) as file:
            actual_content = file.readlines()

        expected_content = ['<p><a href="project.1/review.html">project.1</a></p>\n',
                            '<p><a href="project.2/review.html">project.2</a></p>\n',
                            '<p><a href="project.3/review.html">project.3</a></p>\n']

        assert_equals(expected_content, actual_content)
