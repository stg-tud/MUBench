import hashlib
import shutil
import urllib
from os import remove
from os.path import exists

from typing import Optional

from benchmark.utils.printing import print_ok


def load_detector(url: str, file: str, md5_file: Optional[str] = None) -> None:
    print("Loading detector... ", end='')

    try:
        with urllib.request.urlopen(url) as response, open(file, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    except ValueError:
        exit("error! Invalid URL: {}".format(url))
    except urllib.error.URLError:
        exit("error! Could not connect to {}".format(url))

    if not exists(file):
        exit("error! Detector could not be loaded.")

    if md5_file is not None:
        if not exists(md5_file):
            remove(file)
            exit("error! '{}' does not exist. Cannot verify download.".format(md5_file))
        elif not __check_md5(file, md5_file):
            remove(file)
            exit("error! Detector corrupted (md5 mismatch).")

    print_ok()


def download_file(url: str, file: str, md5_checksum: str = None):
    """
    Downloads a file from a give URL.
    :param url: the URL to download from, must yield a file
    :param file: the destination to save the file to
    :param md5_checksum: a checksum to validate the file with
    """
    with urllib.request.urlopen(url) as response, open(file, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

    try:
        validate_file(file, md5_checksum)
    except:
        remove(file)
        raise


def validate_file(file_path: str, md5_checksum: str = None):
    """
    Checks if the file exists and, if a checksum or checksum file is provided, whether the files checksum matches.
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
