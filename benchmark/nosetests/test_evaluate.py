from os import chdir
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

from nose.tools import assert_equals

from benchmark.evaluate import Evaluation
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
        self.file_detector_result = 'findings.yaml'

        self.uut = Evaluation(self.results_path, self.detector,
                              self.file_detector_result, self.checkout_dir)

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_compares_files_correctly(self):
        self.create_result('svn', 'file: some-class.java')
        self.uut.evaluate('svn.yml', {'fix': {'files': [{'name': 'some-class.java'}]}})
        actual_result = self.uut.results[0]
        assert_equals(('svn.yml', 1), actual_result)

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
        self.uut.evaluate('git.yml', {'misuse': {'usage': 'graph: >\n' +
                                                          '  digraph some-method {\n' +
                                                          '    0 [label="StrBuilder#this#getNullText"]\n' +
                                                          '    1 [label="String#str#length"]\n' +
                                                          '    0 -> 1\n' +
                                                          '  }\n'},
                                      'fix': {'revision': '', 'files': [{'name': 'some-class.java'}]}})
        actual_result = self.uut.results[0]
        assert_equals(('git.yml', 1), actual_result)

    def create_result(self, misuse_name, content):
        safe_write(content, join(self.results_path, misuse_name, self.file_detector_result),
                   append=False)
