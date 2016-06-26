import yaml
from os.path import join
from tempfile import mkdtemp

from nose.tools import assert_equals

from benchmark.data.misuse import Misuse
from benchmark.data.project_version import ProjectVersion
from benchmark.utils.io import remove_tree, create_file, safe_open


# noinspection PyAttributeOutsideInit
class TestProjectVersion:
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-test-project-version_")

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_sets_path(self):
        uut = ProjectVersion("MUBench/data/project/versions/version")
        assert_equals("MUBench/data/project/versions/version", uut._path)

    def test_validate_false(self):
        assert not ProjectVersion.validate(self.temp_dir)

    def test_validate_true(self):
        create_file(join(self.temp_dir, ProjectVersion.VERSION_FILE))
        assert ProjectVersion.validate(self.temp_dir)

    def test_finds_version_yml(self):
        uut = ProjectVersion("path")
        assert_equals(join("path", ProjectVersion.VERSION_FILE), uut._version_file)

    def test_read_version_file(self):
        test_dict = {"build": {"classes": "target/classes/", "commands": ["mvn compile"], "src": "src/java/"},
                     "misuses": ['1', '2'], "revision": "1fe5439baf32af2114958e3cfc3512bd72c84773"}
        with safe_open(join(self.temp_dir, ProjectVersion.VERSION_FILE), 'w+') as stream:
            yaml.dump(test_dict, stream)

        uut = ProjectVersion(self.temp_dir)

        assert_equals(test_dict, uut._yaml)

    def test_misuses_default_empty(self):
        uut = ProjectVersion("")
        uut._YAML = {}
        assert_equals([], uut.misuses)

    def test_finds_misuses_dir(self):
        uut = ProjectVersion(join(self.temp_dir, "versions", "version"))
        assert_equals(join(self.temp_dir, "misuses"), uut._misuses_dir)

    def test_finds_misuses(self):
        version_dir = join(self.temp_dir, "versions", "version")
        uut = ProjectVersion(version_dir)

        misuse_dir = join(self.temp_dir, "misuses", "1")
        create_file(join(misuse_dir, Misuse.MISUSE_FILE))

        uut._YAML = {"misuses": ['1']}

        actual_misuses = uut.misuses
        assert_equals(1, len(actual_misuses))

        actual_misuse = actual_misuses[0]
        assert_equals(misuse_dir, actual_misuse.path)

    def test_creates_build_config(self):
        uut = ProjectVersion("")
        uut._YAML = {"build": {"src": "src/java/", "commands": ["mvn compile"], "classes": "target/classes/"}}
        assert_equals("src/java/", uut.source_dir)
        assert_equals(["mvn compile"], uut.compile_commands)
        assert_equals("target/classes/", uut.classes_dir)

    def test_creates_build_config_with_defaults(self):
        uut = ProjectVersion("")
        uut._YAML = {}
        assert_equals("", uut.source_dir)
        assert_equals([], uut.compile_commands)
        assert_equals("", uut.classes_dir)

    def test_id(self):
        assert_equals("version_id", ProjectVersion("project/versions/version_id").id)

    def test_derives_additional_compile_sources_path(self):
        uut = ProjectVersion("version")
        assert_equals(join("version", "compile"), uut.additional_compile_sources)
