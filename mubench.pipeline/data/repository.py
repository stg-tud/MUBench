from typing import Optional


class Repository:
    def __init__(self, vcstype: Optional[str], url: Optional[str]):
        self.vcstype = vcstype  # type: Optional[str]
        self.url = url  # type: Optional[str]
