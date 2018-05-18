from typing import Dict
from unittest.mock import patch

from nose.tools import assert_equals, assert_raises

from data.finding import Finding
from data.misuse import Location
from data.snippets import Snippet, SnippetUnavailableException
from tests.test_utils.data_util import create_misuse
from utils.shell import CommandFailedError


class TestPotentialHit:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.misuse = create_misuse('misuse', meta={"locations": {"file": "a", "method": "m()"}})
        self.snippets = []
        self.misuse.get_snippets = lambda *_: self.snippets

    def test_matches_on_file(self):
        self.misuse.locations[0].file = "some-class.java"
        self.assert_potential_hit({"file": "some-class.java"})

    def test_matches_on_file_absolute(self):
        self.misuse.locations[0].file = "java/main/some-class.java"
        self.assert_potential_hit({"file": "/some/prefix/java/main/some-class.java"})

    def test_matches_on_class(self):
        self.misuse.locations[0].file = "some-class.java"
        self.assert_potential_hit({"file": "some-class.class"})

    def test_matches_on_inner_class(self):
        self.misuse.locations[0].file = "some-class.java"
        self.assert_potential_hit({"file": "some-class$inner-class.class"})

    def test_differs_on_method(self):
        self.misuse.locations[0].method = "method()"
        self.assert_no_potential_hit({"method": "other_method()"})

    def test_differs_on_method_2(self):
        self.misuse.locations[0].method = "a_method()"
        self.assert_no_potential_hit({"method": "method()"})

    def test_matches_on_method_name(self):
        self.misuse.locations[0].method = "method(A, B)"
        self.assert_potential_hit({"method": "method"})

    def test_differs_on_method_name_prefix(self):
        self.misuse.locations[0].method = "appendX"
        self.assert_no_potential_hit({"method": "append"})

    def test_matches_on_method_signature(self):
        self.misuse.locations[0].method = "method(A, B)"
        self.assert_potential_hit({"method": "method(A, B)"})

    def test_matches_on_method_name_only(self):
        self.misuse.locations[0].method = "method(A)"
        self.assert_potential_hit({"method": "method(p.A)"}, True)

    def test_does_not_match_on_line_without_startline(self):
        self.misuse.locations[0].method = "method(A)"
        self.misuse.locations[0].line = 42
        self.assert_potential_hit({"method": "method(A)"})

    def test_matches_on_line(self):
        self.misuse.locations[0].method = "method(A)"
        self.misuse.locations[0].line = 40
        self.snippets = [Snippet("{\n-some-\n-code-\n}", self.misuse.locations[0].line)]
        self.assert_potential_hit({"method": "method(A)", "startline": 41})

    def test_no_line_match(self):
        self.misuse.locations[0].method = "method(A)"
        self.misuse.locations[0].line = 40
        self.snippets = [Snippet("{\n-some-\n-code-\n}", self.misuse.locations[0].line)]
        self.assert_no_potential_hit({"method": "method(A)", "startline": 1337})

    def test_only_matches_from_the_same_location(self):
        self.misuse._misuse__locations = [Location("b", "method(A)", -1), Location("a", "someMethod(B)", -1)]
        self.assert_no_potential_hit({"file": "a", "method": "method(A)"})

    def assert_potential_hit(self, finding_data: Dict[str, str], method_name_only: bool=False):
        finding = self.create_finding(finding_data)
        assert finding.is_potential_hit(self.misuse, [], method_name_only)

    def assert_no_potential_hit(self, finding_data: Dict[str, str]):
        finding = self.create_finding(finding_data)
        assert not finding.is_potential_hit(self.misuse, [])

    def create_finding(self, finding_data: Dict[str, str]):
        if "file" not in finding_data:
            finding_data["file"] = self.misuse.locations[0].file
        if "method" not in finding_data:
            finding_data["method"] = self.misuse.locations[0].method

        return Finding(finding_data)


@patch("data.snippets.exec_util")
class TestTargetCode:
    def test_no_code(self, utils_mock):
        utils_mock.return_value = ""

        finding = Finding({"file": "-file-"})

        with assert_raises(SnippetUnavailableException):
            finding.get_snippets(["/base"])

    def test_loads_snippet(self, utils_mock):
        utils_mock.side_effect = lambda tool, args:\
                "42:T:-code-" if tool == "MethodExtractor" and args == '"/base/-file-" "-method-"' else ""

        finding = Finding({"file": "-file-", "method": "-method-"})

        assert_equals([Snippet("class T {\n-code-\n}", 41)], finding.get_snippets(["/base"]))

    def test_loads_snippet_absolute_path(self, utils_mock):
        utils_mock.side_effect = lambda tool, args: \
            "42:T:-code-" if tool == "MethodExtractor" and args == '"/-absolute-file-" "-method-"' else ""

        finding = Finding({"file": "/-absolute-file-", "method": "-method-"})

        assert_equals(1, len(finding.get_snippets(["/base"])))

    def test_loads_multiple_snippets(self, utils_mock):
        utils_mock.return_value = "42:T:t-code\n===\n32:A:a-code"

        finding = Finding({"file": "-file-", "method": "-method-"})

        assert_equals(2, len(finding.get_snippets(["/base"])))

    def test_strips_additional_output(self, utils_mock):
        utils_mock.return_value = "Arbitrary additional output\n1:C:code"

        finding = Finding({"file": "-file-", "method": "-method-"})

        assert_equals(1, len(finding.get_snippets(["/base"])))

    def test_extraction_error(self, utils_mock):
        utils_mock.side_effect = CommandFailedError("cmd", "output")

        finding = Finding({"file": "-file-", "method": "-method-"})

        with assert_raises(SnippetUnavailableException):
            finding.get_snippets(["/base"])

    def test_filters_by_startline(self, utils_mock):
        utils_mock.return_value = "42:T:t-code\n===\n32:A:a\nb\nc\n===\n22:N:n-code"

        finding = Finding({"file": "-file-", "method": "-method-", "startline": 33})

        snippets = finding.get_snippets(["/base"])

        assert_equals([Snippet("class A {\na\nb\nc\n}", 31)], snippets)
