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

        self.uut._missing_key.assert_any_call("revision", "-project-/versions/-id-/version.yml")

    def test_missing_misuses(self):
        meta = {"revision": "1"}
        project = create_project("-project-", meta={"empty": ''})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("misuses", "-project-/versions/-id-/version.yml")

    def test_empty_misuses(self):
        meta = {"misuses": []}
        project = create_project("-project-", meta={"empty": ''})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("misuses", "-project-/versions/-id-/version.yml")

    def test_missing_build(self):
        meta = {"misuses": ["1"]}
        project = create_project("-project-", meta={"empty": ''})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("build", "-project-/versions/-id-/version.yml")

    def test_missing_build_classes(self):
        meta = {"build": {}}
        project = create_project("-project-", meta={"empty": ''})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("build.classes", "-project-/versions/-id-/version.yml")

    def test_missing_build_commands(self):
        meta = {"build": {}}
        project = create_project("-project-", meta={"empty": ''})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("build.commands", "-project-/versions/-id-/version.yml")

    def test_empty_build_commands(self):
        meta = {"build": {"commands": []}}
        project = create_project("-project-", meta={"empty": ''})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("build.commands", "-project-/versions/-id-/version.yml")


    def test_missing_build_src(self):
        meta = {"build": {}}
        project = create_project("-project-", meta={"empty": ''})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("build.src", "-project-/versions/-id-/version.yml")

class TestDatasetCheckMisuse:
    def setup(self):
        self.uut = DatasetCheck()
        self.uut._missing_key = MagicMock()

    def test_missing_location(self):
        meta = {"empty": ''}
        project = create_project("-project-", meta={"empty": ''})
        misuse = create_misuse("-id-", project=project)
        misuse._YAML = meta
        version = create_version("-version-", meta={"empty": ''}, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("location", "-project-/misuses/-id-/misuse.yml")

    def test_missing_location_file(self):
        meta = {"location": {}}
        project = create_project("-project-", meta={"empty": ''})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={"empty": ''}, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("location.file", "-project-/misuses/-id-/misuse.yml")

    def test_missing_location_method(self):
        meta = {"location": {}}
        project = create_project("-project-", meta={"empty": ''})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={"empty": ''}, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("location.method", "-project-/misuses/-id-/misuse.yml")

    def test_missing_api(self):
        meta = {"empty": {}}
        project = create_project("-project-", meta={"empty": ''})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={"empty": ''}, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("api", "-project-/misuses/-id-/misuse.yml")

    def test_missing_characteristics(self):
        meta = {"empty": ''}
        project = create_project("-project-", meta={"empty": ''})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={"empty": ''}, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("characteristics", "-project-/misuses/-id-/misuse.yml")

    def test_empty_characteristics(self):
        meta = {"characteristics": []}
        project = create_project("-project-", meta={"empty": ''})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={"empty": ''}, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("characteristics", "-project-/misuses/-id-/misuse.yml")

    def test_missing_description(self):
        meta = {"empty": ''}
        project = create_project("-project-", meta={"empty": ''})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={"empty": ''}, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("description", "-project-/misuses/-id-/misuse.yml")

    def test_empty_description(self):
        meta = {"description": ''}
        project = create_project("-project-", meta={"empty": ''})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={"empty": ''}, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("description", "-project-/misuses/-id-/misuse.yml")

    def test_missing_fix(self):
        meta = {"empty": ''}
        project = create_project("-project-", meta={"empty": ''})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={"empty": ''}, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("fix", "-project-/misuses/-id-/misuse.yml")

    def test_missing_fix_commit(self):
        meta = {"fix": {}}
        project = create_project("-project-", meta={"empty": ''})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={"empty": ''}, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("fix.commit", "-project-/misuses/-id-/misuse.yml")

    def test_missing_fix_revision(self):
        meta = {"fix": {}}
        project = create_project("-project-", meta={"empty": ''})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={"empty": ''}, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("fix.revision", "-project-/misuses/-id-/misuse.yml")

    def test_missing_internal(self):
        meta = {"empty": ''}
        project = create_project("-project-", meta={"empty": ''})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={"empty": ''}, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("internal", "-project-/misuses/-id-/misuse.yml")

    def test_missing_report(self):
        meta = {"empty": ''}
        project = create_project("-project-", meta={"empty": ''})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={"empty": ''}, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("report", "-project-/misuses/-id-/misuse.yml")

    def test_missing_source(self):
        meta = {"empty": ''}
        project = create_project("-project-", meta={"empty": ''})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={"empty": ''}, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("source", "-project-/misuses/-id-/misuse.yml")

    def test_missing_source_name(self):
        meta = {"source": {}}
        project = create_project("-project-", meta={"empty": ''})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={"empty": ''}, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("source.name", "-project-/misuses/-id-/misuse.yml")

    def test_missing_source_url(self):
        meta = {"source": {}}
        project = create_project("-project-", meta={"empty": ''})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={"empty": ''}, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("source.url", "-project-/misuses/-id-/misuse.yml")
