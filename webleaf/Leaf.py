from bs4 import Tag

from webleaf.bfs_utils import element_text


class Leaf(set):
    def from_element(self, element: Tag, depth=5):
        stack = [(element, [])]
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
                str_hash = "".join(str(edge) for edge in path)
                self.add(str_hash)
        return self

    def from_str(self, string):
        for path in string.split(" "):
            if path:
                self.add(path)
        return self

    def compare(self, other):
        diffs = self.symmetric_difference(other)
        score = 1.0
        for diff in diffs:
            factor = (1.0 - pow(2, -len(diff)))
            score = score * factor
        return score

    def __str__(self):
        return " ".join(self)
