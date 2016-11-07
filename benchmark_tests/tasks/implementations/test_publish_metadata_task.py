from unittest.mock import patch

from nose.tools import assert_equals

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
            }
        }])
