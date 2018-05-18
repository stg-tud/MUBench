from unittest.mock import patch

from nose.tools import assert_equals

from data.correct_usage import CorrectUsage
from data.snippets import Snippet
from tasks.implementations.publish_metadata import PublishMetadataTask
from tests.test_utils.data_util import create_misuse, create_project, create_version


@patch("data.misuse.get_snippets")
@patch("tasks.implementations.publish_metadata.post")
class TestPublishMetadataTask:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.project = create_project("-p-", meta={"repository": {"type": "synthetic"}})
        self.version = create_version("-v-", project=self.project, meta={"build": {"src": "", "classes": ""}})

    def test_publish_url(self, post_mock, snippets_mock):
        misuse = create_misuse("-m-", project=self.project, version=self.version)

        task = PublishMetadataTask("-checkouts-path-", "http://test.url")
        task.run(self.project, misuse)
        task.end()

        assert_equals(post_mock.call_args[0][0], "http://test.url/metadata")

    @patch("tasks.implementations.publish_metadata.getpass.getpass")
    def test_post_auth_prompt(self, pass_mock, post_mock, snippets_mock):
        misuse = create_misuse("-m-", project=self.project, version=self.version)
        pass_mock.return_value = "-password-"

        task = PublishMetadataTask("-checkouts-path-", "http://test.url", "-username-")
        task.run(self.project, misuse)
        task.end()

        assert_equals(post_mock.call_args[1]["username"], "-username-")
        assert_equals(post_mock.call_args[1]["password"], "-password-")

    @patch("tasks.implementations.publish_metadata.getpass.getpass")
    def test_post_auth_provided(self, pass_mock, post_mock, snippets_mock):
        misuse = create_misuse("-m-", project=self.project, version=self.version)
        pass_mock.side_effect = UserWarning("should skip prompt")

        task = PublishMetadataTask("-checkouts-path-", "http://test.url", "-username-", "-password-")
        task.run(self.project, misuse)
        task.end()

        assert_equals(post_mock.call_args[1]["username"], "-username-")
        assert_equals(post_mock.call_args[1]["password"], "-password-")

    def test_publishes_metadata(self, post_mock, snippets_mock):
        misuse = create_misuse("-m-", meta={
            "description": "-description-",
            "fix": {
                "description": "-fix-description-",
                "commit": "http://fake.diff/url"
            },
            "violations": [
                "-violation-1-",
                "-violation-2-"
            ],
            "locations": [
                {
                    "file": "/some/file.java",
                    "method": "-some.method()-"
                }
            ]
        }, project=self.project, version=self.version)
        snippets_mock.return_value = [Snippet("-code-", 42)]

        task = PublishMetadataTask("-checkouts-path-", "http://test.url")
        task.run(self.project, misuse)
        task.end()

        assert_equals(post_mock.call_args[0][1], [{
            "project": self.project.id,
            "version": "-v-",
            "misuse": "-m-",
            "description": "-description-",
            "fix": {
                "description": "-fix-description-",
                "diff-url": "http://fake.diff/url"
            },
            "violations": [
                "-violation-1-",
                "-violation-2-"
            ],
            "locations": [
                {
                    "file": "/some/file.java",
                    "method": "-some.method()-",
                    "line": -1
                }
            ],
            "target_snippets": [{"first_line_number": 42, "code": "-code-"}],
            "correct_usages": []
        }])

    @patch("tasks.implementations.publish_metadata.safe_read")
    def test_publishes_correct_usage_code(self, read_mock, post_mock, snippets_mock):
        correct_usage_code = "public class P1 {\n" \
            "  void m() { return; }\n" \
            "}"
        read_mock.return_value = correct_usage_code
        misuse = create_misuse("-m-", project=self.project, correct_usages=[CorrectUsage("/base/path", "P1.java")],
                               version=self.version)

        task = PublishMetadataTask("-checkouts-path-", "http://test.url")
        task.run(self.project, misuse)
        task.end()

        assert_equals(post_mock.call_args[0][1][0]["correct_usages"], [
            {"id": "P1", "snippet": {"code": correct_usage_code, "first_line": 1}}
        ])

    @patch("tasks.implementations.publish_metadata.safe_read")
    def test_publishes_correct_usage_code_without_preamble(self, read_mock, post_mock, snippets_mock):
        correct_usage_preamble = "package foo;\n" \
                       "import Bar;\n" \
                       "\n"
        correct_usage_code = "public class P1 {\n" \
                       "  void m() { return; }\n" \
                       "}"
        read_mock.return_value = correct_usage_preamble + correct_usage_code
        misuse = create_misuse("-m-", project=self.project, correct_usages=[CorrectUsage("/", "P1.java")], version=self.version)

        task = PublishMetadataTask("-checkouts-path-", "http://test.url")
        task.run(self.project, misuse)
        task.end()

        assert_equals(post_mock.call_args[0][1][0]["correct_usages"][0]["snippet"]["code"], correct_usage_code)

    @patch("tasks.implementations.publish_metadata.safe_read")
    def test_publishes_correct_usage_code_without_trailing_newlines(self, read_mock, post_mock, snippets_mock):
        correct_usage_code = "public class P1 {}"
        read_mock.return_value = correct_usage_code + "\n\n\n"
        misuse = create_misuse("-m-", project=self.project, correct_usages=[CorrectUsage("/", "P1.java")], version=self.version)

        task = PublishMetadataTask("-checkouts-path-", "http://test.url")
        task.run(self.project, misuse)
        task.end()

        assert_equals(post_mock.call_args[0][1][0]["correct_usages"][0]["snippet"]["code"], correct_usage_code)
