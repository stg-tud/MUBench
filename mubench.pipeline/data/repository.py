from typing import Optional


class Repository:
    def __init__(self, vcstype: str, url: Optional[str] = None,
                 username: Optional[str] = None, password: Optional[str] = None):
        self.vcstype = vcstype
        self.url = url
        self.username = username
        self.password = password
