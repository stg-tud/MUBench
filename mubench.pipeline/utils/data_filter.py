from typing import List


class DataFilter:
    def __init__(self, white_list: List[str], black_list: List[str]):
        self.white_list = white_list
        self.black_list = black_list

    def is_filtered(self, id_: str):
        blacklisted = self._is_blacklisted(id_)
        whitelisted = not self.white_list or self._is_whitelisted(id_)
        return blacklisted or not whitelisted

    def _is_blacklisted(self, id_: str):
        return any(id_.startswith(blacklisted) for blacklisted in self.black_list)

    def _is_whitelisted(self, id_: str):
        return any(id_.startswith(whitelisted) for whitelisted in self.white_list) or \
               any(whitelisted.startswith(id_) for whitelisted in self.white_list)
