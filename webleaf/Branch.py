from .Leaf import Leaf


class Branch:
    def __init__(self, path):
        self.hash = hash(path)
        self.path = path
        self.leaves = set()
        self.text_values = {}

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __str__(self):
        value_string = "\n".join(self.text_values.values())
        return f"{self.path}\n{len(self.leaves)} leaves\n{value_string}"
