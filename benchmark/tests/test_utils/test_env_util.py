from distutils.dir_util import copy_tree
from os import makedirs
from os.path import join, abspath, dirname
from pathlib import Path
from shutil import rmtree, copyfile
from subprocess import Popen
from tempfile import mkdtemp

import yaml

from config import Config
from utils.io import safe_write


class TestEnvironment:
    def __init__(self):
        self.TEST_ENV_SOURCE_DIR = join(dirname(abspath(__file__)), 'test-env')
        self.TEST_ENV_PATH = mkdtemp(prefix='mubench-test-env_')

        self.REPOSITORY_GIT = join(self.TEST_ENV_PATH, 'repository-git')
        self.REPOSITORY_SVN = Path(join(self.TEST_ENV_PATH, 'repository-svn')).as_uri()
        self.REPOSITORY_SYNTHETIC = 'synthetic.java'

        self.DATA = []

        Config.DATA_PATH = join(self.TEST_ENV_PATH, 'data')
        Config.RESULTS_PATH = join(self.TEST_ENV_PATH, 'results')
        Config.CHECKOUT_DIR = join(self.TEST_ENV_PATH, 'checkout')
        Config.update_derived_values()

        self.__create_yaml_data()
        self.__initialize_repositories()

    # noinspection PyPep8Naming
    def tearDown(self):
        rmtree(self.TEST_ENV_PATH, ignore_errors=True)

    def __initialize_repositories(self):
        # initialize git repository
        git_repository_path = join(self.TEST_ENV_PATH, 'repository-git')
        makedirs(git_repository_path)
        Popen('git init', cwd=git_repository_path, bufsize=1, shell=True).wait()
        copy_tree(join(self.TEST_ENV_SOURCE_DIR, 'repository-git'), git_repository_path)
        Popen('git add -A', cwd=git_repository_path, bufsize=1, shell=True).wait()
        Popen('git commit -m "commit message"', cwd=git_repository_path, bufsize=1, shell=True).wait()

        # initialize svn repository
        # svnadmin create creates the subdirectory 'repository-svn'
        svn_subfolder = 'repository-svn'
        Popen('svnadmin create ' + svn_subfolder, cwd=self.TEST_ENV_PATH, bufsize=1, shell=True).wait()
        svn_source_dir = join(self.TEST_ENV_SOURCE_DIR, svn_subfolder)
        Popen('svn import {} {} -m "Initial import"'.format(svn_source_dir, self.REPOSITORY_SVN)).wait()

        # initialize synthetic repository
        synthetic_repository_path = join(Config.DATA_PATH, 'repository-synthetic')
        makedirs(synthetic_repository_path)
        copy_tree(join(self.TEST_ENV_SOURCE_DIR, 'repository-synthetic'), synthetic_repository_path)
        copyfile(join(self.TEST_ENV_SOURCE_DIR, 'repository-synthetic', 'synthetic.java'),
                 join(Config.DATA_PATH, 'synthetic.java'))

    def __create_yaml_data(self):
        git_yaml = self.__get_git_yaml()
        svn_yaml = self.__get_svn_yaml()
        synthetic_yaml = self.__get_synthetic_yaml()
        self.create_data_file('git.yml', git_yaml)
        self.create_data_file('svn.yml', svn_yaml)
        self.create_data_file('synthetic.yml', synthetic_yaml)

    def __get_git_yaml(self):
        repository = {'url': self.REPOSITORY_GIT, 'type': 'git'}
        files = [{'name': 'some-class.java'}]
        fix = {'repository': repository, 'revision': '', 'files': files}
        self.git_misuse_label = "someClass#this#doSomething"
        misuse = {'file': files[0], 'type': 'some-type', 'method': 'doSomething(Object, int)',
                  'usage': 'digraph { 0 [label="' + self.git_misuse_label + '"] }'}
        content = {'misuse': misuse, 'fix': fix}
        return content

    def __get_svn_yaml(self):
        content = {
            'fix': {'repository': {'url': self.REPOSITORY_SVN, 'type': 'svn'}, 'revision': '1',
                    'files': [{'name': 'some-class.java'}]}}
        return content

    def __get_synthetic_yaml(self):
        content = {
            'fix': {'repository': {'url': self.REPOSITORY_SYNTHETIC, 'revision': '', 'type': 'synthetic'},
                    'files': [{'name': 'synthetic.java'}]}}
        return content

    def create_data_file(self, file_name: str, content: dict):
        file = join(Config.DATA_PATH, file_name)
        safe_write(yaml.dump(content), file, append=False)
        self.DATA.append((file, content))
