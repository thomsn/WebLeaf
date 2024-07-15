import math
import random

from lxml import etree

from . import Leaf
from .Bundle import Bundle
from .Branch import Branch
import csv
from multiprocessing import Pool

MAX_DEPTH = 20
DEPTH = 7
THRESHOLD = 0.7
NUM_LEAVES = 16


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
                depth_divs[max_depth] = divs

        last_metric = 0
        depth_diffs = {}
        for depth in sorted(list(depth_divs.keys())):
            a = depth_divs[depth]
            metric = 0
            for x in a:
                if x:
                    metric += math.log(x, 10)
            diff = metric - last_metric
            depth_diffs[depth] = diff
            last_metric = metric

        chosen_depth = max(depth_diffs, key=depth_diffs.get)
        return chosen_depth

    def segment(self, chosen_depth):
        neighbours = {}
        leaves = {}
        branches = {}
        for html_number, single_html in enumerate(self.html):
            root = etree.HTML(single_html)
            tree = etree.ElementTree(root)
            stack = [(tree.getroot(), 0)]
            divs = []
            while stack:
                current_element, depth = stack.pop(0)
                if depth < chosen_depth:
                    for element in current_element:
                        stack.append((element, depth + 1))
                else:
                    divs.append(current_element)
            for i, element in enumerate(divs):
                branch = Branch(f"{html_number} {tree.getpath(element)}")
                for sub in element.iter():
                    if sub.text and len(sub.text.strip()) and sub.tag not in ["script", "style"]:
                        leaf = Leaf().from_element(tree, sub, DEPTH)
                        if leaf not in leaves:
                            leaves[leaf] = leaf
                        leaves[leaf].branches.add(branch)
                        for neighbour in leaf.neighbours:
                            if neighbour not in neighbours:
                                neighbours[neighbour] = neighbour
                            neighbours[neighbour].leaves.add(leaf)
                        branch.leaves.add(leaf)
                        branch.text_values[leaf] = sub.text
                if len(branch.leaves):
                    branches[branch] = branch
        return branches, leaves, neighbours

    def bundle(self, branches, leaves, neighbours):
        clusters = []
        paired = set()
        for i, branch in enumerate(branches):
            print(f"{i} / {len(branches)}")
            if branch in paired:
                continue
            close = {}
            for leaf in sample(branch.leaves, NUM_LEAVES):
                for neighbour in leaves[leaf].neighbours:
                    for other_leaf in neighbours[neighbour].leaves:
                        factor = pow(1.5, - neighbour.depth) / (len(leaves[other_leaf].neighbours))
                        if other_leaf != leaf:
                            for other_branch in leaves[other_leaf].branches:
                                if other_branch != branch:
                                    if other_branch not in close:
                                        close[other_branch] = {}
                                    if leaf not in close[other_branch]:
                                        close[other_branch][leaf] = {}
                                    if other_leaf not in close[other_branch][leaf]:
                                        close[other_branch][leaf][other_leaf] = 0
                                    close[other_branch][leaf][other_leaf] += factor

            summed = {b: sum(max(close[b][l].values()) for l in close[b]) for b in close}

            other_branches = list(sorted(summed.items(), key=lambda x: x[1], reverse=True))
            new_cluster = Bundle()
            new_cluster.branches.append(branch)
            for other_branch, score in other_branches:
                if other_branch in paired:
                    continue
                if score > THRESHOLD:
                    new_cluster.branches.append(other_branch)
                    paired.add(other_branch)
            paired.add(branch)
            clusters.append(new_cluster)

        bundles = []
        for bundle in sorted(clusters, key=lambda x: len(x.branches) * len(branches[x.branches[0]].leaves), reverse=True):
            if len(bundle.branches) * len(branches[bundle.branches[0]].leaves) < 8:
                break
            bundles.append(bundle)
        return bundles

    def export(self, bundles, branches, leaves, neighbours):
        for i, bundle in enumerate(bundles):
            first_leaves = branches[bundle.branches[0]].leaves
            for leaf in first_leaves:
                print(branches[bundle.branches[0]].text_values[leaf])
            rows = []
            for b, branch in enumerate(bundle.branches):
                print(f"branch {b+1} / {len(bundle.branches)}")
                row = []
                for l, first_leaf in enumerate(first_leaves):
                    print(f"leaf {l}")
                    leaf_options = {}
                    for neighbour in leaves[first_leaf].neighbours:
                        for other_leaf in neighbours[neighbour].leaves:
                            if branch in leaves[other_leaf].branches:
                                if other_leaf not in leaf_options:
                                    leaf_options[other_leaf] = 0
                                leaf_options[other_leaf] += 1
                    best_leaf = sorted(leaf_options, key=lambda x: leaf_options[x], reverse=True)
                    if len(best_leaf):
                        row.append(branch.text_values[best_leaf[0]])
                    else:
                        row.append("")
                rows.append(row)

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


def sample(items, num):
    if len(items) <= num:
        return items
    else:
        return random.sample(items, num)
