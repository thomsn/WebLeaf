import hashlib


class Neighbour:
    def __init__(self, depth: int, path: str, tag: str = "", text: str = "", notext = False):
        self.string_value = f"{path} {tag} {'' if notext  else text}"
        self.text = text
        self.value = hash(self.string_value)
        self.leaves = set()
        self.depth = depth

    def __repr__(self):
        return f"{self.value}"

    def __hash__(self):
        return self.value

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()
