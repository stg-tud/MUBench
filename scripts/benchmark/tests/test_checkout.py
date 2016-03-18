import unittest
from genericpath import exists
from os.path import join
from shutil import rmtree
from tempfile import gettempdir, mkdtemp

from os import mkdir

import checkout

GIT = 'git'
SVN = 'svn'
SYNTHETIC = 'synthetic'

GIT_REPOSITORY = 'https://github.com/stg-tud/MUBench.git'
GIT_REVISION = '472c7b704bed5162e7ed3f0e9a7c464f448e7a83'
GIT_PARENT_REVISION = 'b4db2acace11e41abdb80f3a902bf09148c8c831'

SVN_REPOSITORY = ''  # TODO set these values and remove skip from svn test(s)
SVN_REVISION = ''
SVN_PARENT_REVISION = ''

SYNTHETIC_REPOSITORY = 'synthetic-cme.java'


class CheckoutTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = mkdtemp()

    def test_creates_git_repository(self):
        checkout.checkout_parent(GIT, GIT_REPOSITORY, GIT_REVISION, self.temp_dir, False)
        self.assertTrue(exists(join(self.temp_dir, '.git')))

    @unittest.skip
    def test_creates_svn_repository(self):
        checkout.checkout_parent(SVN, SVN_REPOSITORY, SVN_REVISION, self.temp_dir, False)
        self.assertFalse()

    def test_copies_synthetic_repository(self):
        checkout.checkout_parent(SYNTHETIC, SYNTHETIC_REPOSITORY, None, self.temp_dir, False)
        self.assertTrue(exists(join(self.temp_dir, SYNTHETIC_REPOSITORY)))

    def test_checkout_fails_for_non_empty_target_dir(self):
        mkdir(join(self.temp_dir, 'something'))
        with self.assertRaises(ValueError):
            checkout.checkout_parent(GIT, GIT_REPOSITORY, GIT_REVISION, self.temp_dir, False)

    def test_checkout_fails_for_file_as_target_dir(self):
        file = join(self.temp_dir, 'file')
        open(file, 'w+').close()
        with self.assertRaises(ValueError):
            checkout.checkout_parent(GIT, GIT_REPOSITORY, GIT_REVISION, file, False)

    def test_checkout_fails_for_unknown_vcs(self):
        with self.assertRaises(ValueError):
            checkout.checkout_parent('invalid vcs', GIT_REPOSITORY, GIT_REVISION, self.temp_dir, False)

    def tearDown(self):
        rmtree(self.temp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
