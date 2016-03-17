import unittest
from genericpath import exists
from os.path import join
from shutil import rmtree
from tempfile import gettempdir

import checkout

GIT = 'git'
SVN = 'svn'
SYNTHETIC = 'synthetic'

GIT_REPOSITORY = 'https://github.com/stg-tud/MUBench.git'
GIT_REVISION = '472c7b704bed5162e7ed3f0e9a7c464f448e7a83'
GIT_PARENT_REVISION = 'b4db2acace11e41abdb80f3a902bf09148c8c831'

SVN_REPOSITORY = ''
SYNTHETIC_REPOSITORY = ''

TEMP_DIR = join(str(gettempdir()), 'mubench_test_temp')


class CheckoutTest(unittest.TestCase):
    def test_creates_git_repository(self):
        checkout.checkout_parent(GIT, GIT_REPOSITORY, GIT_REVISION, TEMP_DIR, False)
        self.assertTrue(exists(join(TEMP_DIR, '.git')))

    def test_creates_svn_repository(self):
        pass  # TODO

    def test_copies_synthetic_repository(self):
        pass  # TODO

    def test_checkout_fails_for_non_empty_target_dir(self):
        pass  # TODO

    def test_checkout_fails_for_file_as_target_dir(self):
        pass  # TODO

    def test_checkout_fails_for_unknown_vcs(self):
        pass  # TODO

    def tearDown(self):
        rmtree(TEMP_DIR, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
