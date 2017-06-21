from typing import Dict
from unittest.mock import patch

from nose.tools import assert_equals, assert_raises

from data.snippets import Snippet, SnippetUnavailableException
from data.finding import Finding, UnsupportedTypeError
from utils.shell import CommandFailedError
from tests.test_utils.data_util import create_misuse


class TestPotentialHit:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.misuse = create_misuse('misuse', meta={"location": {"file": "a", "method": "m()"}})

    def test_matches_on_file(self):
        self.misuse.location.file = "some-class.java"
        self.assert_potential_hit({"file": "some-class.java"})

    def test_matches_on_file_absolute(self):
        self.misuse.location.file = "java/main/some-class.java"
        self.assert_potential_hit({"file": "/some/prefix/java/main/some-class.java"})

    def test_matches_on_class(self):
        self.misuse.location.file = "some-class.java"
        self.assert_potential_hit({"file": "some-class.class"})

    def test_matches_on_inner_class(self):
        self.misuse.location.file = "some-class.java"
        self.assert_potential_hit({"file": "some-class$inner-class.class"})

    def test_differs_on_method(self):
        self.misuse.location.method = "method()"
        self.assert_no_potential_hit({"method": "other_method()"})

    def test_differs_on_method_2(self):
        self.misuse.location.method = "a_method()"
        self.assert_no_potential_hit({"method": "method()"})

    def test_matches_on_method_name(self):
        self.misuse.location.method = "method(A, B)"
        self.assert_potential_hit({"method": "method"})

    def test_differs_on_method_name_prefix(self):
        self.misuse.location.method = "appendX"
        self.assert_no_potential_hit({"method": "append"})

    def test_matches_on_method_signature(self):
        self.misuse.location.method = "method(A, B)"
        self.assert_potential_hit({"method": "method(A, B)"})

    def test_matches_on_method_name_only(self):
        self.misuse.location.method = "method(A)"
        self.assert_potential_hit({"method": "method(p.A)"}, True)

    def assert_potential_hit(self, finding_data: Dict[str, str], method_name_only: bool=False):
        finding = self.create_finding(finding_data)
        assert finding.is_potential_hit(self.misuse, method_name_only)

    def assert_no_potential_hit(self, finding_data: Dict[str, str]):
        finding = self.create_finding(finding_data)
        assert not finding.is_potential_hit(self.misuse)

    def create_finding(self, finding_data: Dict[str, str]):
        if "file" not in finding_data:
            finding_data["file"] = self.misuse.location.file
        if "method" not in finding_data:
            finding_data["method"] = self.misuse.location.method

        return Finding(finding_data)


@patch("data.snippets.exec_util")
class TestTargetCode:
    def test_no_code(self, utils_mock):
        utils_mock.return_value = ""

        finding = Finding({"file": "-file-"})

        assert_equals(finding.get_snippets("/base"), [])

    def test_loads_snippet(self, utils_mock):
        utils_mock.side_effect = lambda tool, args:\
                "42:T:-code-" if tool == "MethodExtractor" and args == '"/base/-file-" "-method-"' else ""

        finding = Finding({"file": "-file-", "method": "-method-"})

        assert_equals([Snippet("class T {\n-code-\n}", 41)], finding.get_snippets("/base"))

    def test_loads_snippet_absolute_path(self, utils_mock):
        utils_mock.side_effect = lambda tool, args: \
            "42:T:-code-" if tool == "MethodExtractor" and args == '"/-absolute-file-" "-method-"' else ""

        finding = Finding({"file": "/-absolute-file-", "method": "-method-"})

        assert_equals(1, len(finding.get_snippets("/base")))

    def test_loads_multiple_snippets(self, utils_mock):
        utils_mock.return_value = "42:T:t-code\n===\n32:A:a-code"

        finding = Finding({"file": "-file-", "method": "-method-"})

        assert_equals(2, len(finding.get_snippets("/base")))

    def test_strips_additional_output(self, utils_mock):
        utils_mock.return_value = "Arbitrary additional output\n1:C:code"

        finding = Finding({"file": "-file-", "method": "-method-"})

        assert_equals(1, len(finding.get_snippets("/base")))

    def test_extraction_error(self, utils_mock):
        utils_mock.side_effect = CommandFailedError("cmd", "output")

        finding = Finding({"file": "-file-", "method": "-method-"})

        with assert_raises(SnippetUnavailableException) as context:
            finding.get_snippets("/base")

        assert_equals('/base/-file-', context.exception.file)
        assert_equals(utils_mock.side_effect, context.exception.exception)


class TestMarkdown:
    def setup(self):
        self.uut = Finding(dict())

    def test_raises_on_non_convertible(self):
        class SomeClass: pass
        self.uut["non-convertible"] = SomeClass
        assert_raises(UnsupportedTypeError, self.uut.with_markdown)

    def test_empty_list(self):
        self.uut["list"] = []
        actual = self.uut.with_markdown()
        expected = ""
        assert_equals(expected, actual["list"])

    def test_list(self):
        self.uut["list"] = ["hello", "world"]
        actual = self.uut.with_markdown()
        expected = "* hello\n* world"
        assert_equals(expected, actual["list"])

    def test_empty_dict(self):
        self.uut["dict"] = dict()
        actual = self.uut.with_markdown()
        expected = ""
        assert_equals(expected, actual["dict"])

    def test_dict(self):
        self.uut["dict"] = {"key": "value"}
        actual = self.uut.with_markdown()
        expected = "key: \nvalue"
        assert_equals(expected, actual["dict"])
