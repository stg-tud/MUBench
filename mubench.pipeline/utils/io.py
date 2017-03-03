from os import makedirs, chmod, remove, listdir, readlink, symlink
from os.path import dirname, exists, isfile, join, isdir, basename, islink
from shutil import rmtree, copy
from stat import S_IWRITE
from typing import Dict

import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def safe_write(content: str, file_path: str, append: bool) -> None:
    mode = 'a+' if append else 'w+'
    with safe_open(file_path, mode) as file:
        print(content, file=file)


def safe_open(file_path: str, mode: str, newline: str = None):
    create_file_path(file_path)
    return open(file_path, mode, newline=newline, encoding="utf-8")


def create_file_path(file_path: str) -> None:
    makedirs(dirname(file_path), exist_ok=True)


def create_file(file_path: str, truncate: bool = False) -> None:
    create_file_path(file_path)
    mode = 'w+' if truncate else 'a+'
    open(file_path, mode, encoding="utf-8").close()


def remove_tree(root: str) -> None:
    if not exists(root):
        return

    # noinspection PyUnusedLocal
    def retry_remove(func, path, _):
        if exists(path):
            chmod(path, S_IWRITE)
            try:
                remove(path)
            except PermissionError:
                pass

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
    data = __escape_str(data)
    if file:
        create_file(file)
        with open(file, "w", encoding="utf-8") as stream:
            return yaml.dump(data, stream, Dumper=Dumper, default_flow_style=False, encoding="utf-8")
    else:
        return yaml.dump(data, Dumper=Dumper, default_flow_style=False)


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
    with open(file, "rU", encoding="utf-8") as stream:
        return yaml.load(stream, Loader=Loader)


def read_yamls(file: str):
    with open(file, 'rU', encoding="utf-8") as stream:
        return yaml.load_all(stream, Loader=Loader)
