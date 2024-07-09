from .Leaf import Leaf

NUM_LEAVES_TO_COMPARE = 16


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
            return [0.0] * len(self)

        leaves_compare = []
        for leaf in self:
            # todo: do the other direction comparison as well

            difference = max(map(leaf.compare, other))
            leaves_compare.append(difference)
        return leaves_compare
