from os import chdir
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

import yaml
from nose.tools import assert_equals
from typing import Set

from benchmark.data.misuse import Misuse
from benchmark.subprocesses.datareader import DataReader, DataReaderSubprocess
from benchmark.utils.io import safe_write


# noinspection PyAttributeOutsideInit
class TestDataReader:
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-datareader-test_')

        chdir(self.temp_dir)

        self.repo_dir = join(self.temp_dir, 'repositories')
        self.data_path = join(self.temp_dir, 'data')

        self.data = set()

        self.create_misuse('git', self.__get_git_yaml())
        self.create_misuse('svn', self.__get_svn_yaml())
        self.create_misuse('synthetic', self.__get_synthetic_yaml())

        self.uut = DataReader(self.data_path, white_list=[""], black_list=[])

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_finds_all_files(self):
        subprocess = SavePaths()
        self.uut.add(subprocess)
        self.uut.run()
        assert_equals(len(self.data), len(subprocess.values))

    def test_correct_values_passed(self):
        subprocess = SavePaths()
        self.uut.add(subprocess)
        self.uut.run()
        assert_equals(self.data, subprocess.values)

    def test_black_list(self):
        subprocess = SavePaths()
        self.uut = DataReader(self.data_path, [""], [""])

        self.uut.add(subprocess)
        self.uut.run()

        assert not subprocess.values

    def test_white_list(self):
        subprocess = SavePaths()

        self.uut = DataReader(self.data_path, [], [])

        self.uut.add(subprocess)
        self.uut.run()

        assert not subprocess.values

    def test_setup_called_correctly(self):
        subprocess = SavePaths()

        self.uut.add(subprocess)
        self.uut.run()

        assert subprocess.setup_was_called_correctly

    def test_teardown_called_correctly(self):
        subprocess = SavePaths()

        self.uut.add(subprocess)
        self.uut.run()

        assert subprocess.teardown_was_called_correctly

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

    def create_misuse(self, misuse_name: str, content: dict):
        dir = join(self.data_path, misuse_name)
        file = join(dir, "meta.yml")
        safe_write(yaml.dump(content), file, append=False)
        self.data.add(dir)


class SavePaths(DataReaderSubprocess):
    def __init__(self):
        self.setup_was_called_correctly = False
        self.teardown_was_called_correctly = False
        self.values = set()  # type: Set[Misuse]

    def setup(self):
        if not self.values:
            self.setup_was_called_correctly = True

    def run(self, misuse: Misuse) -> DataReaderSubprocess.Answer:
        self.values.add(misuse.path)

    def teardown(self):
        if self.values:
            self.teardown_was_called_correctly = True
