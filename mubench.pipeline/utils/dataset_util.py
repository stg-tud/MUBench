from typing import Dict, List, Optional

from utils.io import read_yaml


def get_available_datasets(datasets_file_path: str) -> Dict[str, List[str]]:
    return read_yaml(datasets_file_path)


def get_available_dataset_ids(datasets_file_path: str) -> List[str]:
    datasets = __get_lowercase_datasets(datasets_file_path)
    return datasets.keys()


def get_white_list(datasets_file_path: str, dataset_key: str) -> List[str]:
    datasets = __get_lowercase_datasets(datasets_file_path)
    if dataset_key not in datasets:
        raise ValueError("Invalid dataset: '{}'".format(dataset_key))
    return datasets[dataset_key]


def __get_lowercase_datasets(datasets_file_path: str) -> Dict[str, List[str]]:
    datasets = read_yaml(datasets_file_path)
    return {k.lower(): [e.lower() for e in v] for k, v in datasets.items()}
