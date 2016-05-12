import os
import subprocess
from distutils.dir_util import copy_tree
from os import makedirs
from os.path import join
from shutil import copyfile

from nose.tools import assert_raises

from benchmark.checkout import Checkout
from benchmark.nosetests.test_utils.test_env_util import TestEnv

GIT = 'git'
SVN = 'svn'
SYNTHETIC = 'synthetic'

GIT_REVISION = '2c4e93c712461ae20051409f472e4857e2189393'

SVN_REVISION = "1"


# noinspection PyAttributeOutsideInit
class TestCheckout:
    def setup(self):
        self.test_env = TestEnv()

        test_env_source_dir = self.test_env.TEST_ENV_SOURCE_DIR

        test_checkout_dir = join('checkout', 'unittest-checkouts')

        with open(os.devnull, 'w') as FNULL:
            # initialize git repository
            git_repository_path = join('checkout', 'unittest-checkouts', 'repository-git')
            makedirs(git_repository_path, exist_ok=True)
            subprocess.call('git init', cwd=git_repository_path, bufsize=1, shell=True, stdout=FNULL)
            copy_tree(join(test_env_source_dir, 'repository-git'), git_repository_path)
            subprocess.call('git add -A', cwd=git_repository_path, bufsize=1, shell=True, stdout=FNULL)
            subprocess.call('git commit -m "commit message"', cwd=git_repository_path, bufsize=1, shell=True,
                            stdout=FNULL)

            # initialize svn repository
            # svnadmin create creates the subdirectory 'repository-svn'
            svn_repository_path = test_checkout_dir
            svn_subfolder = 'repository-svn'
            subprocess.call('svnadmin create ' + svn_subfolder, cwd=svn_repository_path, bufsize=1, shell=True,
                            stdout=FNULL)
            svn_source_dir = join(test_env_source_dir, svn_subfolder)
            subprocess.call('svn import {} {} -m "Initial import"'.format(svn_source_dir, self.test_env.REPOSITORY_SVN),
                            shell=True, stdout=FNULL)

        # initialize synthetic repository
        test_env_data_path = self.test_env.DATA_PATH
        synthetic_repository_path = join(test_env_data_path, 'repository-synthetic')
        makedirs(synthetic_repository_path)
        copy_tree(join(test_env_source_dir, 'repository-synthetic'), synthetic_repository_path)
        copyfile(join(test_env_source_dir, 'repository-synthetic', 'synthetic.java'),
                 join(test_env_data_path, 'synthetic.java'))

        self.uut = Checkout(checkout_parent=False, setup_revisions=False)

    # TODO implement unittests for checkouts


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
