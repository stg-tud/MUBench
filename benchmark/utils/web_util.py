import hashlib
import shutil
import urllib
from os.path import exists

from typing import Optional

from benchmark.utils.io import create_file_path


def download(url: str, file: str, md5_file: Optional[str] = None) -> bool:
    create_file_path(file)

    with urllib.request.urlopen(url) as response, open(file, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

    if not exists(file):
        return False


# source: http://stackoverflow.com/a/3431838
def _md5(file: str):
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
