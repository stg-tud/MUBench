from unittest.mock import call, MagicMock, patch

from nose.tools import assert_equals

from tasks.implementations.dataset_check_misuse import MisuseCheckTask
from tests.test_utils.data_util import create_project, create_version, create_misuse


@patch('tasks.implementations.dataset_check_misuse.MisuseCheckTask._check_misuse_location_exists')
@patch('tasks.implementations.dataset_check_misuse.Project.repository')
class TestMisuseCheckTask:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.patcher = patch('tasks.implementations.dataset_check_misuse._get_all_misuses', return_value=[])
        self.get_all_misuses_mock = self.patcher.start()

        self.uut = MisuseCheckTask({}, '', '')
        self.uut._report_missing_key = MagicMock()

    def teardown(self):
        self.patcher.stop()

    def test_missing_location(self, _, __):
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta={})
        misuse._YAML = {}  # needs to be set here, since create_misuse adds a location
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("location", "-project-/misuses/-id-/misuse.yml")

    def test_missing_location_file(self, _, __):
        meta = {"location": {}}
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("location.file", "-project-/misuses/-id-/misuse.yml")

    def test_missing_location_method(self, _, __):
        meta = {"location": {}}
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("location.method", "-project-/misuses/-id-/misuse.yml")

    def test_missing_api(self, _, __):
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("api", "-project-/misuses/-id-/misuse.yml")

    def test_missing_characteristics(self, _, __):
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("characteristics", "-project-/misuses/-id-/misuse.yml")

    def test_empty_characteristics(self, _, __):
        meta = {"characteristics": []}
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("characteristics", "-project-/misuses/-id-/misuse.yml")

    def test_missing_description(self, _, __):
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("description", "-project-/misuses/-id-/misuse.yml")

    def test_empty_description(self, _, __):
        meta = {"description": ''}
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("description", "-project-/misuses/-id-/misuse.yml")

    def test_missing_fix(self, _, __):
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("fix", "-project-/misuses/-id-/misuse.yml")

    def test_missing_fix_commit(self, _, __):
        meta = {"fix": {}}
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("fix.commit", "-project-/misuses/-id-/misuse.yml")

    def test_missing_fix_revision(self, _, __):
        meta = {"fix": {}}
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("fix.revision", "-project-/misuses/-id-/misuse.yml")

    def test_synthetic_no_fix(self, repository_mock, __):
        project = create_project("-project-", meta={"repository": {"type": "synthetic"}})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])
        repository_mock.vcstype = 'synthetic'

        self.uut.run(project, version, misuse)

        assert call("fix", "-project-/misuses/-id-/misuse.yml") \
               not in self.uut._report_missing_key.call_args_list

    def test_missing_internal(self, _, __):
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("internal", "-project-/misuses/-id-/misuse.yml")

    def test_synthetic_no_internal(self, repository_mock, __):
        project = create_project("-project-", meta={"repository": {"type": "synthetic"}})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])
        repository_mock.vcstype = 'synthetic'

        self.uut.run(project, version, misuse)

        assert call("internal", "-project-/misuses/-id-/misuse.yml") \
               not in self.uut._report_missing_key.call_args_list

    def test_missing_report(self, _, __):
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("report", "-project-/misuses/-id-/misuse.yml")

    def test_synthetic_no_report(self, repository_mock, __):
        project = create_project("-project-", meta={"repository": {"type": "synthetic"}})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])
        repository_mock.vcstype = 'synthetic'

        self.uut.run(project, version, misuse)

        assert call("report", "-project-/misuses/-id-/misuse.yml") \
               not in self.uut._report_missing_key.call_args_list

    def test_missing_source(self, _, __):
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("source", "-project-/misuses/-id-/misuse.yml")

    def test_missing_source_name(self, _, __):
        meta = {"source": {}}
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("source.name", "-project-/misuses/-id-/misuse.yml")

    def test_missing_source_url(self, _, __):
        meta = {"source": {}}
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])

        self.uut.run(project, version, misuse)

        self.uut._report_missing_key.assert_any_call("source.url", "-project-/misuses/-id-/misuse.yml")

    def test_synthetic_no_source(self, repository_mock, __):
        project = create_project("-project-", meta={"repository": {"type": "synthetic"}})
        misuse = create_misuse("-id-", project=project, meta={})
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])
        repository_mock.vcstype = 'synthetic'

        self.uut.run(project, version, misuse)

        assert call("source", "-project-/misuses/-id-/misuse.yml") \
               not in self.uut._report_missing_key.call_args_list

    def test_invalid_violation_type(self, _, __):
        meta = {"characteristics": ["invalid/violation_type"]}
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])
        self.uut._report_invalid_violation_type = MagicMock()

        self.uut.run(project, version, misuse)

        self.uut._report_invalid_violation_type.assert_any_call("invalid/violation_type",
                                                                "-project-/misuses/-id-/misuse.yml")

    def test_valid_violation_type(self, _, __):
        meta = {"characteristics": ["missing/condition/value_or_state"]}
        project = create_project("-project-", meta={})
        misuse = create_misuse("-id-", project=project, meta=meta)
        version = create_version("-version-", meta={}, project=project, misuses=[misuse])
        self.uut._report_invalid_violation_type = MagicMock()

        self.uut.run(project, version, misuse)

        self.uut._report_invalid_violation_type.assert_not_called()

    @patch("tasks.implementations.dataset_check_misuse.MisuseCheckTask._report_unknown_dataset_entry")
    def test_unknown_entry(self, report_unknown_dataset_entry_mock, _, __):
        uut = MisuseCheckTask({"-dataset-": ["-unknown-.-unknown-.-unknown-"]}, '', '')

        uut.end()

        report_unknown_dataset_entry_mock.assert_any_call("-dataset-", "-unknown-.-unknown-.-unknown-")

    @patch("tasks.implementations.dataset_check_misuse.MisuseCheckTask._report_unknown_dataset_entry")
    def test_no_warning_on_known_project_version_misuse(self, report_unknown_dataset_entry_mock, _, __):
        project = create_project("-project-", meta={})
        version = create_version("-version-", project=project)
        misuse = create_misuse("-misuse-", project=project, version=version)
        uut = MisuseCheckTask({"-dataset-": [misuse.id]}, '', '')

        uut.run(project, version, misuse)
        uut.end()

        report_unknown_dataset_entry_mock.assert_not_called()

    @patch("tasks.implementations.dataset_check_misuse.MisuseCheckTask._report_misuse_not_listed")
    def test_misuse_not_listed_in_any_version(self, report_misuse_not_listed_mock, _, __):
        self.get_all_misuses_mock.return_value = ["-project-.-misuse-"]
        uut = MisuseCheckTask({}, '', '')

        uut.end()

        report_misuse_not_listed_mock.assert_called_once_with("-project-.-misuse-")

    @patch("tasks.implementations.dataset_check_misuse.MisuseCheckTask._report_misuse_not_listed")
    def test_listed_misuse_is_not_reported(self, report_misuse_not_listed_mock, get_all_misuses_mock, _):
        get_all_misuses_mock.return_value = ["-project-.-misuse-"]
        uut = MisuseCheckTask({}, '', '')

        project = create_project("-project-", meta={})
        misuse = create_misuse("-misuse-", project=project, meta={})
        version = create_version("-version-", project=project, misuses=[misuse], meta={})

        uut.run(project, version, misuse)
        uut.end()

        report_misuse_not_listed_mock.assert_not_called()

    @patch("tasks.implementations.dataset_check_misuse.MisuseCheckTask._report_invalid_dataset_entry")
    def test_reports_non_fully_specified_dataset_entry(self, report_invalid_dataset_entry_mock, _, __):
        MisuseCheckTask({'-dataset-': ['-project-.-misuse-']}, '', '')
        report_invalid_dataset_entry_mock.assert_called_with('-dataset-', '-project-.-misuse-')

    @patch("tasks.implementations.dataset_check_misuse.MisuseCheckTask._report_invalid_dataset_entry")
    def test_removes_non_fully_specified_dataset_entries(self, report_invalid_dataset_entry_mock, _, __):
        uut = MisuseCheckTask({'-dataset-': ['-project-.-misuse-']}, '', '')
        assert_equals({'-dataset-': []}, uut.datasets)


