from .Leaf import Leaf
import random

NUM_LEAVES_TO_COMPARE = 8


class Branch(list[Leaf]):
    def __init__(self, element, tree, depth):
        super().__init__()
        for sub in element.iter():
            if sub.text:
                leaf = Leaf().from_element(tree, sub, depth)
                if '.' in leaf:
                    self.append(leaf)

    def compare(self, other):
        if not (len(self) * 0.3 < len(other) < len(self) * 1.7):
            return 0.0

        leaves_compare = []
        for leaf in self.sample(NUM_LEAVES_TO_COMPARE):
            difference = max(map(leaf.compare, other))
            leaves_compare.append(difference)

        for leaf in other.sample(NUM_LEAVES_TO_COMPARE):
            difference = max(map(leaf.compare, self))
            leaves_compare.append(difference)

        return sum(leaves_compare) / len(leaves_compare)

    def sample(self, num):
        if len(self) <= num:
            return self
        else:
            return random.sample(self, num)
