import json

from lxml.html import Element
from lxml.cssselect import CSSSelector
import os
from webleaf.Neighbour import Neighbour


class Leaf:
    """An HTML element as described by a dict of paths to its closest neighbors"""

    def __init__(self):
        self.neighbours = set()
        self.branches = set()
        self.hash = hash("none")

    def __repr__(self):
        return f"Leaf(neighbours={list(self.neighbours)})"

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def from_element(self, tree, element: Element, depth: int = 4, breadth: int = 8):
        """
        Create a Leaf object from a LXML element to a specified depth.
        :param breadth: the amount of siblings to explore
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
                for sibling in parent[:breadth]:
                    if tree.getpath(sibling) != tree.getpath(tag):
                        stack.append((sibling, path + ['..', os.path.basename(tree.getpath(sibling))]))
            else:  # going down
                for child in tag[:breadth]:
                    stack.append((child, path + [os.path.basename(tree.getpath(child))]))

            if tag.text and tag.tag != "script" and tag.text.strip():
                str_hash = "/".join(str(edge) for edge in path)
                self.neighbours.add(Neighbour(depth=len(path), path=str_hash, tag=tag.tag, text=tag.text))
                self.neighbours.add(Neighbour(depth=len(path), path=str_hash, tag=tag.tag, text=tag.text, notext=True))
        self.hash = hash(str(list(self.neighbours)))
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

    def find_closest_leaves(self):
        close = {}
        for neighbour in self.neighbours:
            for other_leaf in neighbour.leaves:
                close[other_leaf] += 1
        return sorted(close)

