from unittest.mock import MagicMock

from tasks.implementations.dataset_check_project import ProjectCheckTask
from tests.test_utils.data_util import create_project


class TestProjectCheckTask:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.uut = ProjectCheckTask()
        self.uut._report_missing_key = MagicMock()

    def test_missing_name(self):
        meta = {"repository": {"type": "git", "url": "https://github.com/stg-tud/MUBench.git"}}
        project = create_project("-id-", meta=meta)

        self.uut.run(project)

        self.uut._report_missing_key.assert_any_call("name", "-id-/project.yml")

    def test_missing_repository(self):
        meta = {"name": "-project-name-"}
        project = create_project("-id-", meta=meta)

        self.uut.run(project)

        self.uut._report_missing_key.assert_any_call("repository", "-id-/project.yml")

    def test_missing_repository_type(self):
        meta = {"name": "-project-name-", "repository": {"url": "https://github.com/stg-tud/MUBench.git"}}
        project = create_project("-id-", meta=meta)

        self.uut.run(project)

        self.uut._report_missing_key.assert_any_call("repository.type", "-id-/project.yml")

    def test_missing_repository_url(self):
        meta = {"name": "-project-name-", "repository": {"type": "git"}}
        project = create_project("-id-", meta=meta)

        self.uut.run(project)

        self.uut._report_missing_key.assert_any_call("repository.url", "-id-/project.yml")

    def test_synthetic_no_url(self):
        meta = {"name": "-project-name-", "repository": {"type": "synthetic"}}
        project = create_project("-id-", meta=meta)

        self.uut.run(project)

        self.uut._report_missing_key.assert_not_called()


