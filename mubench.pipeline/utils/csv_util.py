import csv
from typing import List, Dict

from utils.io import safe_open


def write_table(file: str, headers: List[str], content: Dict[str, Dict[str, str]]):
    with safe_open(file, 'w+', newline='') as result_file:
        w = csv.DictWriter(result_file, fieldnames=headers)
        w.writeheader()
        for row_key in sorted(content):
            print(row_key, end='', file=result_file)
            w.writerow({column_key: content[row_key].get(column_key, '') for column_key in headers[1:]})


def read_table(file: str, row_key: str) -> Dict[str, Dict[str, str]]:
    result = dict()

    with open(file, 'r') as source:
        r = csv.DictReader(source)
        for row in r:
            key = row.pop(row_key)
            row = {k: v for k, v in row.items() if v}  # remove all empty values
            result[key] = row

    return result
