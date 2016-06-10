from os import chdir
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

from nose.tools import assert_equals
from benchmark.nosetests.test_misuse import TMisuse

from benchmark.evaluate import Evaluation
from benchmark.nosetests.test_utils.subprocess_util import run_on_misuse
from benchmark.utils.io import safe_write


# noinspection PyAttributeOutsideInit
class TestEvaluation:
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-result-evaluation-test_')

        chdir(self.temp_dir)

        self.data_path = join(self.temp_dir, 'data')
        self.checkout_dir = join(self.temp_dir, 'checkouts')
        self.results_path = join(self.temp_dir, 'results', 'test-detector')
        self.detector = 'test-detector'
        self.file_detector_result = 'findings.yml'

        self.uut = Evaluation(self.results_path, self.file_detector_result, self.checkout_dir)

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_compares_files_correctly(self):
        self.create_result('svn', 'file: some-class.java')
        run_on_misuse(self.uut, TMisuse('svn', {'fix': {'files': [{'name': 'some-class.java'}]}}))
        actual_result = self.uut.results[0]
        assert_equals(('svn', 1), actual_result)

    def test_compares_graphs_correctly(self):
        self.create_result('git',
                           'file: some-class.java\n' +
                           'graph: >\n' +
                           '  digraph some-method {\n' +
                           '    0 [label="StrBuilder#this#getNullText"]\n' +
                           '    1 [label="String#str#length"]\n' +
                           '    0 -> 1\n' +
                           '  }\n' +
                           '---\n' +
                           'file: other-class.java\n' +
                           '---\n' +
                           'graph: >\n' +
                           '  digraph graph {}\n')
        run_on_misuse(self.uut, TMisuse('git', {'misuse': {'usage': 'graph: >\n' +
                                                                    '  digraph some-method {\n' +
                                                                    '    0 [label="StrBuilder#this#getNullText"]\n' +
                                                                    '    1 [label="String#str#length"]\n' +
                                                                    '    0 -> 1\n' +
                                                                    '  }\n'},
                                                'fix': {'revision': '', 'files': [{'name': 'some-class.java'}]}}))
        actual_result = self.uut.results[0]
        assert_equals(('git', 1), actual_result)

    def create_result(self, misuse_name, content):
        safe_write(content, join(self.results_path, misuse_name, self.file_detector_result),
                   append=False)
