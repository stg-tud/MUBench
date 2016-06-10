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
        exit("error! Invalid detector URL: {}".format(url))
    except urllib.error.URLError:
        exit("error! Could not connect to server on {}".format(url))

    if not exists(file):
        exit("error! Detector could not be loaded.")

    if md5_file is not None and not _check_md5(file, md5_file):
        remove(file)
        exit("error! Incorrect md5; detector was not loaded correctly.")

    print_ok()


def _check_md5(file, reference_file):
    actual_md5 = _md5(file)
    with open(reference_file, 'r') as reference_md5_file:
        reference_md5 = reference_md5_file.read().rstrip("\n")
    return reference_md5 == actual_md5


# source: http://stackoverflow.com/a/3431838
def _md5(file: str):
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


class InvalidURLError(Exception):
    pass


class ConnectionFailedError(Exception):
    pass
