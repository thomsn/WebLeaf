from .Leaf import Leaf


class Branch:
    def __init__(self, path):
        self.hash = hash(path)
        self.path = path
        self.leaves = set()

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()
