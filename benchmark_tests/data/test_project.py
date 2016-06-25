import os
import yaml
from tempfile import mkdtemp

from nose.tools import assert_equals, assert_raises
from os.path import join

from benchmark.data import project
from benchmark.data.project import Project
from benchmark.data.project_checkout import LocalProjectCheckout, GitProjectCheckout, SVNProjectCheckout
from benchmark.data.project_version import ProjectVersion
from benchmark.utils.io import remove_tree, create_file, safe_open


# noinspection PyAttributeOutsideInit
class TestProject:
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-test-project_")

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_sets_path(self):
        uut = Project("MUBench/data/project/")
        assert_equals("MUBench/data/project/", uut._path)

    def test_finds_project_file(self):
        uut = Project("MUBench/data/project/")
        assert_equals(os.path.join("MUBench/data/project/", Project.PROJECT_FILE), uut._project_file)

    def test_finds_versions_path(self):
        uut = Project("MUBench/data/project/")
        assert_equals(os.path.join("MUBench/data/project/", "versions"), uut._versions_path)

    def test_validate_false(self):
        assert not Project.validate(self.temp_dir)

    def test_validate_true(self):
        create_file(join(self.temp_dir, Project.PROJECT_FILE))
        assert Project.validate(self.temp_dir)

    def test_finds_versions(self):
        version_file = join(self.temp_dir, "versions", "v0", ProjectVersion.VERSION_FILE)
        create_file(version_file)

        uut = Project(self.temp_dir)

        actual_versions = uut.versions
        assert_equals(1, len(actual_versions))

        actual_version = actual_versions[0]
        assert_equals(join(self.temp_dir, "versions", "v0"), actual_version._path)

    def test_reads_project_file(self):
        project_file = join(self.temp_dir, Project.PROJECT_FILE)
        test_dict = {"name": "Project Name", "repository": {"type": "git", "url": "https://git.org/repo.git"},
                     "url": "http://www.project.org/"}
        with safe_open(project_file, 'w+') as stream:
            yaml.dump(test_dict, stream)

        uut = Project(self.temp_dir)

        assert_equals(test_dict, uut._yaml)

    def test_id(self):
        uut = Project(join(self.temp_dir, "project"))
        assert_equals("project", uut.id)

    def test_name(self):
        uut = Project(self.temp_dir)
        uut._YAML = {"name": "Project Name"}
        assert_equals("Project Name", uut.name)

    def test_name_default_none(self):
        uut = Project(self.temp_dir)
        uut._YAML = {}
        assert_equals(None, uut.name)

    def test_repository_default_none(self):
        uut = Project(self.temp_dir)
        uut._YAML = {}
        assert_equals(None, uut.name)

    def test_repository_type(self):
        uut = Project(self.temp_dir)
        uut._YAML = {"repository": {"type": "git"}}
        assert_equals("git", uut.repository.vcstype)

    def test_repository_url(self):
        uut = Project(self.temp_dir)
        uut._YAML = {"repository": {"url": "http://git.org/repo.git"}}
        assert_equals("http://git.org/repo.git", uut.repository.url)

    def test_derives_compile_base_path(self):
        uut = Project("project")
        uut._YAML = {}
        project_compile = uut.get_compile(ProjectVersion("version"), "/base/path")
        assert_equals(join("/base/path", "project", "version"), project_compile.base_path)

    def test_finds_all_projects(self):
        create_file(join(self.temp_dir, "p1", "project.yml"))
        create_file(join(self.temp_dir, "p2", "project.yml"))

        actual = Project.get_projects(self.temp_dir)

        assert_equals(2, len(actual))
        assert_equals(join(self.temp_dir, "p1"), actual[0]._path)
        assert_equals(join(self.temp_dir, "p2"), actual[1]._path)

    def test_validates_projects(self):
        create_file(join(self.temp_dir, "p1", "iamnotaproject.yml"))
        actual = Project.get_projects(self.temp_dir)
        assert_equals([], actual)


class TestProjectCheckout:
    def test_synthetic_project(self):
        uut = Project("-project-")
        uut._YAML = {"repository": {"type": "synthetic"}}
        version = ProjectVersion("")

        checkout = uut.get_checkout(version, ":base_path:")

        assert isinstance(checkout, LocalProjectCheckout)
        assert_equals(join("-project-", "versions", "0", "compile"), checkout.url)
        assert_equals("-project-", checkout.name)

    def test_git_project(self):
        uut = Project("-project-")
        uut._YAML = {"repository": {"type": "git", "url": "ssh://foobar.git"}}
        version = ProjectVersion("-version-")
        version._YAML = {"revision": "-revision-"}

        checkout = uut.get_checkout(version, "-base_path-")

        assert isinstance(checkout, GitProjectCheckout)
        assert_equals("ssh://foobar.git", checkout.url)
        assert_equals("-project-", checkout.name)
        assert_equals("-version-", checkout.version)
        assert_equals("-revision-~1", checkout.revision)

    def test_svn_project(self):
        uut = Project("-project-")
        uut._YAML = {"repository": {"type": "svn", "url": "http://url/svn"}}
        version = ProjectVersion("-version-")
        version._YAML = {"revision": "667"}

        checkout = uut.get_checkout(version, "-base_path-")

        assert isinstance(checkout, SVNProjectCheckout)
        assert_equals("http://url/svn", checkout.url)
        assert_equals("-project-", checkout.name)
        assert_equals("-version-", checkout.version)
        assert_equals("666", checkout.revision)

    def test_unknown_type(self):
        uut = Project("")
        uut._YAML = {"repository": {"type": "unknown"}}
        assert_raises(ValueError, uut.get_checkout, ProjectVersion(""), "-irrelevant-")
