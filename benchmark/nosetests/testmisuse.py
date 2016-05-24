from typing import Dict, Union

from benchmark.misuse import Misuse

class TMisuse(Misuse):
    
    def __init__(self, path: str, meta: Dict[str, Union[str, Dict]]):
        Misuse.__init__(self, path)
        self._META = meta
