import os
import subprocess
import unittest
from os import makedirs
from os.path import join, exists
from shutil import rmtree
from tempfile import mkdtemp

from nose.tools import assert_raises

from benchmark.nosetests.test_misuse import TMisuse
from benchmark.checkout import Checkout
from benchmark.utils.io import create_file

GIT = 'git'
SVN = 'svn'
SYNTHETIC = 'synthetic'

GIT_REVISION = '2c4e93c712461ae20051409f472e4857e2189393'

SVN_REVISION = "1"


# noinspection PyAttributeOutsideInit
class TestCheckout(unittest.TestCase):
    def setUp(self):

        self.temp_dir = mkdtemp(prefix='mubench-checkout-test_')

        os.chdir(self.temp_dir)

        self.test_checkout_dir = join(self.temp_dir, 'checkouts')
        makedirs(self.test_checkout_dir)

        self.uut = Checkout(checkout_parent=False, setup_revisions=False, outlog=None, errlog=None)

    def tearDown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    @unittest.skip("")
    def test_checkout_git(self):
        self.create_git_repository()
        git_url = join(self.test_checkout_dir, 'git')
        Checkout(True, True, None, None).checkout(TMisuse('', self.get_yaml(git_url, 'git')))
        git_repository = join(self.test_checkout_dir, 'git', '.git')
        assert exists(git_repository)

    @unittest.skip("")
    def test_checkout_svn(self):
        self.create_svn_repository()
        svn_url = join(self.test_checkout_dir, 'svn')
        Checkout(True, True, None, None).checkout(TMisuse('', self.get_yaml(svn_url, 'svn', revision='1')))
        svn_repository = join(self.test_checkout_dir, 'svn', '.svn')
        assert exists(svn_repository)

    def test_checkout_synthetic(self):
        self.create_synthetic_repository('synthetic-exmpl', 'synthetic.java')
        Checkout(True, True, None, None).checkout(TMisuse('synthetic-exmpl', self.get_yaml(":url:", 'synthetic')))
        synthetic_file = join(self.test_checkout_dir, 'synthetic-exmpl', 'synthetic.java')
        assert exists(synthetic_file)

    @staticmethod
    def get_yaml(url: str, vcs_type: str, revision: str = '', file: str = ''):
        repository = {'url': url, 'type': vcs_type}
        return {'fix': {'repository': repository, 'revision': revision, 'file': file}}

    def create_git_repository(self):
        with open(os.devnull, 'w') as FNULL:
            # initialize git repository
            git_repository_path = join(self.test_checkout_dir, 'git')
            makedirs(git_repository_path, exist_ok=True)
            subprocess.call('git init', cwd=git_repository_path, bufsize=1, shell=True, stdout=FNULL)

    def create_svn_repository(self):
        with open(os.devnull, 'w') as FNULL:
            # initialize svn repository
            # svnadmin create creates the subdirectory 'repository-svn'
            svn_subfolder = 'svn'
            subprocess.call('svnadmin create ' + svn_subfolder, cwd=self.test_checkout_dir, bufsize=1, shell=True,
                            stdout=FNULL)
            subprocess.call('svn update ', cwd=join(self.test_checkout_dir, svn_subfolder), bufsize=1, shell=True,
                            stdout=FNULL)

    def create_synthetic_repository(self, misuse_name: str, example_file: str):
        test_data_path = join(self.temp_dir, misuse_name, 'compile')
        makedirs(test_data_path, exist_ok=True)
        create_file(join(test_data_path, example_file))


class TestGetParent:
    def test_get_parent_git(self):
        assert "bla~1" == Checkout.get_parent(GIT, "bla")

    def test_get_parent_svn(self):
        assert 41 == Checkout.get_parent(SVN, 42)

    def test_get_parent_svn_with_string_input(self):
        assert 41 == Checkout.get_parent(SVN, "42")

    def test_get_parent_synthetic(self):
        assert 100 == Checkout.get_parent(SYNTHETIC, 100)

    def test_value_error_on_unknown_vcs(self):
        assert_raises(ValueError, Checkout.get_parent, 'unknown vcs', 1)
