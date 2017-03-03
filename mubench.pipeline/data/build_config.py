from typing import List


class BuildConfig:
    def __init__(self, src: str, commands: List[str], classes: str):
        self.src = src
        self.commands = commands
        self.classes = classes

    def __eq__(self, other):
        return isinstance(other, BuildConfig) and \
               self.src == other.src and \
               self.commands == other.commands and \
               self.classes == other.classes

    def __hash__(self):
        return hash(self.src + "".join(self.commands) + self.classes)

    def __str__(self):
        return "[src: {}, classes: {}, commands: {}]".format(self.src, self.classes, self.commands)
