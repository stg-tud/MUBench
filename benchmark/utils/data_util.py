from typing import Optional


def normalize_result_misuse_path(misuse_file: str, checkout_dir: str, src_prefix: Optional[str]) -> str:
    normed_misuse_file = misuse_file.replace('\\', '/')
    checkout_dir = checkout_dir.replace('\\', '/')

    # cut everything before project subfolder
    checkout_dir_prefix = checkout_dir + '/'
    if checkout_dir_prefix in normed_misuse_file:
        normed_misuse_file = normed_misuse_file.split(checkout_dir_prefix, 1)[1]

    # cut trunk folder (only for svn repositories)
    if 'trunk/' in normed_misuse_file:
        normed_misuse_file = normed_misuse_file.split('trunk/', 1)[1]

    # cut src prefix
    if src_prefix and src_prefix in normed_misuse_file:
        normed_misuse_file = normed_misuse_file.split(src_prefix, 1)[1]

    return normed_misuse_file
