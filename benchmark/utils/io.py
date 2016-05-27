from os import makedirs
from os.path import dirname


def safe_write(content: str, file_path: str, append: bool) -> None:
    mode = 'a+' if append else 'w+'
    with safe_open(file_path, mode) as file:
        print(content, file=file)


def safe_open(file_path: str, mode: str):
    create_file_path(file_path)
    return open(file_path, mode)


def create_file_path(file_path: str) -> None:
    makedirs(dirname(file_path), exist_ok=True)


def create_file(file_path: str, truncate: bool = False) -> None:
    create_file_path(file_path)
    mode = 'w+' if truncate else 'a+'
    open(file_path, mode).close()
