import unittest
from genericpath import exists
from os import mkdir
from os.path import join, basename
from shutil import rmtree
from tempfile import mkdtemp

import utils.io

import checkout
import settings
from tests.test_utils.test_env_util import TestEnvironment

GIT = 'git'
SVN = 'svn'
SYNTHETIC = 'synthetic'

GIT_REVISION = '2c4e93c712461ae20051409f472e4857e2189393'
GIT_PARENT_REVISION = '451c2fd61437c1a4616f08cc1849feacc0be4839'

SVN_REPOSITORY = 'svn://svn.code.sf.net/p/itext/code/trunk'  # TODO setup local svn repository in test env instead
SVN_REVISION = 5091
SVN_PARENT_REVISION = SVN_REVISION - 1


class CheckoutTest(unittest.TestCase):
    def setUp(self):
        self.test_env = TestEnvironment()
        self.test_env.setUp()
        self.temp_dir = mkdtemp()

    def test_creates_git_repository(self):
        checkout.checkout_parent(GIT, self.test_env.REPOSITORY_GIT, GIT_REVISION, self.temp_dir, False)
        repository = join(self.temp_dir, '.git')
        self.assertTrue(exists(repository))

    def test_creates_svn_repository(self):
        checkout.checkout_parent(SVN, SVN_REPOSITORY, SVN_REVISION, self.temp_dir, False)
        repository = join(self.temp_dir, 'trunk')
        self.assertTrue(exists(repository))

    def test_copies_synthetic_repository(self):
        checkout.checkout_parent(SYNTHETIC, self.test_env.REPOSITORY_SYNTHETIC, '', self.temp_dir, False)
        repository = join(self.temp_dir, basename(self.test_env.REPOSITORY_SYNTHETIC))
        self.assertTrue(exists(repository))

    def test_checkout_fails_for_non_empty_target_dir(self):
        mkdir(join(self.temp_dir, 'something'))
        with self.assertRaises(ValueError):
            checkout.checkout_parent(GIT, self.test_env.REPOSITORY_GIT, GIT_REVISION, self.temp_dir, False)

    def test_checkout_fails_for_file_as_target_dir(self):
        file = join(self.temp_dir, 'file')
        utils.io.create_file_path(file)
        with self.assertRaises(ValueError):
            checkout.checkout_parent(GIT, self.test_env.REPOSITORY_GIT, GIT_REVISION, file, False)

    def test_checkout_fails_for_unknown_vcs(self):
        with self.assertRaises(ValueError):
            checkout.checkout_parent('invalid vcs', self.test_env.REPOSITORY_GIT, GIT_REVISION, self.temp_dir, False)

    def test_logs_into_log_folder(self):
        settings.LOG_PATH = join(self.temp_dir, 'logs')
        settings.LOG_FILE_CHECKOUT = join(settings.LOG_PATH, 'checkout.log')
        checkout.checkout_parent(GIT, self.test_env.REPOSITORY_GIT, GIT_REVISION, self.temp_dir, False)
        self.assertTrue(exists(settings.LOG_FILE_CHECKOUT))

    def tearDown(self):
        self.test_env.tearDown()
        rmtree(self.temp_dir, ignore_errors=True)


class GetParentTest(unittest.TestCase):
    def test_get_parent_git(self):
        self.assertEquals(checkout.get_parent(GIT, "bla"), "bla~1")

    def test_get_parent_svn(self):
        self.assertEquals(checkout.get_parent(SVN, 42), "41")

    def test_get_parent_synthetic(self):
        self.assertEquals(checkout.get_parent(SYNTHETIC, 100), "100")

    def test_value_error_on_unknown_vcs(self):
        with self.assertRaises(ValueError):
            checkout.get_parent('unknown vcs', 1)


if __name__ == '__main__':
    unittest.main()
