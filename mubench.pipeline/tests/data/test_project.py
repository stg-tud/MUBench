from os.path import join
from tempfile import mkdtemp

import yaml
from nose.tools import assert_equals

from data.project import Project
from utils.io import remove_tree, create_file, safe_open
from tests.test_utils.data_util import create_version


class TestProject:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-test-project_")

        self.project_id = "-project-"
        self.project_path = join(self.temp_dir, self.project_id)
        self.uut = Project(self.temp_dir, self.project_id)

    def mock_meta_data(self, meta):
        self.uut._YAML.update(meta)

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_rejects_non_project_path(self):
        assert not Project.is_project(self.temp_dir)

    def test_accepts_project_path(self):
        create_file(join(self.project_path, Project.PROJECT_FILE))
        assert Project.is_project(self.project_path)

    def test_reads_project_file(self):
        test_dict = {"name": "Project Name"}
        with safe_open(self.uut._project_file, 'w+') as stream:
            yaml.dump(test_dict, stream)

        assert_equals(test_dict, self.uut._yaml)

    def test_id(self):
        assert_equals(self.project_id, self.uut.id)

    def test_name(self):
        self.mock_meta_data({"name": "Project Name"})

        assert_equals("Project Name", self.uut.name)

    def test_repository_type(self):
        self.mock_meta_data({"repository": {"type": "git"}})

        assert_equals("git", self.uut.repository.vcstype)

    def test_repository_url(self):
        self.mock_meta_data({"repository": {"url": "http://git.org/repo.git"}})

        assert_equals("http://git.org/repo.git", self.uut.repository.url)

    def test_finds_versions(self):
        version = create_version("v1", project=self.uut)
        create_file(version._version_file)

        versions = self.uut.versions

        assert_equals([version], versions)
