import unittest
from genericpath import exists
from os.path import join

from checkout import Checkout
import utils.io
from tests.test_utils.test_env_util import TestEnvironment

GIT = 'git'
SVN = 'svn'
SYNTHETIC = 'synthetic'

GIT_REVISION = '2c4e93c712461ae20051409f472e4857e2189393'

SVN_REVISION = 1


class CheckoutTest(unittest.TestCase):
    def setUp(self):
        self.test_env = TestEnvironment()
        self.uut = Checkout(self.test_env.DATA_PATH, self.test_env.CHECKOUT_DIR)

    def tearDown(self):
        self.test_env.tearDown()

    def test_creates_git_repository(self):
        target_dir = join(self.test_env.CHECKOUT_DIR, 'git')
        self.uut.checkout_parent(GIT, self.test_env.REPOSITORY_GIT, GIT_REVISION, target_dir)
        repository = join(target_dir, '.git')
        self.assertTrue(exists(repository))

    def test_creates_svn_repository(self):
        target_dir = join(self.test_env.CHECKOUT_DIR, 'svn')
        self.uut.checkout_parent(SVN, self.test_env.REPOSITORY_SVN, SVN_REVISION, target_dir)
        repository = join(target_dir, 'repository-svn')
        self.assertTrue(exists(repository))

    def test_copies_synthetic_repository(self):
        target_dir = join(self.test_env.CHECKOUT_DIR, 'synthetic')
        self.uut.checkout_parent(SYNTHETIC, 'synthetic-close-1.java', '', target_dir)
        repository = join(target_dir, 'synthetic-close-1.java')
        self.assertTrue(exists(repository))

    def test_checkout_fails_for_non_empty_target_dir(self):
        with self.assertRaises(ValueError):
            non_empty_dir = join(self.test_env.CHECKOUT_DIR, 'non-empty-target-dir')
            utils.io.create_file_path(join(non_empty_dir, 'something'))
            utils.io.create_file(join(non_empty_dir, 'something'))
            self.uut.checkout_parent(GIT, self.test_env.REPOSITORY_GIT, GIT_REVISION, non_empty_dir)

    def test_checkout_fails_for_file_as_target_dir(self):
        file = join(self.test_env.CHECKOUT_DIR, 'file')
        utils.io.create_file_path(file)
        utils.io.create_file(file)
        with self.assertRaises(ValueError):
            self.uut.checkout_parent(GIT, self.test_env.REPOSITORY_GIT, GIT_REVISION, file)

    def test_checkout_fails_for_unknown_vcs(self):
        with self.assertRaises(ValueError):
            target_dir = join(self.test_env.CHECKOUT_DIR, 'unknown-vcs')
            self.uut.checkout_parent('invalid vcs', self.test_env.REPOSITORY_GIT, GIT_REVISION, target_dir)

    def test_logs_into_log_folder(self):
        target_dir = join(self.test_env.CHECKOUT_DIR, 'log-test-checkout')
        self.uut.checkout_parent(GIT, self.test_env.REPOSITORY_GIT, GIT_REVISION, target_dir)
        self.assertTrue(exists(join(target_dir, 'checkout.log')))

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


class GetParentTest(unittest.TestCase):
    def test_get_parent_git(self):
        self.assertEquals(Checkout.get_parent(GIT, "bla"), "bla~1")

    def test_get_parent_svn(self):
        self.assertEquals(Checkout.get_parent(SVN, 42), "41")

    def test_get_parent_svn_with_string_input(self):
        self.assertEquals(Checkout.get_parent(SVN, "42"), "41")

    def test_get_parent_synthetic(self):
        self.assertEquals(Checkout.get_parent(SYNTHETIC, 100), "100")

    def test_value_error_on_unknown_vcs(self):
        with self.assertRaises(ValueError):
            Checkout.get_parent('unknown vcs', 1)


if __name__ == '__main__':
    unittest.main()
