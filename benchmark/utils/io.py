from os import makedirs, chmod, remove, listdir
from os.path import dirname, exists, isfile, join, isdir, basename

from shutil import rmtree, copy
from stat import S_IWRITE


def safe_write(content: str, file_path: str, append: bool) -> None:
    mode = 'a+' if append else 'w+'
    with safe_open(file_path, mode) as file:
        print(content, file=file)


def safe_open(file_path: str, mode: str, newline: str = None):
    create_file_path(file_path)
    return open(file_path, mode, newline=newline)


def create_file_path(file_path: str) -> None:
    makedirs(dirname(file_path), exist_ok=True)


def create_file(file_path: str, truncate: bool = False) -> None:
    create_file_path(file_path)
    mode = 'w+' if truncate else 'a+'
    open(file_path, mode).close()


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
    contents = [join(src, content) for content in listdir(src)]

    for content in contents:
        if isfile(content):
            makedirs(dst, exist_ok=True)
            copy(content, dst)
        elif isdir(content):
            copy_tree(content, join(dst, basename(content)))
