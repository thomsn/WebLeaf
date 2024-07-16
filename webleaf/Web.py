import math
import random

from lxml import etree

from . import Leaf
from .Bundle import Bundle
from .Branch import Branch
import csv
from .LeafPile import LeafPile
from multiprocessing import Pool

MAX_DEPTH = 20
DEPTH = 7


class Web:
    def __init__(self, html):
        self.div_leaves = None
        if isinstance(html, str):
            self.html = [html]
        else:
            self.html = html

    def plan_segment(self):
        depth_divs = {}
        for single_html in self.html:
            root = etree.HTML(single_html)
            tree = etree.ElementTree(root)

            for max_depth in range(MAX_DEPTH):
                divs = []
                stack = [(tree.getroot(), 0)]
                while stack:
                    current_element, depth = stack.pop(0)
                    if depth < max_depth:
                        for element in current_element:
                            stack.append((element, depth + 1))
                    else:
                        count = 0
                        for el in current_element.iter():
                            if el.text:
                                count += 1
                        divs.append(count)
                if max_depth not in depth_divs:
                    depth_divs[max_depth] = divs
                else:
                    depth_divs[max_depth].extend(divs)

        last_metric = 1
        depth_diffs = {}
        for depth in sorted(list(depth_divs.keys())):
            a = depth_divs[depth]
            metric = 0
            for x in a:
                if x:
                    metric += max(math.log(x, 10), 0)
            diff = metric / last_metric
            last_metric = metric
            if depth == 0:
                continue
            depth_diffs[depth] = diff

        chosen_depth = max(depth_diffs, key=depth_diffs.get)
        return chosen_depth

    def segment(self, chosen_depth):
        pile = LeafPile()
        for html_number, single_html in enumerate(self.html):
            root = etree.HTML(single_html)
            tree = etree.ElementTree(root)
            stack = [(root, 0)]
            while stack:
                current_element, depth = stack.pop(0)
                if depth < chosen_depth:
                    for element in current_element:
                        stack.append((element, depth + 1))
                else:
                    branch = Branch(tree.getpath(current_element), current_element, tree, html_number)
                    pile.segment(branch, DEPTH)
        return pile

    def bundle(self, pile):
        return pile.bundle()

    def export(self, bundles, pile):
        for i, bundle in enumerate(bundles):

            rows = pile.extract(bundle, DEPTH)

            cleaned_rows = []
            changed = [False] * len(rows[0])
            for row in rows:
                for j, entry in enumerate(row):
                    if entry != rows[0][j]:
                        changed[j] = True
            for row in rows:
                cleaned_row = []
                for j, entry in enumerate(row):
                    if changed[j]:
                        cleaned_row.append(entry)
                cleaned_rows.append(cleaned_row)

            if not len(cleaned_rows) or not len(cleaned_rows[0]):
                continue

            with open(f"cluster{i}.csv", "w+") as f:
                csv.writer(f).writerows(cleaned_rows)
