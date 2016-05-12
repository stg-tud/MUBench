import os
import subprocess
from distutils.dir_util import copy_tree
from os import makedirs
from os.path import join, exists
from pprint import PrettyPrinter

from nose.tools import assert_raises
from shutil import copyfile

from benchmark.checkout import Checkout
from benchmark.nosetests.test_utils.test_env_util import TestEnv
from benchmark.utils.io import create_file
from benchmark.utils.io import create_file_path

GIT = 'git'
SVN = 'svn'
SYNTHETIC = 'synthetic'

GIT_REVISION = '2c4e93c712461ae20051409f472e4857e2189393'

SVN_REVISION = "1"


# noinspection PyAttributeOutsideInit
class TestCheckout:
    def setup(self):
        self.test_env = TestEnv()

        test_env_instance_path = self.test_env.TEST_ENV_INSTANCE_PATH
        test_env_source_dir = self.test_env.TEST_ENV_SOURCE_DIR

        # initialize git repository
        git_repository_path = join(test_env_instance_path, 'repository-git')
        makedirs(git_repository_path)

        with open(os.devnull, 'w') as FNULL:
            subprocess.call('git init', cwd=git_repository_path, bufsize=1, shell=True, stdout=FNULL)
            copy_tree(join(test_env_source_dir, 'repository-git'), git_repository_path)
            subprocess.call('git add -A', cwd=git_repository_path, bufsize=1, shell=True, stdout=FNULL)
            subprocess.call('git commit -m "commit message"', cwd=git_repository_path, bufsize=1, shell=True,
                            stdout=FNULL)

            # initialize svn repository
            # svnadmin create creates the subdirectory 'repository-svn'
            svn_subfolder = 'repository-svn'
            subprocess.call('svnadmin create ' + svn_subfolder, cwd=test_env_instance_path, bufsize=1, shell=True,
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

        self.uut = Checkout()

    def teardown(self):
        self.test_env.tearDown()

    def test_creates_git_repository(self):
        target_dir = join(self.test_env.CHECKOUT_DIR, 'git')
        self.uut.checkout_parent(GIT, self.test_env.REPOSITORY_GIT, GIT_REVISION, target_dir)
        repository = join(target_dir, '.git')
        assert exists(repository)

    def test_creates_svn_repository(self):
        target_dir = join(self.test_env.CHECKOUT_DIR, 'svn')
        self.uut.checkout_parent(SVN, self.test_env.REPOSITORY_SVN, SVN_REVISION, target_dir)
        repository = join(target_dir, 'repository-svn')
        assert exists(repository)

    def test_copies_synthetic_repository(self):
        target_dir = join(self.test_env.CHECKOUT_DIR, 'synthetic')
        self.uut.checkout_parent(SYNTHETIC, 'synthetic-close-1.java', '', target_dir)
        repository = join(target_dir, 'synthetic-close-1.java')
        assert exists(repository)

    def test_checkout_fails_for_file_as_target_dir(self):
        file = join(self.test_env.CHECKOUT_DIR, 'file')
        create_file_path(file)
        create_file(file)
        assert_raises(FileExistsError, self.uut.checkout_parent, GIT, self.test_env.REPOSITORY_GIT, GIT_REVISION, file)

    def test_checkout_fails_for_unknown_vcs(self):
        target_dir = join(self.test_env.CHECKOUT_DIR, 'unknown-vcs')
        assert_raises(ValueError, self.uut.checkout_parent, 'invalid vcs', self.test_env.REPOSITORY_GIT, GIT_REVISION,
                      target_dir)

    def test_reset_to_revision_git(self):
        target_dir = join(self.test_env.CHECKOUT_DIR, 'git-reset')
        self.uut.checkout_parent(GIT, self.test_env.REPOSITORY_GIT, GIT_REVISION, target_dir)
        self.uut.reset_to_revision(GIT, target_dir, GIT_REVISION)

    def test_reset_to_revision_svn(self):
        target_dir = join(self.test_env.CHECKOUT_DIR, 'svn-reset')
        self.uut.checkout_parent(SVN, self.test_env.REPOSITORY_SVN, SVN_REVISION, target_dir)
        self.uut.reset_to_revision(SVN, target_dir, SVN_REVISION)

    def test_reset_to_revision_synthetic(self):
        self.uut.reset_to_revision(SYNTHETIC, '', '')


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
