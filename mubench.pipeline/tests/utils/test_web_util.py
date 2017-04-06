import io
from os.path import join, exists
from pathlib import Path
from tempfile import mkdtemp
from unittest.mock import patch, MagicMock
from urllib.error import URLError

from nose.tools import assert_raises, assert_equals
from requests import Response

from utils.io import create_file, safe_write
from utils.web_util import validate_file, download_file, is_valid_file, post

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

    def test_is_invalid(self):
        assert not is_valid_file(self.file)

    def test_is_valid(self):
        create_file(self.file)

        assert is_valid_file(self.file)


class TestDownloadFile:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.tmp = mkdtemp()
        self.remote_file = join(self.tmp, "remote.file")
        create_file(self.remote_file)
        self.url = Path(self.remote_file).as_uri()

        self.target = join(self.tmp, "local.file")

    def test_downloads_file(self):
        download_file(self.url, self.target)

        assert exists(self.target)

    def test_raises_on_invalid_url(self):
        with assert_raises(ValueError):
            download_file(":invalid-url:", self.target)

    def test_raises_on_unavailable(self):
        with assert_raises(URLError):
            download_file("http://unavailable.sven-amann.de/file", self.target)

    def test_validates_download(self):
        download_file(self.url, self.target, EMPTY_FILE_MD5)

        assert exists(self.target)

    def test_invalidates_download(self):
        with assert_raises(ValueError):
            download_file(self.url, self.target, ":wrong-md5:")

        assert not exists(self.target)


@patch("requests.post")
class TestPost:
    def test_post_data(self, post_mock):
        post("-url-", "-data-")

        post_mock.assert_called_with(url="-url-", data='"-data-"')

    def test_post_auth(self, post_mock):
        post("-url-", "-data-", username="user", password="pw")

        assert_equals(post_mock.call_args[1]["auth"], ("user", "pw"))

    @patch("builtins.open")
    def test_post_with_files(self, open_mock, post_mock):
        mock_file = io.StringIO("-file-content-")
        open_mock.return_value = mock_file

        post("-url-", "-data-", file_paths=["/fake/file/path.png"])

        args = post_mock.call_args
        assert_equals(args[1]["data"], {"data": '"-data-"'})
        assert_equals(args[1]["files"], [("path.png", ("path.png", mock_file, "image/png"))])

    @patch("utils.web_util.getpass.getpass")
    def test_post_with_auth(self, pass_mock, post_mock):
        pass_mock.return_value = "-password-"

        post("-url-", "-data-", username="-username-")

        assert_equals(post_mock.call_args[1]["auth"], ("-username-", "-password-"))

    def test_post_access_denied(self, post_mock):
        response = MagicMock(spec=Response)
        response.raise_for_status.side_effect = UserWarning()
        post_mock.return_value = response

        with assert_raises(UserWarning):
            post("-url-", "-data-")
