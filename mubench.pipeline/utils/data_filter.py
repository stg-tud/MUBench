from typing import List


class DataFilter:
    def __init__(self, white_list: List[str], black_list: List[str]):
        self.black_list = black_list
        self.white_list = white_list

    def is_filtered(self, id_: str):
        blacklisted = id_ in self.black_list
        whitelisted = not self.white_list or self._is_whitelisted(id_)
        return blacklisted or not whitelisted

    def _is_whitelisted(self, id_: str):
        return id_ in self.white_list if '.' not in id_ \
            else self._is_whitelisted(id_.rsplit('.', 1)[0])
