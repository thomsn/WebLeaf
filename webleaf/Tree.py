import jellyfish
from bs4 import BeautifulSoup


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
        return self

    def similar(self, this_id, ratio=0.8) -> str:
        for option in self:
            if self[this_id][0].name == self[option][0].name:
                match = (1 - float(jellyfish.levenshtein_distance(this_id, option))/len(this_id))
                if match > ratio:
                    yield option
