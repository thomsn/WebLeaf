import unicodedata
import jellyfish
from html import unescape
from bs4 import BeautifulSoup, Tag


class Tree(dict):
    def __init__(self, depth=5):
        super().__init__()
        self.depth = depth

    def load(self, soup: BeautifulSoup):
        # builds the hashtable for all elements so lookup is faster
        for element in soup.find_all():
            text = element.find(text=True, recursive=False)
            if text and element.name != "script":
                new_id = self.id(element)
                if new_id:
                    self[new_id] = self.get(new_id, []) + [element]

    def id(self, element: Tag) -> str:
        stack = [(element, [])]
        paths = []
        while len(stack):
            tag, path = stack.pop(0)
            if len(path) > self.depth:
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

            text = tag.find(text=True, recursive=False)
            if text:
                text = unescape(text.text)
                text = unicodedata.normalize('NFKC', text).strip()
            if text and tag.name != "script" and path:
                paths.append(path)
        str_hash = ""
        for path in paths:
            for addr in path:
                str_hash = str_hash + str(addr)
            str_hash += " "
        return str_hash

    def similar(self, this_id, ratio=0.8) -> str:
        for option in self:
            if self[this_id][0].name == self[option][0].name:
                match = (1 - float(jellyfish.levenshtein_distance(this_id, option))/len(this_id))
                if match > ratio:
                    yield option
