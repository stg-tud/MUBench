import unittest
from genericpath import exists
from os import mkdir
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

import utils.io

import checkout
import settings

GIT = 'git'
SVN = 'svn'
SYNTHETIC = 'synthetic'

GIT_REPOSITORY = 'https://github.com/stg-tud/MUBench.git'
GIT_REVISION = '472c7b704bed5162e7ed3f0e9a7c464f448e7a83'
GIT_PARENT_REVISION = 'b4db2acace11e41abdb80f3a902bf09148c8c831'

SVN_REPOSITORY = 'svn://svn.code.sf.net/p/itext/code/trunk'  # TODO set these values and remove skip from svn test(s)
SVN_REVISION = 5091
SVN_PARENT_REVISION = SVN_REVISION - 1

SYNTHETIC_REPOSITORY = 'synthetic-cme.java'


class CheckoutTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = mkdtemp()

    def test_creates_git_repository(self):
        checkout.checkout_parent(GIT, GIT_REPOSITORY, GIT_REVISION, self.temp_dir, False)
        repository = join(self.temp_dir, '.git')
        self.assertTrue(exists(repository))

    def test_creates_svn_repository(self):
        checkout.checkout_parent(SVN, SVN_REPOSITORY, SVN_REVISION, self.temp_dir, False)
        repository = join(self.temp_dir, 'trunk')
        self.assertTrue(exists(repository))

    def test_copies_synthetic_repository(self):
        checkout.checkout_parent(SYNTHETIC, SYNTHETIC_REPOSITORY, None, self.temp_dir, False)
        repository = join(self.temp_dir, SYNTHETIC_REPOSITORY)
        self.assertTrue(exists(repository))

    def test_checkout_fails_for_non_empty_target_dir(self):
        mkdir(join(self.temp_dir, 'something'))
        with self.assertRaises(ValueError):
            checkout.checkout_parent(GIT, GIT_REPOSITORY, GIT_REVISION, self.temp_dir, False)

    def test_checkout_fails_for_file_as_target_dir(self):
        file = join(self.temp_dir, 'file')
        utils.io.create_file_path(file)
        with self.assertRaises(ValueError):
            checkout.checkout_parent(GIT, GIT_REPOSITORY, GIT_REVISION, file, False)

    def test_checkout_fails_for_unknown_vcs(self):
        with self.assertRaises(ValueError):
            checkout.checkout_parent('invalid vcs', GIT_REPOSITORY, GIT_REVISION, self.temp_dir, False)

    def test_logs_into_log_folder(self):
        settings.LOG_PATH = join(self.temp_dir, 'logs')
        settings.LOG_FILE_CHECKOUT = join(settings.LOG_PATH, 'checkout.log')
        checkout.checkout_parent(GIT, GIT_REPOSITORY, GIT_REVISION, self.temp_dir, False)
        self.assertTrue(exists(settings.LOG_FILE_CHECKOUT))

    def tearDown(self):
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
