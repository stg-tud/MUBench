from unittest.mock import patch

from nose.tools import assert_equals

from data.pattern import Pattern
from data.snippets import Snippet
from tasks.implementations.publish_metadata import PublishMetadataTask
from tests.test_utils.data_util import create_misuse, create_project, create_version


@patch("data.misuse.get_snippets")
@patch("tasks.implementations.publish_metadata.post")
class TestPublishMetadataTask:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.project = create_project("-p-")

    def test_publish_url(self, post_mock, snippets_mock):
        misuse = create_misuse("-m-", project=self.project)
        create_version("-v-", project=self.project, misuses=[misuse])

        task = PublishMetadataTask("-compiles-path-", "http://test.url")
        task.run(self.project, misuse)
        task.end()

        assert_equals(post_mock.call_args[0][0], "http://test.url/api/upload/metadata")

    @patch("tasks.implementations.publish_metadata.getpass.getpass")
    def test_post_auth_prompt(self, pass_mock, post_mock, snippets_mock):
        misuse = create_misuse("-m-", project=self.project)
        create_version("-v-", project=self.project, misuses=[misuse])
        pass_mock.return_value = "-password-"

        task = PublishMetadataTask("-compiles-path-", "http://test.url", "-username-")
        task.run(self.project, misuse)
        task.end()

        assert_equals(post_mock.call_args[1]["username"], "-username-")
        assert_equals(post_mock.call_args[1]["password"], "-password-")

    @patch("tasks.implementations.publish_metadata.getpass.getpass")
    def test_post_auth_provided(self, pass_mock, post_mock, snippets_mock):
        misuse = create_misuse("-m-", project=self.project)
        create_version("-v-", project=self.project, misuses=[misuse])
        pass_mock.side_effect = UserWarning("should skip prompt")

        task = PublishMetadataTask("-compiles-path-", "http://test.url", "-username-", "-password-")
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
            "characteristics": [
                "-violation-type-1-",
                "-violation-type-2-"
            ],
            "location": {
                "file": "/some/file.java",
                "method": "-some.method()-"
            }
        }, project=self.project)
        create_version("-v-", project=self.project, misuses=[misuse])
        snippets_mock.return_value = [Snippet("-code-", 42)]

        task = PublishMetadataTask("-compiles-path-", "http://test.url")
        task.run(self.project, misuse)
        task.end()

        assert_equals(post_mock.call_args[0][1], [{
            "project": self.project.id,
            "version": "-v-",
            "misuse": misuse.id,
            "description": "-description-",
            "fix": {
                "description": "-fix-description-",
                "diff-url": "http://fake.diff/url"
            },
            "violation_types": [
                "-violation-type-1-",
                "-violation-type-2-"
            ],
            "location": {
                "file": "/some/file.java",
                "method": "-some.method()-"
            },
            "target_snippets": [{"first_line_number": 42, "code": "-code-"}],
            "patterns": []
        }])

    @patch("tasks.implementations.publish_metadata.safe_read")
    def test_publishes_pattern_code(self, read_mock, post_mock, snippets_mock):
        pattern_code = "public class P1 {\n" \
            "  void m() { return; }\n" \
            "}"
        read_mock.return_value = pattern_code
        misuse = create_misuse("-m-", project=self.project, patterns=[Pattern("/base/path", "P1.java")])
        create_version("-v-", project=self.project, misuses=[misuse])

        task = PublishMetadataTask("-compiles-path-", "http://test.url")
        task.run(self.project, misuse)
        task.end()

        assert_equals(post_mock.call_args[0][1][0]["patterns"], [
            {"id": "P1", "snippet": {"code": pattern_code, "first_line": 1}}
        ])

    @patch("tasks.implementations.publish_metadata.safe_read")
    def test_publishes_pattern_code_without_preamble(self, read_mock, post_mock, snippets_mock):
        pattern_preamble = "package foo;\n" \
                       "import Bar;\n" \
                       "\n"
        pattern_code = "public class P1 {\n" \
                       "  void m() { return; }\n" \
                       "}"
        read_mock.return_value = pattern_preamble + pattern_code
        misuse = create_misuse("-m-", project=self.project, patterns=[Pattern("/", "P1.java")])
        create_version("-v-", project=self.project, misuses=[misuse])

        task = PublishMetadataTask("-compiles-path-", "http://test.url")
        task.run(self.project, misuse)
        task.end()

        assert_equals(post_mock.call_args[0][1][0]["patterns"][0]["snippet"]["code"], pattern_code)

    @patch("tasks.implementations.publish_metadata.safe_read")
    def test_publishes_pattern_code_without_trailing_newlines(self, read_mock, post_mock, snippets_mock):
        pattern_code = "public class P1 {}"
        read_mock.return_value = pattern_code + "\n\n\n"
        misuse = create_misuse("-m-", project=self.project, patterns=[Pattern("/", "P1.java")])
        create_version("-v-", project=self.project, misuses=[misuse])

        task = PublishMetadataTask("-compiles-path-", "http://test.url")
        task.run(self.project, misuse)
        task.end()

        assert_equals(post_mock.call_args[0][1][0]["patterns"][0]["snippet"]["code"], pattern_code)
