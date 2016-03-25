from os import makedirs
from os.path import dirname


def safe_write(content: str, file_path: str, append: bool):
    """
    Writes the given string to a file. Creates the path and file, if they don't exist.
    :param content: The content to be written into the file
    :param file_path: The path to the target file
    :param append: If the written string should be appended, or overwrite existing text
    """
    mode = 'a+' if append else 'w+'
    with safe_open(file_path, mode) as file:
        print(content, file=file)


def safe_open(file_path: str, mode: str):
    """
    Creates the path to the file if doesn't exist and opens the file in the given mode.
    :param file_path: The path to the file to open
    :param mode: The mode in which the file will be opened
    :rtype: file
    :return: The opened file
    """
    create_file_path(file_path)
    return open(file_path, mode)


def create_file_path(file_path: str):
    """
    Creates all directories in the path and the files itself.
    :param file_path: The path to the file to be created
    """
    makedirs(dirname(file_path), exist_ok=True)


def create_file(file_path: str, truncate: bool = False):
    """
    Creates the file
    :param file_path: The path to the file to be created
    :param truncate: If the file should be truncated if it existed before
    """
    mode = 'w+' if truncate else 'a+'
    open(file_path, mode).close()
