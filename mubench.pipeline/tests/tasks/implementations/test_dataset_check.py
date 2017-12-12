from os.path import join
from tempfile import mkdtemp
from unittest import SkipTest
from unittest.mock import call, MagicMock, patch

from data.misuse import Misuse
from data.project import Project
from tasks.implementations.dataset_check import ProjectCheckTask, VersionCheckTask, MisuseCheckTask
from tests.test_utils.data_util import create_project, create_version, create_misuse
from utils.io import remove_tree, create_file


class TestProjectCheckTask:
    def setup(self):
        self.uut = ProjectCheckTask()
        self.uut._report_missing_key = MagicMock()
        self.uut._check_misuse_location_exists = MagicMock()

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


class TestVersionCheckTask:
    def setup(self):
        self.uut = VersionCheckTask()
        self.uut._report_missing_key = MagicMock()
        self.uut._check_misuse_location_exists = MagicMock()

    def test_missing_revision(self):
        meta = {"misuses": ["1"]}
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.run(project, version)

        self.uut._report_missing_key.assert_any_call("revision", "-project-/versions/-id-/version.yml")

    def test_synthetic_no_revision(self):
        meta = {"misuses": ["1"]}
        project = create_project("-project-", meta={"repository": {"type": "synthetic"}})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.run(project, version)

        assert call("revision", "-project-/versions/-id-/version.yml") \
               not in self.uut._report_missing_key.call_args_list

    def test_missing_misuses(self):
        meta = {"revision": "1"}
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.run(project, version)

        self.uut._report_missing_key.assert_any_call("misuses", "-project-/versions/-id-/version.yml")

    def test_empty_misuses(self):
        meta = {"misuses": []}
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.run(project, version)

        self.uut._report_missing_key.assert_any_call("misuses", "-project-/versions/-id-/version.yml")

    def test_misuses_none(self):
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta={"misuses": None}, project=project)

        self.uut.run(project, version)

        self.uut._report_missing_key.assert_any_call("misuses", "-project-/versions/-id-/version.yml")

    def test_missing_build(self):
        meta = {"misuses": ["1"]}
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.run(project, version)

        self.uut._report_missing_key.assert_any_call("build", "-project-/versions/-id-/version.yml")

    def test_missing_build_classes(self):
        meta = {"build": {}}
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.run(project, version)

        self.uut._report_missing_key.assert_any_call("build.classes", "-project-/versions/-id-/version.yml")

    def test_missing_build_commands(self):
        meta = {"build": {}}
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.run(project, version)

        self.uut._report_missing_key.assert_any_call("build.commands", "-project-/versions/-id-/version.yml")

    def test_empty_build_commands(self):
        meta = {"build": {"commands": []}}
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.run(project, version)

        self.uut._report_missing_key.assert_any_call("build.commands", "-project-/versions/-id-/version.yml")

    def test_missing_build_src(self):
        meta = {"build": {}}
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.run(project, version)

        self.uut._report_missing_key.assert_any_call("build.src", "-project-/versions/-id-/version.yml")

    def test_non_existent_misuse(self):
        self.uut._report_unknown_misuse = MagicMock()
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta={"misuses": ["-misuse-"]}, project=project)
        version._MISUSES = []

        self.uut.run(project, version)

        self.uut._report_unknown_misuse.assert_any_call(version.id, "-misuse-")

    def test_existent_misuse(self):
        self.uut._report_unknown_misuse = MagicMock()
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta={"misuses": ["-misuse-"]}, project=project)

        project.path = mkdtemp(prefix="mubench_test-dataset-check_")
        try:
            misuse_yml_path = join(project.path, Project.MISUSES_DIR, "-misuse-", Misuse.MISUSE_FILE)
            create_file(misuse_yml_path)

            self.uut.run(project, version)

            self.uut._report_unknown_misuse.assert_not_called()
        finally:
            remove_tree(project.path)


