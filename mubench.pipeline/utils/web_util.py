import getpass
import hashlib
import json
import mimetypes
import shutil
from contextlib import ExitStack
from typing import List
from urllib.request import urlopen
from os import remove
from os.path import exists, basename

import requests


def download_file(url: str, file: str, md5_checksum: str = None):
    """
    Downloads a file from a give URL.
    :param url: the URL to download from, must yield a file
    :param file: the destination to save the file to
    :param md5_checksum: a checksum to validate the file with
    """
    with urlopen(url) as response, open(file, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

    try:
        validate_file(file, md5_checksum)
    except:
        remove(file)
        raise


def is_valid_file(file_path: str, md5_checksum: str = None):
    """
    Checks if the file exists and, if a checksum is provided, whether the file's checksum matches.
    :param file_path: the file to validate
    :param md5_checksum: the MD5 checksum or MD5-checksum file
    :return: True, if the file is valid, False otherwise
    """
    try:
        validate_file(file_path, md5_checksum)
        return True
    except (FileNotFoundError, ValueError):
        return False


def validate_file(file_path: str, md5_checksum: str = None):
    """
    Checks if the file exists and, if a checksum is provided, whether the file's checksum matches. Raises an exception,
    if the file is invalid.
    :param file_path: the file to validate
    :param md5_checksum: the MD5 checksum or MD5 checksum file
    """
    if not exists(file_path):
        raise FileNotFoundError("file not found '{}'".format(file_path))
    if md5_checksum:
        __check_md5(file_path, md5_checksum)


def __check_md5(file, md5_checksum):
    if exists(md5_checksum):
        # assume we are provided an md5 file
        with open(md5_checksum, 'r') as md5_file:
            md5_checksum = md5_file.read().rstrip("\n")

    file_checksum = __compute_md5(file)
    if not md5_checksum == file_checksum:
        raise ValueError("invalid MD5 checksum '{}', expected '{}'".format(file_checksum, md5_checksum))
    else:
        return True


# source: http://stackoverflow.com/a/3431838
def __compute_md5(file: str):
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def post(url: str, data: object, file_paths: List[str] = None, username: str="", password: str=""):
    request = {
        "url": url,
        "data": json.dumps(data)
    }

    if username:
        if not password:
            password = getpass.getpass("Enter password for '{}': ".format(username))
        request["auth"] = (username, password)

    with ExitStack() as es:
        if file_paths:
            request["data"] = {"data": request["data"]}
            request["files"] = [__create_file_tuple(path, es) for path in file_paths]

        response = requests.post(**request)
        response.raise_for_status()


def __create_file_tuple(path: str, es: ExitStack):
    filename = basename(path)
    file_handle = es.enter_context(open(path, 'rb'))
    mime_type = mimetypes.guess_type(path)[0]
    return filename, (filename, file_handle, mime_type)
