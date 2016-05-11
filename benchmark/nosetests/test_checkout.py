from os.path import join, exists
from pprint import PrettyPrinter

from nose.tools import assert_raises

from benchmark.checkout import Checkout
from benchmark.nosetests.test_utils.test_env_util import TestEnv
from benchmark.utils.io import create_file
from benchmark.utils.io import create_file_path

GIT = 'git'
SVN = 'svn'
SYNTHETIC = 'synthetic'

GIT_REVISION = '2c4e93c712461ae20051409f472e4857e2189393'

SVN_REVISION = "1"


class TestCheckout:
    def setup(self):
        self.test_env = TestEnv()
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
