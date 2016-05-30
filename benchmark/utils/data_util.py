from typing import Optional


def normalize_data_misuse_path(misuse_file: str, src_prefix: Optional[str]) -> str:
    normed_misuse_file = misuse_file

    # cut trunk folder (only for svn repositories)
    if 'trunk/' in normed_misuse_file:
        normed_misuse_file = normed_misuse_file.split('trunk/', 1)[1]

    # cut src prefix
    if src_prefix is not None and src_prefix in normed_misuse_file:
        normed_misuse_file = normed_misuse_file.split(src_prefix, 1)[1]

    return normed_misuse_file


def normalize_result_misuse_path(misuse_file: str, checkout_base_dir: str, src_prefix: Optional[str]) -> str:
    normed_misuse_file = misuse_file.replace('\\', '/')
    checkout_base_dir = checkout_base_dir.replace('\\', '/')

    # cut everything before project subfolder
    checkout_dir_prefix = checkout_base_dir + '/'
    if checkout_dir_prefix in normed_misuse_file:
        normed_misuse_file = normed_misuse_file.split(checkout_dir_prefix, 1)[1]

    # cut project subfolder
    if '/' in normed_misuse_file:
        normed_misuse_file = normed_misuse_file.split('/', 1)[1]

    # cut trunk folder (only for svn repositories)
    if 'trunk/' in normed_misuse_file:
        normed_misuse_file = normed_misuse_file.split('trunk/', 1)[1]

    # cut src prefix
    if src_prefix is not None and src_prefix in normed_misuse_file:
        normed_misuse_file = normed_misuse_file.split(src_prefix, 1)[1]

    return normed_misuse_file
