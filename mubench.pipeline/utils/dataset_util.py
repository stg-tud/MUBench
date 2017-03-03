from typing import List, Optional

from utils.io import read_yaml


def get_white_list(datasets_file_path: str, dataset_key: Optional[str]) -> List[str]:
    if dataset_key is None:
        return []

    datasets = read_yaml(datasets_file_path)
    if dataset_key not in datasets:
        raise ValueError("Invalid dataset: '{}'".format(dataset_key))
    return datasets[dataset_key]
