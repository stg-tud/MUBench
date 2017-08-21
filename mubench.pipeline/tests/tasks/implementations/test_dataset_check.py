from unittest.mock import patch, MagicMock, ANY
from nose.tools import assert_equals

from tasks.implementations.dataset_check import DatasetCheck
from tests.test_utils.data_util import create_project, create_version, create_misuse

EMPTY_META = {"empty": None}

class TestDatasetCheckProject:
    def setup(self):
        self.uut = DatasetCheck({}, '')
        self.uut._missing_key = MagicMock()
        self.uut._check_misuse_location_exists = MagicMock()

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

    def test_version_and_misuse_with_same_name(self):
        self.uut._version_misuse_conflict = MagicMock()
        project = create_project("-project-", meta=EMPTY_META)
        misuse = create_misuse("-conflict-", project=project, meta=EMPTY_META)
        version = create_version("-conflict-", project=project, misuses=[misuse], meta=EMPTY_META)

        self.uut.process_project(project)

        self.uut._version_misuse_conflict.assert_any_call("-project-", "-conflict-")


class TestDatasetCheckProjectVersion:
    def setup(self):
        self.uut = DatasetCheck({}, '')
        self.uut._missing_key = MagicMock()
        self.uut._check_misuse_location_exists = MagicMock()

    def test_missing_revision(self):
        meta = {"misuses": ["1"]}
        project = create_project("-project-", meta=EMPTY_META)
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("revision", "-project-/versions/-id-/version.yml")

    def test_missing_misuses(self):
        meta = {"revision": "1"}
        project = create_project("-project-", meta=EMPTY_META)
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("misuses", "-project-/versions/-id-/version.yml")

    def test_empty_misuses(self):
        meta = {"misuses": []}
        project = create_project("-project-", meta=EMPTY_META)
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("misuses", "-project-/versions/-id-/version.yml")

    def test_misuses_none(self):
        project = create_project("-project-", meta=EMPTY_META)
        version = create_version("-id-", meta={"misuses": None}, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("misuses", "-project-/versions/-id-/version.yml")

    def test_missing_build(self):
        meta = {"misuses": ["1"]}
        project = create_project("-project-", meta=EMPTY_META)
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("build", "-project-/versions/-id-/version.yml")

    def test_missing_build_classes(self):
        meta = {"build": {}}
        project = create_project("-project-", meta=EMPTY_META)
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("build.classes", "-project-/versions/-id-/version.yml")

    def test_missing_build_commands(self):
        meta = {"build": {}}
        project = create_project("-project-", meta=EMPTY_META)
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("build.commands", "-project-/versions/-id-/version.yml")

    def test_empty_build_commands(self):
        meta = {"build": {"commands": []}}
        project = create_project("-project-", meta=EMPTY_META)
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("build.commands", "-project-/versions/-id-/version.yml")


    def test_missing_build_src(self):
        meta = {"build": {}}
        project = create_project("-project-", meta=EMPTY_META)
        version = create_version("-id-", meta=meta, project=project)

        self.uut.process_project_version(project, version)

        self.uut._missing_key.assert_any_call("build.src", "-project-/versions/-id-/version.yml")


    def test_non_existent_misuse(self):
        self.uut._unknown_misuse = MagicMock()
        project = create_project("-project-")
        version = create_version("-id-", meta={"misuses": ["-misuse-"]}, project=project)
        version._MISUSES = []

        self.uut.process_project_version(project, version)

        self.uut._unknown_misuse.assert_any_call(version.id, "-misuse-")


class TestDatasetCheckMisuse:
    def setup(self):
        self.uut = DatasetCheck({}, '')
        self.uut._missing_key = MagicMock()
        self.uut._check_misuse_location_exists = MagicMock()

    def test_missing_location(self):
        project = create_project("-project-", meta=EMPTY_META)
        misuse = create_misuse("-id-", project=project, meta=EMPTY_META)
        misuse._YAML = EMPTY_META # needs to be set here, since create_misuse adds a location
        version = create_version("-version-", meta=EMPTY_META, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("location", "-project-/misuses/-id-/misuse.yml")

    def test_missing_location_file(self):
        meta = {"location": {}}
        project = create_project("-project-", meta=EMPTY_META)
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta=EMPTY_META, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("location.file", "-project-/misuses/-id-/misuse.yml")

    def test_missing_location_method(self):
        meta = {"location": {}}
        project = create_project("-project-", meta=EMPTY_META)
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta=EMPTY_META, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("location.method", "-project-/misuses/-id-/misuse.yml")

    def test_missing_api(self):
        project = create_project("-project-", meta=EMPTY_META)
        misuse = create_misuse("-id-", project=project, meta=EMPTY_META)
        version = create_version("-version-", meta=EMPTY_META, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("api", "-project-/misuses/-id-/misuse.yml")

    def test_missing_characteristics(self):
        project = create_project("-project-", meta=EMPTY_META)
        misuse = create_misuse("-id-", project=project, meta=EMPTY_META)
        version = create_version("-version-", meta=EMPTY_META, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("characteristics", "-project-/misuses/-id-/misuse.yml")

    def test_empty_characteristics(self):
        meta = {"characteristics": []}
        project = create_project("-project-", meta=EMPTY_META)
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta=EMPTY_META, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("characteristics", "-project-/misuses/-id-/misuse.yml")

    def test_missing_description(self):
        project = create_project("-project-", meta=EMPTY_META)
        misuse = create_misuse("-id-", project=project, meta=EMPTY_META)
        version = create_version("-version-", meta=EMPTY_META, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("description", "-project-/misuses/-id-/misuse.yml")

    def test_empty_description(self):
        meta = {"description": ''}
        project = create_project("-project-", meta=EMPTY_META)
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta=EMPTY_META, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("description", "-project-/misuses/-id-/misuse.yml")

    def test_missing_fix(self):
        project = create_project("-project-", meta=EMPTY_META)
        misuse = create_misuse("-id-", project=project, meta=EMPTY_META)
        version = create_version("-version-", meta=EMPTY_META, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("fix", "-project-/misuses/-id-/misuse.yml")

    def test_missing_fix_commit(self):
        meta = {"fix": {}}
        project = create_project("-project-", meta=EMPTY_META)
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta=EMPTY_META, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("fix.commit", "-project-/misuses/-id-/misuse.yml")

    def test_missing_fix_revision(self):
        meta = {"fix": {}}
        project = create_project("-project-", meta=EMPTY_META)
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta=EMPTY_META, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("fix.revision", "-project-/misuses/-id-/misuse.yml")

    def test_missing_internal(self):
        project = create_project("-project-", meta=EMPTY_META)
        misuse = create_misuse("-id-", project=project, meta=EMPTY_META)
        version = create_version("-version-", meta=EMPTY_META, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("internal", "-project-/misuses/-id-/misuse.yml")

    def test_missing_report(self):
        project = create_project("-project-", meta=EMPTY_META)
        misuse = create_misuse("-id-", project=project, meta=EMPTY_META)
        version = create_version("-version-", meta=EMPTY_META, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("report", "-project-/misuses/-id-/misuse.yml")

    def test_missing_source(self):
        project = create_project("-project-", meta=EMPTY_META)
        misuse = create_misuse("-id-", project=project, meta=EMPTY_META)
        version = create_version("-version-", meta=EMPTY_META, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("source", "-project-/misuses/-id-/misuse.yml")

    def test_missing_source_name(self):
        meta = {"source": {}}
        project = create_project("-project-", meta=EMPTY_META)
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta=EMPTY_META, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("source.name", "-project-/misuses/-id-/misuse.yml")

    def test_missing_source_url(self):
        meta = {"source": {}}
        project = create_project("-project-", meta=EMPTY_META)
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta=EMPTY_META, project=project, misuses=[misuse])

        self.uut.process_project_version_misuse(project, version, misuse)

        self.uut._missing_key.assert_any_call("source.url", "-project-/misuses/-id-/misuse.yml")


class TestDatasetCheckDatasetLists:
    def setup(self):
        self.uut = DatasetCheck({}, '')
        self.uut._unknown_dataset_entry = MagicMock()
        self.uut._check_misuse_location_exists = MagicMock()

    def test_unknown_entry(self):
        self.uut.datasets = {"-dataset-": ["-unknown-entry-"]}

        self.uut.end()

        self.uut._unknown_dataset_entry.assert_any_call("-dataset-", "-unknown-entry-")

    def test_no_warning_on_known_project(self):
        project = create_project("-project-", meta=EMPTY_META)
        self.uut.datasets = {"-dataset-": [project.id]}

        self.uut.process_project(project)
        self.uut.end()

        self.uut._unknown_dataset_entry.assert_not_called()

    def test_no_warning_on_known_version(self):
        project = create_project("-project-", meta=EMPTY_META)
        version = create_version("-version-", project=project, meta=EMPTY_META)
        self.uut.datasets = {"-dataset-": [version.id]}

        self.uut.process_project_version(project, version)
        self.uut.end()

        self.uut._unknown_dataset_entry.assert_not_called()

    def test_no_warning_on_known_misuse(self):
        project = create_project("-project-", meta=EMPTY_META)
        misuse = create_misuse("-misuse-", project=project, meta=EMPTY_META)
        version = create_version("-version-", project=project, misuses=[misuse], meta=EMPTY_META)
        self.uut.datasets = {"-dataset-": [misuse.id]}

        self.uut.process_project_version_misuse(project, version, misuse)
        self.uut.end()

        self.uut._unknown_dataset_entry.assert_not_called()


class TestDatasetCheckUnknownLocation:
    def setup(self):
        self.uut = DatasetCheck({}, '')
        self.uut._cannot_find_location = MagicMock()

        self.project = create_project("-project-", meta=EMPTY_META)

        misuse_meta = {"location": {"file": "-file-", "method": "-method-"}}
        self.misuse = create_misuse("-id-", project=self.project, meta=misuse_meta)

        version_meta = {"build": {"src": "-source_dir-"}}
        self.version = create_version("-version-", meta=version_meta, project=self.project, misuses=[self.misuse])
        checkout = MagicMock()
        checkout.exists = MagicMock(return_value=True)
        checkout.checkout_dir = "-checkout_dir-"
        self.version.get_checkout = MagicMock(return_value=checkout)

    def test_unknown_location(self):
        self.uut._location_exists = MagicMock(return_value=False)

        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        self.uut._location_exists.assert_called_once_with("-checkout_dir-/-source_dir-", "-file-", "-method-")
        self.uut._cannot_find_location.assert_called_once_with("Location(-file-, -method-)", "-project-/misuses/-id-/misuse.yml")

    def test_known_location(self):
        self.uut._location_exists = MagicMock(return_value=True)

        self.uut.process_project_version_misuse(self.project, self.version, self.misuse)

        self.uut._location_exists.assert_called_once_with("-checkout_dir-/-source_dir-", "-file-", "-method-")
        self.uut._cannot_find_location.assert_not_called()
