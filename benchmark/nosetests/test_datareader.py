import yaml
from os import chdir
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

from nose.tools import assert_equals

from benchmark.datareader import DataReader
from benchmark.utils.io import safe_write


# noinspection PyAttributeOutsideInit
class TestDatareader:
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-datareader-test_')

        chdir(self.temp_dir)

        self.repo_dir = join(self.temp_dir, 'repositories')
        self.data_path = join(self.temp_dir, 'data')

        self.data = []

        self.create_data_file('git.yml', self.__get_git_yaml())
        self.create_data_file('svn.yml', self.__get_svn_yaml())
        self.create_data_file('synthetic.yml', self.__get_synthetic_yaml())

        self.uut = DataReader(self.data_path, white_list=[""], black_list=[])

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_finds_all_files(self):
        def save_values(file, data): values_used.append((file, data))

        values_used = []
        self.uut.add(save_values)
        self.uut.run()
        assert len(values_used) == len(self.data)

    def test_correct_values_passed(self):
        def save_values(file, data): values_used.append((file, data))

        values_used = []
        self.uut.add(save_values)
        self.uut.run()
        assert values_used == self.data

    def test_return_values(self):
        def return_values(file, data): return file, data

        self.uut.add(return_values)
        actual = self.uut.run()
        assert_equals(self.data, actual)

    def test_black_list(self):
        def save_values(file, data): values_used.append((file, data))

        self.uut = DataReader(self.data_path, [""], [""])

        values_used = []
        self.uut.add(save_values)
        self.uut.run()

        assert not values_used

    def test_white_list(self):
        def save_values(file, data): values_used.append((file, data))

        self.uut = DataReader(self.data_path, [], [])

        values_used = []
        self.uut.add(save_values)
        self.uut.run()

        assert not values_used

    def __create_yaml_data(self):
        git_yaml = self.__get_git_yaml()
        svn_yaml = self.__get_svn_yaml()
        synthetic_yaml = self.__get_synthetic_yaml()
        self.create_data_file('git.yml', git_yaml)
        self.create_data_file('svn.yml', svn_yaml)
        self.create_data_file('synthetic.yml', synthetic_yaml)

    def __get_git_yaml(self):
        repository = {'url': 'git', 'type': 'git'}
        files = [{'name': 'some-class.java'}]
        fix = {'repository': repository, 'revision': '', 'files': files}
        self.git_misuse_label = "someClass#this#doSomething"
        misuse = {'file': files[0], 'type': 'some-type', 'method': 'doSomething(Object, int)',
                  'usage': 'digraph { 0 [label="' + self.git_misuse_label + '"] }'}
        content = {'misuse': misuse, 'fix': fix}
        return content

    @staticmethod
    def __get_svn_yaml():
        content = {
            'fix': {'repository': {'url': 'svn', 'type': 'svn'}, 'revision': '1',
                    'files': [{'name': 'some-class.java'}]}}
        return content

    @staticmethod
    def __get_synthetic_yaml():
        content = {
            'fix': {'repository': {'url': 'synthetic-close-1.java', 'revision': '', 'type': 'synthetic'},
                    'files': [{'name': 'synthetic.java'}]}}
        return content

    def create_data_file(self, file_name: str, content: dict):
        file = join(self.data_path, file_name)
        safe_write(yaml.dump(content), file, append=False)
        self.data.append((file, content))
