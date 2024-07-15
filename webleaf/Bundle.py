from .Branch import Branch


class Bundle:
    def __init__(self):
        self.branches = []

    def __str__(self):
        return f"{len(self.branches)} branches"
