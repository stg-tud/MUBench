from os import makedirs
from os.path import join, exists
from tempfile import mkdtemp

from nose.tools import assert_equals

from benchmark.subprocesses.tasks.implementations.review.index_generators import version_index
from benchmark.utils.io import remove_tree
from benchmark_tests.test_utils.data_util import create_project, create_version


class TestIndexGenerator:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-test-index-generator_')

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_creates_links_to_review_files(self):
        version_findings_folder = join(self.temp_dir, 'version')

        makedirs(join(version_findings_folder, 'project.1'))
        makedirs(join(version_findings_folder, 'project.2'))
        makedirs(join(version_findings_folder, 'project.3'))

        version_index.generate(self.temp_dir, version_findings_folder, create_project('project'),
                               create_version('version'))

        index_file = join(self.temp_dir, 'index.html')
        assert exists(index_file)

        with open(index_file) as file:
            actual_content = file.readlines()

        expected_content = ['<p><a href="project.1/review.html">project.1</a></p>\n',
                            '<p><a href="project.2/review.html">project.2</a></p>\n',
                            '<p><a href="project.3/review.html">project.3</a></p>\n']

        assert_equals(sorted(expected_content), sorted(actual_content))
