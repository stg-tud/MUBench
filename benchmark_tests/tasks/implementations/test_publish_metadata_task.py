from unittest.mock import patch

from benchmark.tasks.implementations.publish_metadata_task import PublishMetadataTask
from benchmark_tests.test_utils.data_util import create_misuse, create_version, create_project


class TestPublishMetadataTask:

    @patch("benchmark.tasks.implementations.publish_metadata_task.post")
    def test_publishes_metadata(self, post_mock):
        project = create_project("-p-")
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
        }, project=project)

        task = PublishMetadataTask("http://test.url")
        task.process_project_misuse(project, misuse)
        task.end()

        post_mock.assert_called_with("http://test.url/upload/metadata", [{
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