@patch('tasks.implementations.dataset_check_misuse.Project.repository')
@patch('tasks.implementations.dataset_check_misuse._get_all_misuses')
class TestDatasetCheckMisuseLocation:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        version_meta = {"build": {"src": "-source_dir-"}}
        self.project = create_project("-project-")
        self.version = create_version("-version-", meta=version_meta, project=self.project)
        self.misuse = create_misuse("-misuse-", version=self.version)
        checkout = MagicMock()
        checkout.exists = MagicMock(return_value=True)
        checkout.base_path = "-checkout_dir-"
        self.version.get_checkout = MagicMock(return_value=checkout)

    def test_unknown_location(self, _, __):
        uut = MisuseCheckTask({}, '', '')
        uut._location_exists = MagicMock(return_value=False)
        uut._report_cannot_find_location = MagicMock()

        uut.run(self.project, self.version, self.misuse)

        uut._location_exists.assert_called_once_with(["-checkout_dir-/-source_dir-"], "-dummy-/-file-", "-method-()")
        uut._report_cannot_find_location.assert_called_once_with("Location(-dummy-/-file-, -method-())",
                                                                 "-project-/misuses/-misuse-/misuse.yml")

    def test_known_location(self, _, __):
        uut = MisuseCheckTask({}, '', '')
        uut._location_exists = MagicMock(return_value=True)
        uut._report_cannot_find_location = MagicMock()

        uut.run(self.project, self.version, self.misuse)

        uut._location_exists.assert_called_once_with(["-checkout_dir-/-source_dir-"], "-dummy-/-file-", "-method-()")
        uut._report_cannot_find_location.assert_not_called()
