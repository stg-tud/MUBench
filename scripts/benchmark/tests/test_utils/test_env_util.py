from distutils.dir_util import copy_tree
from os import makedirs
from os.path import join, abspath, dirname
from shutil import rmtree, copy, copyfile
from tempfile import mkdtemp

import yaml
from subprocess import Popen

import settings
from utils.io import safe_write, create_file


class TestEnvironment:
    def __init__(self):
        self.TEST_ENV_SOURCE_DIR = join(dirname(abspath(__file__)), 'test-env')

        self.TEST_ENV_PATH = join(mkdtemp(), 'test_env')

        self.DATA_PATH = join(self.TEST_ENV_PATH, 'data')
        self.MINER = 'test-markall-miner.jar'
        self.MISUSE_DETECTOR = join(self.TEST_ENV_SOURCE_DIR, self.MINER)
        self.FILE_DETECTOR_RESULT = 'result.txt'

        self.RESULTS_PATH = join(self.TEST_ENV_PATH, 'results')
        self.BENCHMARK_RESULT_FILE = join(self.RESULTS_PATH, 'test-benchmark-result.txt')

        self.LOG_PATH = join(self.TEST_ENV_PATH, 'logs')
        self.LOG_FILE_ERROR = join(self.LOG_PATH, 'test-error.log')
        self.LOG_FILE_CHECKOUT = join(self.LOG_PATH, 'test-checkout.log')
        self.LOG_FILE_RESULTS_EVALUATION = join(self.LOG_PATH, 'test-results-evaluation.log')

        self.TEMP_SUBFOLDER = 'test-checkout'
        self.VERBOSE = False
        self.IGNORES = []

        self.REPOSITORY_GIT = join(self.TEST_ENV_PATH, 'repository-git')
        self.REPOSITORY_SVN = join(self.TEST_ENV_PATH, 'repository-svn')
        self.REPOSITORY_SYNTHETIC = 'synthetic.java'

        self.DATA = []

        makedirs(self.TEST_ENV_PATH)
        self.__setup_settings()
        self.__create_yaml_data()
        self.__initialize_repositories()

    def tearDown(self):
        rmtree(self.TEST_ENV_PATH, ignore_errors=True)

    def __setup_settings(self):
        settings.DATA_PATH = self.DATA_PATH
        settings.MISUSE_DETECTOR = self.MISUSE_DETECTOR
        settings.FILE_DETECTOR_RESULT = self.FILE_DETECTOR_RESULT

        settings.RESULTS_PATH = self.RESULTS_PATH
        settings.BENCHMARK_RESULT_FILE = self.BENCHMARK_RESULT_FILE

        settings.LOG_PATH = self.LOG_PATH
        settings.LOG_FILE_ERROR = self.LOG_FILE_ERROR
        settings.LOG_FILE_CHECKOUT = self.LOG_FILE_CHECKOUT
        settings.LOG_FILE_RESULTS_EVALUATION = self.LOG_FILE_RESULTS_EVALUATION

        settings.TEMP_SUBFOLDER = self.TEMP_SUBFOLDER
        settings.VERBOSE = self.VERBOSE
        settings.IGNORES = self.IGNORES

    def __initialize_repositories(self):
        # initialize git repository
        git_repository_path = join(self.TEST_ENV_PATH, 'repository-git')
        makedirs(git_repository_path)
        Popen('git init', cwd=git_repository_path, bufsize=1, shell=True).wait()
        copy_tree(join(self.TEST_ENV_SOURCE_DIR, 'repository-git'), git_repository_path)
        Popen('git add -A', cwd=git_repository_path, bufsize=1, shell=True).wait()
        Popen('git commit -m "commit message"', cwd=git_repository_path, bufsize=1, shell=True).wait()

        # initialize svn repository
        svn_repository_path = join(self.TEST_ENV_PATH, 'repository-svn')
        makedirs(svn_repository_path)
        # TODO create repository in svn_repository_path
        copy_tree(join(self.TEST_ENV_SOURCE_DIR, 'repository-svn'), svn_repository_path)

        # initialize synthetic repository
        synthetic_repository_path = join(settings.DATA_PATH, 'repository-synthetic')
        makedirs(synthetic_repository_path)
        copy_tree(join(self.TEST_ENV_SOURCE_DIR, 'repository-synthetic'), synthetic_repository_path)
        copyfile(join(self.TEST_ENV_SOURCE_DIR, 'repository-synthetic', 'synthetic.java'),
                 join(self.DATA_PATH, 'synthetic.java'))

    def __create_yaml_data(self):
        git_yaml = self.__get_git_yaml()
        svn_yaml = self.__get_svn_yaml()
        synthetic_yaml = self.__get_synthetic_yaml()
        self.create_data_file('git.yml', git_yaml)
        self.create_data_file('svn.yml', svn_yaml)
        self.create_data_file('synthetic.yml', synthetic_yaml)

    def __get_git_yaml(self):
        content = {
            'fix': {'repository': {'url': self.REPOSITORY_GIT, 'type': 'git'}, 'files': [{'name': 'some-class.java'}]}}
        return content

    def __get_svn_yaml(self):
        content = {
            'fix': {'repository': {'url': self.REPOSITORY_SVN, 'type': 'svn'}, 'files': [{'name': 'some-class.java'}]}}
        return content

    def __get_synthetic_yaml(self):
        content = {'fix': {'repository': {'url': self.REPOSITORY_SYNTHETIC, 'type': 'synthetic'},
                           'files': [{'name': 'synthetic.java'}]}}
        return content

    def create_data_file(self, file_name, content):
        file = join(settings.DATA_PATH, file_name)
        safe_write(yaml.dump(content), file, append=False)
        self.DATA.append((file, content))
