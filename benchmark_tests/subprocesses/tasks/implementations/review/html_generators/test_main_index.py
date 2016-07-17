from os import makedirs
from tempfile import mkdtemp

from os.path import join, exists

from nose.tools import assert_equals

from benchmark.subprocesses.tasks.implementations.review.html_generators import main_index
from benchmark.utils.io import remove_tree


class TestMainIndexGenerator:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-test-index-generator_')

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_creates_links_to_detectors(self):
        findings_folder = join(self.temp_dir, 'findings')

        makedirs(join(findings_folder, 'detector1'))
        makedirs(join(findings_folder, 'detector2'))
        makedirs(join(findings_folder, 'detector3'))

        main_index.generate(self.temp_dir, findings_folder)

        index_file = join(self.temp_dir, 'index.html')
        assert exists(index_file)

        with open(index_file) as file:
            actual_content = file.readlines()

        expected_content = ['<p><a href="detector1/index.html">detector1</a></p>\n',
                            '<p><a href="detector2/index.html">detector2</a></p>\n',
                            '<p><a href="detector3/index.html">detector3</a></p>\n']

        assert_equals(sorted(expected_content), sorted(actual_content))
