import os
import subprocess
from os import makedirs
from os.path import join, exists
from shutil import rmtree
from tempfile import mkdtemp

from nose.tools import assert_raises

from benchmark.checkout import Checkout
from benchmark.utils.io import create_file

GIT = 'git'
SVN = 'svn'
SYNTHETIC = 'synthetic'

GIT_REVISION = '2c4e93c712461ae20051409f472e4857e2189393'

SVN_REVISION = "1"


# noinspection PyAttributeOutsideInit
class TestCheckout:
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-checkout-test_')

        os.chdir(self.temp_dir)

        self.test_checkout_dir = join(self.temp_dir, 'checkouts', 'unittest-checkouts')
        self.test_data_path = join(self.temp_dir, 'data')

        makedirs(self.test_checkout_dir)
        makedirs(self.test_data_path)

        setup_repositories(self.test_checkout_dir)

        self.uut = Checkout(checkout_parent=False, setup_revisions=False)

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_checkout_git(self):
        git_url = join(self.test_checkout_dir, 'git')
        Checkout(True, True).checkout('', get_yaml(git_url, 'git'))
        git_repository = join(self.temp_dir, 'checkouts', 'git', '.git')
        assert exists(git_repository)

    def test_checkout_svn(self):
        svn_url = join(self.test_checkout_dir, 'svn')
        Checkout(True, True).checkout('', get_yaml(svn_url, 'svn', revision='1'))
        svn_repository = join(self.temp_dir, 'checkouts', 'svn', '.svn')
        assert exists(svn_repository)

    def test_checkout_synthetic(self):
        create_file(join(self.test_data_path, 'synthetic.java'))
        synthetic_url = 'synthetic.java'
        Checkout(True, True).checkout('synthetic.yml', get_yaml(synthetic_url, 'synthetic', file='synthetic.java'))
        synthetic_file = join(self.temp_dir, 'checkouts', 'synthetic', 'synthetic.java')
        assert exists(synthetic_file)


def get_yaml(url: str, vcs_type: str, revision: str = '', file: str = ''):
    repository = {'url': url, 'type': vcs_type}
    return {'fix': {'repository': repository, 'revision': revision, 'file': file}}


def setup_repositories(checkout_dir: str):
    with open(os.devnull, 'w') as FNULL:
        # initialize git repository
        git_repository_path = join(checkout_dir, 'git')
        makedirs(git_repository_path, exist_ok=True)
        subprocess.call('git init', cwd=git_repository_path, bufsize=1, shell=True, stdout=FNULL)

        # initialize svn repository
        # svnadmin create creates the subdirectory 'repository-svn'
        svn_repository_path = checkout_dir
        svn_subfolder = 'svn'
        subprocess.call('svnadmin create ' + svn_subfolder, cwd=svn_repository_path, bufsize=1, shell=True,
                        stdout=FNULL)


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
