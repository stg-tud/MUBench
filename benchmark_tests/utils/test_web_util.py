from tempfile import mkdtemp

from os.path import join

from nose.tools import assert_raises

from benchmark.utils.io import create_file, safe_write
from benchmark.utils.web_util import validate_file

EMPTY_FILE_MD5 = "d41d8cd98f00b204e9800998ecf8427e"


class TestValidateFile:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.tmp = mkdtemp()
        self.file = join(self.tmp, "-somefile-")

    def test_invalid_if_not_exists(self):
        with assert_raises(FileNotFoundError):
            validate_file(self.file)

    def test_valid_if_exists(self):
        create_file(self.file)

        validate_file(self.file)

    def test_invalid_if_md5_mismatch(self):
        create_file(self.file)

        with assert_raises(ValueError):
            validate_file(self.file, ":wrong-md5:")

    def test_valid_by_md5(self):
        create_file(self.file)

        validate_file(self.file, EMPTY_FILE_MD5)

    def test_valid_by_md5_file(self):
        create_file(self.file)
        md5_file = join(self.tmp, "my.md5")
        safe_write(EMPTY_FILE_MD5, md5_file, append=False)

        validate_file(self.file, md5_file)
