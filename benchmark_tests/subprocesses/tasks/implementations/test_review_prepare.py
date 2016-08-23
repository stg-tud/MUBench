import ast
from os.path import join
from typing import Dict, List

from nose.tools import assert_equals, assert_in

from benchmark.data.misuse import Misuse
from benchmark.subprocesses.tasks.implementations.review_prepare import ReviewPrepare
from benchmark_tests.data.test_misuse import create_misuse
from benchmark_tests.test_utils.data_util import create_project, create_version


class TestFindPotentialMatches:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.misuse = create_misuse('misuse', meta={"location": {"file": "a", "method": "m()"}})

    def test_matches_on_file(self):
        self.misuse.location.file = "some-class.java"
        self.assert_potential_hit([{"file": "some-class.java"}])

    def test_matches_on_file_absolute(self):
        self.misuse.location.file = "java/main/some-class.java"
        self.assert_potential_hit([{"file": "/some/prefix/java/main/some-class.java"}])

    def test_matches_on_class(self):
        self.misuse.location.file = "some-class.java"
        self.assert_potential_hit([{"file": "some-class.class"}])

    def test_matches_on_inner_class(self):
        self.misuse.location.file = "some-class.java"
        self.assert_potential_hit([{"file": "some-class$inner-class.class"}])

    def test_differs_on_method(self):
        self.misuse.location.method = "method()"
        self.assert_no_potential_hit([{"method": "other_method()"}])

    def test_matches_on_method_name(self):
        self.misuse.location.method = "method(A, B)"
        self.assert_potential_hit([{"method": "method"}])

    def test_differs_on_method_name_prefix(self):
        self.misuse.location.method = "appendX"
        self.assert_no_potential_hit([{"method": "append"}])

    def test_matches_on_method_signature(self):
        self.misuse.location.method = "method(A, B)"
        self.assert_potential_hit([{"method": "method(A, B)"}])

    def test_falls_back_to_method_name_if_no_match_on_signature(self):
        self.misuse.location.method = "method(A)"
        self.assert_potential_hit([{"method": "method(p.A)"}])

    def test_matches_only_on_signature_if_match_on_signature(self):
        self.misuse.location.method = "method(A)"
        self.assert_potential_hit([{"method": "method(A)"}, {"method": "method(B)"}])

    def test_matches_constructor(self):
        self.misuse.location.method = "A()"
        self.assert_potential_hit([{"method": "<init>()"}])

    def create_findings(self, findings: List[Dict[str, str]]):
        for finding in findings:
            if "file" not in finding:
                finding["file"] = self.misuse.location.file
            if "method" not in finding:
                finding["method"] = self.misuse.location.method
        return findings

    def assert_potential_hit(self, findings):
        assert ReviewPrepare.find_potential_hits(self.create_findings(findings), self.misuse)

    def assert_no_potential_hit(self, findings):
        assert not ReviewPrepare.find_potential_hits(self.create_findings(findings), self.misuse)
