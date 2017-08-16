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

        self.uut._missing_key.assert_any_call("name", "-id-/project.yml")

    def test_missing_repository(self):
        meta = {"name": "-project-name-"}
        project = create_project("-id-", meta=meta)

        self.uut.process_project(project)

        self.uut._missing_key.assert_any_call("repository", "-id-/project.yml")

    def test_missing_repository_type(self):
        meta = {"name": "-project-name-", "repository": {"url": "https://github.com/stg-tud/MUBench.git"}}
        project = create_project("-id-", meta=meta)

        self.uut.process_project(project)

        self.uut._missing_key.assert_any_call("repository.type", "-id-/project.yml")

    def test_missing_repository_url(self):
        meta = {"name": "-project-name-", "repository": {"type": "git"}}
        project = create_project("-id-", meta=meta)

        self.uut.process_project(project)

        self.uut._missing_key.assert_any_call("repository.url", "-id-/project.yml")

class TestDatasetCheckProjectVersion:
    def setup(self):
        self.uut = DatasetCheck()
        self.uut._missing_key = MagicMock()

    def test_missing_revision(self):
        meta = {"misuses": ["1"]}
        project = create_project("-project-", meta={"empty": ''})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("revision", "-project-/-id-/version.yml")

    def test_missing_misuses(self):
        meta = {"revision": "1"}
        project = create_project("-project-", meta={"empty": ''})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("misuses", "-project-/-id-/version.yml")

    def test_missing_misuses(self):
        meta = {"misuses": []}
        project = create_project("-project-", meta={"empty": ''})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("misuses", "-project-/-id-/version.yml")

    def test_missing_build(self):
        meta = {"misuses": ["1"]}
        project = create_project("-project-", meta={"empty": ''})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("build", "-project-/-id-/version.yml")

    def test_missing_build_classes(self):
        meta = {"build": {}}
        project = create_project("-project-", meta={"empty": ''})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("build.classes", "-project-/-id-/version.yml")

    def test_missing_build_commands(self):
        meta = {"build": {}}
        project = create_project("-project-", meta={"empty": ''})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("build.commands", "-project-/-id-/version.yml")

    def test_empty_build_commands(self):
        meta = {"build": {"commands": []}}
        project = create_project("-project-", meta={"empty": ''})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("build.commands", "-project-/-id-/version.yml")


    def test_missing_build_src(self):
        meta = {"build": {}}
        project = create_project("-project-", meta={"empty": ''})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("build.src", "-project-/-id-/version.yml")
