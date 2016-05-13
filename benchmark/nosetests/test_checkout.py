import os
import subprocess
from os import makedirs
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

from nose.tools import assert_raises

from benchmark.checkout import Checkout

GIT = 'git'
SVN = 'svn'
SYNTHETIC = 'synthetic'

GIT_REVISION = '2c4e93c712461ae20051409f472e4857e2189393'

SVN_REVISION = "1"


# noinspection PyAttributeOutsideInit
class TestCheckout:
    def setup(self):
        self.temp_dir = mkdtemp(prefix='mubench-checkout-test_')

        test_checkout_dir = join(self.temp_dir, 'checkouts', 'unittest-checkouts')
        test_data_path = join(self.temp_dir, 'data')

        makedirs(test_checkout_dir)
        makedirs(test_data_path)

        self.__setup_repositories(test_checkout_dir)

        self.uut = Checkout(checkout_parent=False, setup_revisions=False)

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_checkout(self):
        pass  # TODO implement unittests

    @staticmethod
    def __setup_repositories(test_checkout_dir):
        with open(os.devnull, 'w') as FNULL:
            # initialize git repository
            git_repository_path = join('checkout', 'unittest-checkouts', 'repository-git')
            makedirs(git_repository_path, exist_ok=True)
            subprocess.call('git init', cwd=git_repository_path, bufsize=1, shell=True, stdout=FNULL)

            # initialize svn repository
            # svnadmin create creates the subdirectory 'repository-svn'
            svn_repository_path = test_checkout_dir
            svn_subfolder = 'repository-svn'
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
