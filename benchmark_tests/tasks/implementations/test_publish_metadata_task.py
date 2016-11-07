from unittest.mock import patch

from benchmark.tasks.implementations.publish_metadata_task import PublishMetadataTask
from benchmark_tests.test_utils.data_util import create_misuse, create_version, create_project


class TestPublishMetadataTask:

    @patch("benchmark.tasks.implementations.publish_metadata_task.post")
    def test_publishes_metadata(self, post_mock):
        project = create_project("-p-")
        misuse = create_misuse("-m-", meta={"description": "-description-"}, project=project)

        task = PublishMetadataTask("http://test.url")
        task.process_project_misuse(project, misuse)
        task.end()

        post_mock.assert_called_with("http://test.url/upload/metadata", [{
            "misuse": misuse.id,
        }])
