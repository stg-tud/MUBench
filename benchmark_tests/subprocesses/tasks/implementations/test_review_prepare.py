import ast
import yaml
from os import chdir, remove
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp
from typing import Dict, List

from nose.tools import assert_equals, assert_in

from benchmark.data.misuse import Misuse
from benchmark.subprocesses.tasks.implementations.review_prepare import ReviewPrepare
from benchmark.utils.io import safe_write, create_file
from benchmark_tests.data.test_misuse import create_misuse
from benchmark_tests.test_utils.data_util import create_project, create_version


class TestReviewPrepare:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-result-evaluation-test_')

        chdir(self.temp_dir)

        self.data_path = join(self.temp_dir, 'data')
        self.checkout_dir = join(self.temp_dir, 'checkouts')
        self.results_path = join(self.temp_dir, 'results', 'test-detector')
        self.review_path = join(self.temp_dir, 'review', 'test-detector')
        self.detector = 'test-detector'
        self.eval_result_file = 'result.csv'

        self.uut = ReviewPrepare(self.results_path, self.review_path, self.checkout_dir, self.eval_result_file, False)

        self.project = create_project('project')
        self.version = create_version('version', project=self.project)
        self.misuse = create_misuse('misuse', meta={"location": {"file": "a", "method": "m()"}}, project=self.project)

        create_file('checkouts/project/version/original-src/a')

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_matches_on_file(self):
        create_file("checkouts/project/version/original-src/some-class.java")
        self.misuse.location.file = "some-class.java"
        self.create_result([{"file": "some-class.java"}])

        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        self.assert_potential_hit(self.misuse)

    def test_matches_on_file_absolute(self):
        create_file("checkouts/project/version/original-src/java/main/some-class.java", truncate=True)
        self.misuse.location.file = "/java/main/some-class.java"
        self.create_result([{"file": "/java/main/some-class.java"}])

        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        self.assert_potential_hit(self.misuse)

    def test_matches_on_class(self):
        create_file("checkouts/project/version/original-src/some-class.java")
        self.misuse.location.file = "some-class.java"
        self.create_result([{"file": "some-class.class"}])

        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        self.assert_potential_hit(self.misuse)

    def test_matches_on_inner_class(self):
        create_file("checkouts/project/version/original-src/some-class.java")
        self.misuse.location.file = "some-class.java"
        self.create_result([{"file": "some-class$inner-class.class"}])

        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        self.assert_potential_hit(self.misuse)

    def test_differs_on_method(self):
        self.misuse.location.method = "method()"
        self.create_result([{"method": "other_method()"}])

        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        self.assert_no_hit(self.misuse)

    def test_matches_on_method_name(self):
        self.misuse.location.method = "method(A, B)"
        self.create_result([{"method": "method"}])

        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        self.assert_potential_hit(self.misuse)

    def test_not_matches_on_method_name_prefix(self):
        self.misuse.location.method = "appendX"
        self.create_result([{"method": "append"}])

        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        self.assert_no_hit(self.misuse)

    def test_matches_on_method_signature(self):
        self.misuse.location.method = "method(A, B)"
        self.create_result([{"method": "method(A, B)"}])

        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        self.assert_potential_hit(self.misuse)

    def test_falls_back_to_method_name_if_no_match_on_signature(self):
        self.misuse.location.method = "method(A)"
        self.create_result([{"method": "method(p.A)"}])

        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        self.assert_potential_hit(self.misuse)

    def test_matches_only_on_signature_if_match_on_signature(self):
        self.misuse.location.method = "method(A)"
        self.create_result([{"method": "method(A)"}, {"method": "method(B)"}])

        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        self.assert_potential_hit(self.misuse)

    def test_writes_results_on_end(self):
        self.uut.results = {('NoHit', 0), ('PotentialHit', 1)}

        self.uut.end()

        with open(join(self.results_path, self.eval_result_file), 'r') as actual_result_file:
            actual_content = actual_result_file.read().splitlines()

        assert_in("'NoHit', 0", actual_content)
        assert_in("'PotentialHit', 1", actual_content)
        assert_equals(2, len(actual_content))

    def test_output_format_is_parseable(self):
        test_result = ('Misuse', 0)
        self.uut.results = {test_result}

        self.uut.end()

        with open(join(self.results_path, self.eval_result_file), 'r') as actual_result_file:
            actual = actual_result_file.read().splitlines()[0]

        assert_equals(test_result, ast.literal_eval(actual))

    def create_result(self, findings: List[Dict[str, str]]):
        result_path = join(self.results_path, self.project.id, self.version.version_id)
        safe_write("result: success", join(result_path, "result.yml"), append=False)

        for finding in findings:
            if "file" not in finding:
                finding["file"] = self.misuse.location.file
            if "method" not in finding:
                finding["method"] = self.misuse.location.method

        file = join(result_path, "findings.yml")
        create_file(file)
        with open(file, "w") as stream:
            return yaml.dump_all(findings, stream, default_flow_style=False)

    def assert_potential_hit(self, misuse: Misuse):
        assert_equals([(misuse.id, 1)], self.uut.results)

    def assert_no_hit(self, misuse: Misuse):
        assert_equals([(misuse.id, 0)], self.uut.results)
