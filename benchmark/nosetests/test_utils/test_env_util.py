import yaml
from os import makedirs, chdir
from os.path import join, abspath, dirname, pardir
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp

from benchmark.utils.io import safe_write


class TestEnv:
    def __init__(self):
        self.TEST_ENV_SOURCE_DIR = join(dirname(abspath(__file__)), 'test-env')
        self.TEST_ENV_INSTANCE_PATH = mkdtemp(prefix='mubench-test-env_')

        mubench = join(dirname(abspath(__file__)), pardir, pardir, pardir)
        chdir(mubench)  # set the cwd to the MUBench folder

        self.DATA = []

        self.DETECTOR = 'dummy-miner'

        self.FILE_DETECTOR_RESULT = 'result.txt'

        self.DATA_PATH = join(self.TEST_ENV_INSTANCE_PATH, 'data')
        self.RESULTS_PATH = join(self.TEST_ENV_INSTANCE_PATH, 'results', self.DETECTOR)
        self.CHECKOUT_DIR = join(self.TEST_ENV_INSTANCE_PATH, 'checkout')

        makedirs(self.RESULTS_PATH, exist_ok=True)

        self.REPOSITORY_GIT = join(self.TEST_ENV_INSTANCE_PATH, 'repository-git')
        self.REPOSITORY_SVN = Path(join(self.TEST_ENV_INSTANCE_PATH, 'repository-svn')).as_uri()

        self.TIMEOUT = None

    # noinspection PyPep8Naming
    def tearDown(self):
        rmtree(self.TEST_ENV_INSTANCE_PATH, ignore_errors=True)


