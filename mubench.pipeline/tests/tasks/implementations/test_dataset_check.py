from unittest.mock import patch, MagicMock, ANY
from nose.tools import assert_equals

from tasks.implementations.dataset_check import DatasetCheck
from tests.test_utils.data_util import create_project, create_version, create_misuse


class TestDatasetCheckProject:
    def setup(self):
        self.uut = DatasetCheck()
        self.uut._missing_key = MagicMock()

    def test_missing_name(self):
        meta = {"repository": {"type": "git", "url": "https://github.com/stg-tud/MUBench.git"}}
        project = create_project("-id-", meta=meta)

        self.uut.process_project(project)

        self.uut._missing_key.assert_called_with("name", "-id-/project.yml")

    def test_missing_repository(self):
        meta = {"name": "-project-name-"}
        project = create_project("-id-", meta=meta)

        self.uut.process_project(project)

        self.uut._missing_key.assert_called_with("repository", "-id-/project.yml")

    def test_missing_repository_type(self):
        meta = {"name": "-project-name-", "repository": {"url": "https://github.com/stg-tud/MUBench.git"}}
        project = create_project("-id-", meta=meta)

        self.uut.process_project(project)

        self.uut._missing_key.assert_called_with("repository.type", "-id-/project.yml")

    def test_missing_repository_url(self):
        meta = {"name": "-project-name-", "repository": {"type": "git"}}
        project = create_project("-id-", meta=meta)

        self.uut.process_project(project)

        self.uut._missing_key.assert_called_with("repository.url", "-id-/project.yml")
