from io import StringIO
from unittest.mock import patch

from nose.tools import assert_equals

from benchmark.data.pattern import Pattern
from benchmark.tasks.implementations.publish_metadata_task import PublishMetadataTask
from benchmark_tests.test_utils.data_util import create_misuse, create_project


@patch("benchmark.tasks.implementations.publish_metadata_task.post")
class TestPublishMetadataTask:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.project = create_project("-p-")

    def test_publish_url(self, post_mock):
        misuse = create_misuse("-m-")

        task = PublishMetadataTask("http://test.url")
        task.process_project_misuse(self.project, misuse)
        task.end()

        assert_equals(post_mock.call_args[0][0], "http://test.url/upload/metadata")

    def test_publishes_metadata(self, post_mock):
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

        task = PublishMetadataTask("http://test.url")
        task.process_project_misuse(self.project, misuse)
        task.end()

        assert_equals(post_mock.call_args[0][1], [{
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
            "patterns": []
        }])

    @patch("benchmark.tasks.implementations.publish_metadata_task.open")
    def test_publishes_pattern_code(self, open_mock, post_mock):
        pattern_code = "public class P1 {\n" \
            "  void m() { return; }\n" \
            "}"
        open_mock.return_value = StringIO(pattern_code)
        misuse = create_misuse("-m-", project=self.project, patterns=[Pattern("/base/path", "P1.java")])

        task = PublishMetadataTask("http://test.url")
        task.process_project_misuse(self.project, misuse)
        task.end()

        assert_equals(post_mock.call_args[0][1][0]["patterns"], [
            {"id": "P1", "snippet": {"code": pattern_code, "first_line": 1}}
        ])

    @patch("benchmark.tasks.implementations.publish_metadata_task.open")
    def test_publishes_pattern_code_without_preamble(self, open_mock, post_mock):
        pattern_preamble = "package foo;\n" \
                       "import Bar;\n" \
                       "\n"
        pattern_code = "public class P1 {\n" \
                       "  void m() { return; }\n" \
                       "}"
        open_mock.return_value = StringIO(pattern_preamble + pattern_code)
        misuse = create_misuse("-m-", project=self.project, patterns=[Pattern("/", "P1.java")])

        task = PublishMetadataTask("http://test.url")
        task.process_project_misuse(self.project, misuse)
        task.end()

        assert_equals(post_mock.call_args[0][1][0]["patterns"][0]["snippet"]["code"], pattern_code)

    @patch("benchmark.tasks.implementations.publish_metadata_task.open")
    def test_publishes_pattern_code_without_trailing_newlines(self, open_mock, post_mock):
        pattern_code = "public class P1 {}"
        open_mock.return_value = StringIO(pattern_code + "\n\n\n")
        misuse = create_misuse("-m-", project=self.project, patterns=[Pattern("/", "P1.java")])

        task = PublishMetadataTask("http://test.url")
        task.process_project_misuse(self.project, misuse)
        task.end()

        assert_equals(post_mock.call_args[0][1][0]["patterns"][0]["snippet"]["code"], pattern_code)
