import ast
from os import chdir
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

from nose.tools import assert_equals, assert_in

from benchmark.data.pattern import Pattern
from benchmark.subprocesses.evaluate import Evaluation
from benchmark.utils.io import safe_write
from benchmark_tests.data.test_misuse import create_misuse
from benchmark_tests.test_utils.subprocess_util import run_on_misuse


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
        self.eval_result_file = 'result.csv'

        self.uut = Evaluation(self.results_path, self.file_detector_result, self.checkout_dir, self.eval_result_file)

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_compares_files_correctly(self):
        self.create_result('svn', 'file: some-class.java')
        run_on_misuse(self.uut, create_misuse('svn', {'fix': {'files': [{'name': 'some-class.java'}]}}))
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
        run_on_misuse(self.uut, create_misuse('git', {'misuse': {'usage': 'graph: >\n' +
                                                                          '  digraph some-method {\n' +
                                                                          '    0 [label="StrBuilder#this#getNullText"]\n' +
                                                                          '    1 [label="String#str#length"]\n' +
                                                                          '    0 -> 1\n' +
                                                                          '  }\n'},
                                                      'fix': {'revision': '', 'files': [{'name': 'some-class.java'}]}}))
        actual_result = self.uut.results[0]
        assert_equals(('git', 1), actual_result)

    def test_handles_patterns(self):
        self.create_result('git', 'file: pattern0.java\n')

        test_misuse = create_misuse('git', {'fix': {'files': [{'name': 'some-class.java'}]}})
        test_misuse._PATTERNS = {Pattern("", 'pattern.java')}

        run_on_misuse(self.uut, test_misuse)

        actual_result = self.uut.results[0]
        assert_equals(('git', 1), actual_result)

    def test_writes_results_on_teardown(self):
        self.uut.results = {('NoHit', 0), ('PotentialHit', 1)}

        self.uut.teardown()

        with open(join(self.results_path, self.eval_result_file), 'r') as actual_result_file:
            actual_content = actual_result_file.read().splitlines()

        assert_in("'NoHit', 0", actual_content)
        assert_in("'PotentialHit', 1", actual_content)
        assert_equals(2, len(actual_content))

    def test_output_format_is_parseable(self):
        test_result = ('Misuse', 0)
        self.uut.results = {test_result}

        self.uut.teardown()

        with open(join(self.results_path, self.eval_result_file), 'r') as actual_result_file:
            actual = actual_result_file.read().splitlines()[0]

        assert_equals(test_result, ast.literal_eval(actual))

    def create_result(self, misuse_name, content):
        safe_write(content, join(self.results_path, misuse_name, self.file_detector_result),
                   append=False)
