import csv
from typing import List, Dict

from benchmark.utils.io import safe_open


def write_table(file: str, headers: List[str], content: Dict[str, Dict[str, str]]):
    with safe_open(file, 'w+') as result_file:
        w = csv.DictWriter(result_file, fieldnames=headers)
        w.writeheader()
        for row_key in sorted(content):
            print(row_key, end='', file=result_file)
            w.writerow({column_key: content[row_key].get(column_key) or '' for column_key in headers[1:]})
