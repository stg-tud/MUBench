import os
from os.path import splitext, basename, normpath

from config import Config


def extract_project_name_from_file_path(file: str) -> str:
    """
    Extracts the project name from a given file path, using '.' as a separator (<path>/<project>.<rest>)
    :param file: The file path (should be in the form "<path>/<project>.<rest>" or "<path>/synthetic-<rest>")
    :rtype: str
    :return: The project name
    """
    project_name = splitext(basename(file))[0]
    if 'synthetic' not in project_name and '.' in project_name:
        project_name = project_name.split('.', 1)[0]
    return project_name


def normalize_data_misuse_path(misuse_file: str) -> str:
    """
    Normalizes the misuse file path (from a data file)
    :param misuse_file: The path that is given in the data file
    :rtype: str
    :return: The normalized path (can be compared to normalized result paths)
    """
    normed_misuse_file = normpath(misuse_file)

    # cut trunk folder (only for svn repositories)
    if 'trunk' + os.sep in normed_misuse_file:
        normed_misuse_file = normed_misuse_file.split('trunk' + os.sep, 1)[1]

    return normed_misuse_file


def normalize_result_misuse_path(misuse_file: str) -> str:
    """
    Normalizes the misuse file path (from a result file)
    :param misuse_file: The path that is given in the result file
    :rtype: str
    :return: The normalized path (can be compared to normalized data paths)
    """
    normed_misuse_file = normpath(misuse_file)

    # cut everything before project subfolder
    checkout_dir_prefix = Config.CHECKOUT_DIR + os.sep
    if checkout_dir_prefix in normed_misuse_file:
        normed_misuse_file = normed_misuse_file.split(checkout_dir_prefix, 1)[1]

    # cut project subfolder
    if os.sep in normed_misuse_file:
        normed_misuse_file = normed_misuse_file.split(os.sep, 1)[1]

    # cut trunk folder (only for svn repositories)
    if 'trunk' + os.sep in normed_misuse_file:
        normed_misuse_file = normed_misuse_file.split('trunk' + os.sep, 1)[1]

    return normed_misuse_file
