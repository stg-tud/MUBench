from os.path import join
from tempfile import mkdtemp

import yaml
from nose.tools import assert_equals, assert_raises

from benchmark.data.project import Project
from benchmark.data.project_checkout import LocalProjectCheckout, GitProjectCheckout, SVNProjectCheckout
from benchmark.data.project_version import ProjectVersion
from benchmark.utils.io import remove_tree, create_file, safe_open
from benchmark_tests.test_utils.data_util import create_project


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

    def test_derives_compile_base_path(self):
        project_compile = self.uut.get_compile(ProjectVersion("version"), "/base/path")

        assert_equals(join("/base/path", self.project_id, "version"), project_compile.base_path)

    def test_finds_versions(self):
        version = ProjectVersion(join(self.uut._path, "versions", "v1"))
        create_file(version._version_file)

        versions = self.uut.versions

        assert_equals([version], versions)


class TestProjectCheckout:
    def test_synthetic_project(self):
        uut = create_project("-project-", yaml={"repository": {"type": "synthetic"}})
        version = ProjectVersion("")

        checkout = uut.get_checkout(version, ":base_path:")

        assert isinstance(checkout, LocalProjectCheckout)
        assert_equals(join(uut._path, "versions", "0", "compile"), checkout.url)
        assert_equals("-project-", checkout.name)

    def test_git_project(self):
        uut = create_project("-project-", yaml={"repository": {"type": "git", "url": "ssh://foobar.git"}})
        version = ProjectVersion("-version-")
        version._YAML = {"revision": "-revision-"}

        checkout = uut.get_checkout(version, "-base_path-")

        assert isinstance(checkout, GitProjectCheckout)
        assert_equals("ssh://foobar.git", checkout.url)
        assert_equals("-project-", checkout.name)
        assert_equals("-version-", checkout.version)
        assert_equals("-revision-~1", checkout.revision)

    def test_svn_project(self):
        uut = create_project("-project-", yaml={"repository": {"type": "svn", "url": "http://url/svn"}})
        version = ProjectVersion("-version-")
        version._YAML = {"revision": "667"}

        checkout = uut.get_checkout(version, "-base_path-")

        assert isinstance(checkout, SVNProjectCheckout)
        assert_equals("http://url/svn", checkout.url)
        assert_equals("-project-", checkout.name)
        assert_equals("-version-", checkout.version)
        assert_equals("666", checkout.revision)

    def test_unknown_type(self):
        uut = create_project("", yaml={"repository": {"type": "unknown"}})
        assert_raises(ValueError, uut.get_checkout, ProjectVersion(""), "-irrelevant-")
