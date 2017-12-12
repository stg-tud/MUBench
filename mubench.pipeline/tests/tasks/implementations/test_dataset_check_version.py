from tempfile import mkdtemp
from unittest.mock import MagicMock, patch, call

from os.path import join

from data.misuse import Misuse
from data.project import Project
from tasks.implementations.dataset_check_version import VersionCheckTask
from tests.test_utils.data_util import create_project, create_version
from utils.io import create_file, remove_tree


@patch('tasks.implementations.dataset_check_version.Project.repository')
class TestVersionCheckTask:
    def setup(self):
        self.uut = VersionCheckTask()
        self.uut._report_missing_key = MagicMock()

    def test_missing_revision(self, _):
        meta = {"misuses": ["1"]}
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.run(project, version)

        self.uut._report_missing_key.assert_any_call("revision", "-project-/versions/-id-/version.yml")

    def test_synthetic_no_revision(self, repository_mock):
        meta = {"misuses": ["1"]}
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta=meta, project=project)
        repository_mock.vcstype = "synthetic"

        self.uut.run(project, version)

        assert call("revision", "-project-/versions/-id-/version.yml") \
               not in self.uut._report_missing_key.call_args_list

    def test_missing_misuses(self, _):
        meta = {"revision": "1"}
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.run(project, version)

        self.uut._report_missing_key.assert_any_call("misuses", "-project-/versions/-id-/version.yml")

    def test_empty_misuses(self, _):
        meta = {"misuses": []}
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.run(project, version)

        self.uut._report_missing_key.assert_any_call("misuses", "-project-/versions/-id-/version.yml")

    def test_misuses_none(self, _):
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta={"misuses": None}, project=project)

        self.uut.run(project, version)

        self.uut._report_missing_key.assert_any_call("misuses", "-project-/versions/-id-/version.yml")

    def test_missing_build(self, _):
        meta = {"misuses": ["1"]}
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.run(project, version)

        self.uut._report_missing_key.assert_any_call("build", "-project-/versions/-id-/version.yml")

    def test_missing_build_classes(self, _):
        meta = {"build": {}}
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.run(project, version)

        self.uut._report_missing_key.assert_any_call("build.classes", "-project-/versions/-id-/version.yml")

    def test_missing_build_commands(self, _):
        meta = {"build": {}}
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.run(project, version)

        self.uut._report_missing_key.assert_any_call("build.commands", "-project-/versions/-id-/version.yml")

    def test_empty_build_commands(self, _):
        meta = {"build": {"commands": []}}
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.run(project, version)

        self.uut._report_missing_key.assert_any_call("build.commands", "-project-/versions/-id-/version.yml")

    def test_missing_build_src(self, _):
        meta = {"build": {}}
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta=meta, project=project)

        self.uut.run(project, version)

        self.uut._report_missing_key.assert_any_call("build.src", "-project-/versions/-id-/version.yml")

    def test_non_existent_misuse(self, _):
        self.uut._report_unknown_misuse = MagicMock()
        project = create_project("-project-", meta={})
        version = create_version("-id-", meta={"misuses": ["-misuse-"]}, project=project)
        version._MISUSES = []

        self.uut.run(project, version)

        self.uut._report_unknown_misuse.assert_any_call(version.id, "-misuse-")

    def test_existent_misuse(self, _):
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


