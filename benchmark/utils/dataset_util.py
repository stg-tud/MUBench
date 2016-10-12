from typing import List

from benchmark.utils.io import read_yaml


def get_white_list(datasets_file_path: str, dataset_key: str) -> List[str]:
    datasets = read_yaml(datasets_file_path)
    if dataset_key not in datasets:
        raise ValueError("Invalid dataset: '{}'".format(dataset_key))
    return datasets[dataset_key]

