from typing import List


class DataFilter:
    def __init__(self, white_list: List[str], black_list: List[str]):
        self.black_list = black_list
        for whitelisted in white_list:
            if whitelisted in self.black_list:
                self.black_list.remove(whitelisted)

    def is_filtered(self, id_: str):
        return id_ in self.black_list
