from os import makedirs
from os.path import join, exists
from tempfile import mkdtemp

from nose.tools import assert_equals

from benchmark.subprocesses.tasks.implementations.review.index_generators import project_index
from benchmark.utils.io import remove_tree
from benchmark_tests.test_utils.data_util import create_project


class TestProjectIndexGenerator:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-test-index-generator_')

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_creates_links_to_versions(self):
        project_folder = join(self.temp_dir, 'project')

        makedirs(join(project_folder, 'version1'))
        makedirs(join(project_folder, 'version2'))
        makedirs(join(project_folder, 'version3'))

        project_index.generate(project_folder, create_project('project'))

        index_file = join(project_folder, 'index.html')
        assert exists(index_file)

        with open(index_file) as file:
            actual_content = file.readlines()

        expected_content = ['<p><a href="version1/index.html">version1</a></p>\n',
                            '<p><a href="version2/index.html">version2</a></p>\n',
                            '<p><a href="version3/index.html">version3</a></p>\n']

        assert_equals(expected_content, actual_content)
