from bs4 import Tag
from webleaf.bfs_utils import element_text


class Leaf(set[str]):
    """An HTML element as described by a set of paths to its closest neighbors"""
    def from_element(self, tag: Tag, depth: int = 5):
        """
        Create a Leaf object from a BeautifulSoup tag to a specified depth. This walks the tree in a breadth first
        search. The path is encoded with 0 representing up in the tree; 1,2,3 ... representing the 1-indexed index of an
        element.
        :param tag: the BeautifulSoup tag
        :param depth: the integer depth to traverse within the tree
        :return: a Leaf()
        """
        stack = [(tag, [])]
        while len(stack):
            tag, path = stack.pop(0)
            if len(path) > depth:
                continue
            going_up = not path or path[-1] == 0
            parent = tag.parent
            if parent and going_up:
                stack.append((parent, path + [0]))
                for index, sibling in enumerate(parent.findChildren(recursive=False)):
                    if sibling != tag:
                        stack.append((sibling, path + [index + 1]))
            else:  # going down
                for index, child in enumerate(tag.findChildren(recursive=False)):
                    stack.append((child, path + [index + 1]))
            if element_text(tag) and tag.name != "script" and path:
                str_hash = ".".join(str(edge) for edge in path)
                self.add(str_hash)
        return self

    def from_str(self, string: str):
        """
        Create a Leaf()® from a string.
        :param string: the Leaf in string format
        :return: a Leaf()
        """
        for path in string.split(" "):
            if path:
                self.add(path)
        return self

    def compare(self, other) -> float:
        """
        Compare two Leaves and produce a score. Closer neighbors are weighted exponentially more than further neighbors.
        :param other: the Leaf to compare to
        :return: a score between 1.0 and 0.0 representing how similar the Leaves are.
        """
        diffs = self.symmetric_difference(other)
        score = 1.0
        for diff in diffs:
            depth = diff.count(".") + 1
            factor = (1.0 - pow(2, - depth))
            score = score * factor
        return score

    def __str__(self):
        """
        Serialize a Leaf to a string.
        :return: String representation of the Leaf()
        """
        return " ".join(self)
