from bs4 import Tag
import unicodedata
from html import unescape


class Leaf(list):
    def from_element(self, element: Tag, depth=5):
        stack = [(element, [])]
        paths = []
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

            text = tag.find(text=True, recursive=False)
            if text:
                text = unescape(text.text)
                text = unicodedata.normalize('NFKC', text).strip()
            if text and tag.name != "script" and path:
                paths.append(path)
        for path in paths:
            str_hash = "".join(str(edge) for edge in path)
            self.append(str_hash)
        return self

    def compare(self, other):
        diffs = set(self).symmetric_difference(set(other))
        score = 1.0
        for diff in diffs:
            factor = (1.0 - pow(2, -len(diff)))
            score = score * factor
        return score

    def __str__(self):
        return " ".join(self)