@patch("tasks.implementations.dataset_check.MisuseCheckTask._get_all_misuses")
class TestMisuseCheckTask:
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench_test-dataset-check_')
        self.uut = MisuseCheckTask({}, self.temp_dir, self.temp_dir)
        self.uut._report_missing_key = MagicMock()
        self.uut._check_misuse_location_exists = MagicMock()

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_missing_location(self, _):
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta={})
        misuse._YAML = {}  # needs to be set here, since create_misuse adds a location
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("location", "-project-/misuses/-id-/misuse.yml")

    def test_missing_location_file(self, _):
        meta = {"location": {}}
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("location.file", "-project-/misuses/-id-/misuse.yml")

    def test_missing_location_method(self, _):
        meta = {"location": {}}
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("location.method", "-project-/misuses/-id-/misuse.yml")

    def test_missing_api(self, _):
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("api", "-project-/misuses/-id-/misuse.yml")

    def test_missing_characteristics(self, _):
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("characteristics", "-project-/misuses/-id-/misuse.yml")

    def test_empty_characteristics(self, _):
        meta = {"characteristics": []}
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("characteristics", "-project-/misuses/-id-/misuse.yml")

    def test_missing_description(self, _):
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("description", "-project-/misuses/-id-/misuse.yml")

    def test_empty_description(self, _):
        meta = {"description": ''}
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("description", "-project-/misuses/-id-/misuse.yml")

    def test_missing_fix(self, _):
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("fix", "-project-/misuses/-id-/misuse.yml")

    def test_missing_fix_commit(self, _):
        meta = {"fix": {}}
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("fix.commit", "-project-/misuses/-id-/misuse.yml")

    def test_missing_fix_revision(self, _):
        meta = {"fix": {}}
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("fix.revision", "-project-/misuses/-id-/misuse.yml")

    def test_synthetic_no_fix(self, _):
        project = create_project("-project-", meta={"repository": {"type": "synthetic"}})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        assert call("fix", "-project-/misuses/-id-/misuse.yml") \
               not in self.uut._report_missing_key.call_args_list

    def test_missing_internal(self, _):
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("internal", "-project-/misuses/-id-/misuse.yml")

    def test_synthetic_no_internal(self, _):
        project = create_project("-project-", meta={"repository": {"type": "synthetic"}})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        assert call("internal", "-project-/misuses/-id-/misuse.yml") \
               not in self.uut._report_missing_key.call_args_list

    def test_missing_report(self, _):
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("report", "-project-/misuses/-id-/misuse.yml")

    def test_synthetic_no_report(self, _):
        project = create_project("-project-", meta={"repository": {"type": "synthetic"}})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        assert call("report", "-project-/misuses/-id-/misuse.yml") \
               not in self.uut._report_missing_key.call_args_list

    def test_missing_source(self, _):
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("source", "-project-/misuses/-id-/misuse.yml")

    def test_missing_source_name(self, _):
        meta = {"source": {}}
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("source.name", "-project-/misuses/-id-/misuse.yml")

    def test_missing_source_url(self, _):
        meta = {"source": {}}
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("source.url", "-project-/misuses/-id-/misuse.yml")

    def test_synthetic_no_source(self, _):
        project = create_project("-project-", meta={"repository": {"type": "synthetic"}})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        assert call("source", "-project-/misuses/-id-/misuse.yml") \
               not in self.uut._report_missing_key.call_args_list

    def test_invalid_violation_type(self, _):
        meta = {"characteristics": ["invalid/violation_type"]}
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])
        self.uut._report_invalid_violation_type = MagicMock()

        self.uut.run(project, version, misuse)

        self.uut._report_invalid_violation_type.assert_any_call("invalid/violation_type",
                                                                "-project-/misuses/-id-/misuse.yml")

    def test_valid_violation_type(self, _):
        meta = {"characteristics": ["missing/condition/value_or_state"]}
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])
        self.uut._report_invalid_violation_type = MagicMock()

        self.uut.run(project, version, misuse)

        self.uut._report_invalid_violation_type.assert_not_called()


