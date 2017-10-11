from typing import List


class DataFilter:
    def __init__(self, white_list: List[str], black_list: List[str]):
        self.black_list = black_list
        self.white_list = white_list

    def is_filtered(self, id_: str):
        blacklisted = id_ in self.black_list
        whitelisted = not self.white_list or id_ in self.white_list
        return blacklisted or not whitelisted
