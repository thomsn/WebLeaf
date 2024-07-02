import json

from lxml.html import Element
from lxml.cssselect import CSSSelector
import os
from webleaf.Neighbour import Neighbour


class Leaf(dict[str, Neighbour]):
    """An HTML element as described by a dict of paths to its closest neighbors"""

    def from_element(self, tree, element: Element, depth: int = 5):
        """
        Create a Leaf object from a LXML element to a specified depth. This walks the tree in a breadth first
        search. The path is encoded with 0 representing up in the tree; 1,2,3 ... representing the 1-indexed index of an
        element.
        :param tree: the lxml etree
        :param element: the lxml element
        :param depth: the integer depth to traverse within the tree
        :return: a Leaf()
        """
        stack = [(element, ["."])]
        while len(stack):
            tag, path = stack.pop(0)
            if len(path) - 1 > depth:
                continue
            going_up = path[-1] in [".", ".."]
            parent = tag.getparent()
            if parent is not None and going_up:
                stack.append((parent, path + [".."]))
                for sibling in parent:
                    if tree.getpath(sibling) != tree.getpath(tag):
                        stack.append((sibling, path + ['..', os.path.basename(tree.getpath(sibling))]))
            else:  # going down
                for child in tag:
                    stack.append((child, path + [os.path.basename(tree.getpath(child))]))
            if tag.text and tag.tag != "script" and tag.text.strip():
                str_hash = "/".join(str(edge) for edge in path)
                self[str_hash] = Neighbour(path=str_hash, tag=tag.tag, text=tag.text)
        return self

    def from_xpath(self, tree, xpath: str, depth: int = 5):
        """
        Create a Leaf from a XPath.
        :param tree: the lxml etree
        :param xpath: the xpath string
        :param depth: integer depth to build the Leaf,
        :return: the Leaf.
        """
        elements = tree.xpath(xpath)
        assert elements, f"no element found for xpath {xpath}"
        return self.from_element(tree, elements[0], depth)

    def from_css(self, tree, css, depth: int = 5):
        """
        Create a Leaf from a CSS selector.
        :param tree: the lxml etree
        :param css: the css string
        :param depth: integer depth to build the Leaf,
        :return: the Leaf.
        """
        xpath = CSSSelector(css).path
        elements = tree.xpath(xpath)
        assert elements, f"no element found for css {css}"
        return self.from_element(tree, elements[0], depth)

    def compare(self, other) -> float:
        """
        Compare two Leaves and produce a score. Closer neighbors are weighted exponentially more than further neighbors.
        Values that are different are slightly less
        :param other: the Leaf to compare to
        :return: a score between 1.0 and 0.0 representing how similar the Leaves are.
        """

        paths = set(self.keys()).union(set(other.keys()))
        score = 1.0

        for path in paths:
            depth = path.count("/")
            deduction = 0.0
            if bool(path in self) != bool(path in other):
                deduction += 1.0

            if path in self and path in other:
                for aspect in ['tag', 'text']:
                    if self[path][aspect] != other[path][aspect]:
                        deduction += 0.5

            factor = pow(4, - (depth + 1)) * deduction
            score = score - factor
        return max(score, 0.0)

    def __str__(self):
        """
        Serialize a Leaf to a string.
        :return: String representation of the Leaf()
        """
        return json.dumps(self)

    def find(self, tree, depth: int = 5):
        """
        Inefficient find matching leaves.
        :param tree: the lxml etree
        :param depth: the depth to construct leaves for
        :return: lxml element iterator
        """
        other_elements = []
        for element in tree.iter():
            other_leaf = Leaf().from_element(tree, element, depth)
            compare = self.compare(other_leaf)
            if element.text:
                other_elements.append((compare, element, other_leaf))

        for compare, element, leaf in sorted(other_elements, key=lambda x: x[0], reverse=True):
            yield element