@patch("tasks.implementations.dataset_check.MisuseCheckTask._get_all_misuses")
@patch("tasks.implementations.dataset_check.MisuseCheckTask._report_unknown_dataset_entry")
class TestDatasetCheckDatasetLists:
    def test_unknown_entry(self, report_unknown_dataset_entry_mock, _):
        uut = MisuseCheckTask({"-dataset-": ["-unknown-.-unknown-.-unknown-"]}, '', '')

        uut.end()

        report_unknown_dataset_entry_mock.assert_any_call("-dataset-", "-unknown-.-unknown-.-unknown-")

    def test_no_warning_on_known_project_version_misuse(self, report_unknown_dataset_entry_mock, _):
        project = create_project("-project-", meta={})
        version = create_version("-version-", project=project)
        misuse = create_misuse("-misuse-", project=project, version=version)
        uut = MisuseCheckTask({"-dataset-": [misuse.id]}, '', '')

        uut.run(project, version, misuse)
        uut.end()

        report_unknown_dataset_entry_mock.assert_not_called()


class TestDatasetCheckUnknownLocation:
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench_test-dataset-check_')

        self.uut = MisuseCheckTask({}, self.temp_dir, self.temp_dir)
        self.uut._report_cannot_find_location = MagicMock()

        self.project = create_project("-project-", meta={})

        misuse_meta = {"location": {"file": "-file-", "method": "-method-"}}
        self.misuse = create_misuse("-id-", project=self.project, meta=misuse_meta)

        version_meta = {"build": {"src": "-source_dir-"}}
        self.version = create_version("-version-", meta=version_meta, project=self.project, misuses=[self.misuse])
        checkout = MagicMock()
        checkout.exists = MagicMock(return_value=True)
        checkout.checkout_dir = "-checkout_dir-"
        self.version.get_checkout = MagicMock(return_value=checkout)

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_unknown_location(self):
        self.uut._location_exists = MagicMock(return_value=False)

        self.uut.run(self.project, self.version, self.misuse)

        self.uut._location_exists.assert_called_once_with("-checkout_dir-/-source_dir-", "-file-", "-method-")
        self.uut._report_cannot_find_location.assert_called_once_with("Location(-file-, -method-)",
                                                                      "-project-/misuses/-id-/misuse.yml")

    def test_known_location(self):
        self.uut._location_exists = MagicMock(return_value=True)

        self.uut.run(self.project, self.version, self.misuse)

        self.uut._location_exists.assert_called_once_with("-checkout_dir-/-source_dir-", "-file-", "-method-")
        self.uut._report_cannot_find_location.assert_not_called()


@patch("tasks.implementations.dataset_check.MisuseCheckTask._report_misuse_not_listed")
@patch("tasks.implementations.dataset_check.MisuseCheckTask._get_all_misuses")
class TestDatasetCheckUnlistedMisuses:
    def test_misuse_not_listed_in_any_version(self, get_all_misuses_mock, report_misuse_not_listed_mock):
        get_all_misuses_mock.return_value = ["-project-.-misuse-"]
        uut = MisuseCheckTask({}, '', '')

        uut.end()

        report_misuse_not_listed_mock.assert_called_once_with("-project-.-misuse-")

    def test_listed_misuse_is_not_reported(self, get_all_misuses_mock, report_misuse_not_listed_mock):
        get_all_misuses_mock.return_value = ["-project-.-misuse-"]
        uut = MisuseCheckTask({}, '', '')

        project = create_project("-project-", meta={})
        misuse = create_misuse("-misuse-", project=project, meta={})
        version = create_version("-version-", project=project, misuses=[misuse], meta={})

        uut.run(project, version, misuse)
        uut.end()

        report_misuse_not_listed_mock.assert_not_called()
