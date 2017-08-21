from typing import Dict, List, Optional

from utils.io import read_yaml


def get_datasets(datasets_file_path: str) -> Dict[str, List[str]]:
    return read_yaml(datasets_file_path)


def get_available_datasets(datasets_file_path: str) -> List[str]:
    datasets = read_yaml(datasets_file_path)
    return list(datasets.keys())


def get_white_list(datasets_file_path: str, dataset_key: Optional[str]) -> List[str]:
    if dataset_key is None:
        return []

    datasets = read_yaml(datasets_file_path)
    if dataset_key not in datasets:
        raise ValueError("Invalid dataset: '{}'".format(dataset_key))
    return datasets[dataset_key]
