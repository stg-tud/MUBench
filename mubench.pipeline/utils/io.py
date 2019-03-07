import logging
import zipfile
from os import makedirs, chmod, remove, listdir, readlink, symlink, stat, walk
from os.path import dirname, exists, isfile, join, isdir, basename, islink, relpath
from shutil import rmtree, copy
from stat import S_IWRITE
from typing import Dict, List

import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def safe_write(content: str, file_path: str, append: bool) -> None:
    mode = 'a+' if append else 'w+'
    with safe_open(file_path, mode) as file:
        print(content, file=file)


def safe_read(file_path: str) -> str:
    with open(file_path, 'r', encoding="utf-8") as file:
        return file.read()


def safe_open(file_path: str, mode: str, newline: str = None):
    create_file_path(file_path)
    return open(file_path, mode, newline=newline, encoding="utf-8")


def create_file_path(file_path: str) -> None:
    makedirs(dirname(file_path), exist_ok=True)


def create_file(file_path: str, truncate: bool = False) -> None:
    create_file_path(file_path)
    mode = 'w+' if truncate else 'a+'
    open(file_path, mode, encoding="utf-8").close()


def is_empty(file_path: str) -> bool:
    return exists(file_path) and stat(file_path).st_size == 0


def remove_tree(root: str) -> None:
    if not exists(root):
        return

    # noinspection PyUnusedLocal
    def retry_remove(func, path, _):
        if exists(path):
            chmod(path, S_IWRITE)
            remove(path)

    rmtree(root, onerror=retry_remove)


def copy_tree(src: str, dst: str) -> None:
    if not exists(src): raise FileNotFoundError("Cannot copy non-existent file or directory '{}'.".format(src))
    makedirs(dst, exist_ok=True)

    for content in [join(src, content) for content in listdir(src)]:
        if islink(content):
            link_target = readlink(content)
            link_name = basename(content)
            symlink(link_target, join(dst, link_name))
        elif isdir(content):
            directory_name = join(dst, basename(content))
            makedirs(directory_name, exist_ok=True)
            copy_tree(content, directory_name)
        elif isfile(content):
            copy(content, dst)
        else:
            raise UserWarning("unknown file type: {}".format(content))


class __MultilineString(str):
    pass


def __multiline_string_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
yaml.add_representer(__MultilineString, __multiline_string_presenter)


def write_yaml(data: Dict, file: str = None):
    return __write_yaml(data, yaml.dump, file)


def write_yamls(data: List[Dict], file: str = None):
    return __write_yaml(data, yaml.dump_all, file)


def __write_yaml(data, dump, file):
    data = __escape_str(data)
    if file:
        create_file(file)
        with open(file, "w", encoding="utf-8") as stream:
            return dump(data, stream, Dumper=Dumper, default_flow_style=False, encoding="utf-8")
    else:
        return dump(data, Dumper=Dumper, default_flow_style=False)


def __escape_str(data):
    if isinstance(data, str):
        if "\n" in data:
            return __MultilineString(data)
        else:
            return data
    elif isinstance(data, dict):
        new = dict()
        for key in data:
            new[key] = __escape_str(data[key])
        return new
    elif isinstance(data, list):
        return [__escape_str(item) for item in data]
    else:
        return data


def read_yaml(file: str):
    with open(file, 'rU', encoding="utf-8") as stream:
        return yaml.load(stream, Loader=Loader)


def read_yaml_if_exists(file: str):
    return read_yaml(file) if exists(file) else {}


class open_yamls:
    def __init__(self, filename: str):
        self.filename = filename
        self._file = None

    def __enter__(self):
        self._file = open(self.filename, 'rU', encoding="utf-8")
        return yaml.load_all(self._file)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file.close()


class open_yamls_if_exists(open_yamls):
    def __enter__(self):
        return open_yamls.__enter__(self) if exists(self.filename) else []

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file:
            open_yamls.__exit__(self, exc_type, exc_val, exc_tb)


def zip_dir_contents(sources: List[str], destination: str):
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
        for source in sources:
            for root, dirs, files in walk(source):
                for file in files:
                    file_path = join(root, file)
                    file_path_in_archive = relpath(file_path, source)
                    if not any(file == file_path_in_archive for file in archive.namelist()):
                        archive.write(file_path, file_path_in_archive)
                    else:
                        logger = logging.getLogger("io.zip_dir_contents")
                        logger.debug("File conflict in zip {}: {}".format(destination, file_path_in_archive))
