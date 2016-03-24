from os import makedirs
from os.path import join, abspath, dirname
from shutil import rmtree
from tempfile import mkdtemp

import yaml

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

        self.REPOSITORY_GIT = join(self.TEST_ENV_SOURCE_DIR, 'repository-git')
        self.REPOSITORY_SVN = join(self.TEST_ENV_SOURCE_DIR, 'repository-svn')
        self.REPOSITORY_SYNTHETIC = 'synthetic.java'

        self.DATA = []

    def setUp(self):
        makedirs(self.TEST_ENV_PATH)
        self.setup_settings()
        self.create_yaml_data()

    def tearDown(self):
        rmtree(self.TEST_ENV_PATH)

    def setup_settings(self):
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

    def create_yaml_data(self):
        git_yaml = self.get_git_yaml()
        svn_yaml = self.get_svn_yaml()
        synthetic_yaml = self.get_synthetic_yaml()
        self.create_data_file('git.yml', git_yaml)
        self.create_data_file('svn.yml', svn_yaml)
        self.create_data_file('synthetic.yml', synthetic_yaml)
        create_file(join(settings.DATA_PATH, 'synthetic.java'), truncate=True)

    def get_git_yaml(self):
        content = {
            'fix': {'repository': {'url': self.REPOSITORY_GIT, 'type': 'git'}, 'files': [{'name': 'some-class.java'}]}}
        return content

    def get_svn_yaml(self):
        content = {
            'fix': {'repository': {'url': self.REPOSITORY_SVN, 'type': 'svn'}, 'files': [{'name': 'some-class.java'}]}}
        return content

    def get_synthetic_yaml(self):
        content = {'fix': {'repository': {'url': self.REPOSITORY_SYNTHETIC, 'type': 'synthetic'},
                           'files': [{'name': 'synthetic.java'}]}}
        return content

    def create_data_file(self, file_name, content):
        file = join(settings.DATA_PATH, file_name)
        safe_write(yaml.dump(content), file, append=False)
        self.DATA.append((file, content))
