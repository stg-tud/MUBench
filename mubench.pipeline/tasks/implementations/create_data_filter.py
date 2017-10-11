from typing import List

from utils.data_filter import DataFilter


class CreateDataFilter:
    def __init__(self, white_list: List[str], black_list: List[str]):
        self.data_filter = DataFilter(white_list, black_list)

    def run(self):
        return [self.data_filter]
