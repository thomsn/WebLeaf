import math
from lxml import etree

from .Branch import Branch
from .Leaf import Leaf
import csv
from multiprocessing import Pool

MAX_DEPTH = 20
DEPTH = 7
THRESHOLD = 0.7


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
        branches = []
        for single_html in self.html:
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
            for element in divs:
                branch = Branch(element, tree, DEPTH)
                if len(branch):
                    branches.append(branch)
        return branches

    def compare(self, branches):
        # p = Pool(11)
        self.branches = branches
        return map(self.compare_branches, branches)

    def compare_branches(self, branch):
        branch_diffs = []
        for other_branch in self.branches:
            branch_diffs.append(branch.compare(other_branch))
        return branch_diffs

    def bundle(self, branch_diffs):
        clusters = []
        paired = set()

        for i, div in enumerate(branch_diffs):
            if i in paired:
                continue
            new_cluster = [i]
            for j, other_div in enumerate(div):
                if i == j:
                    continue
                if j in paired:
                    continue
                if other_div > THRESHOLD:
                    new_cluster.append(j)
                    paired.add(j)
            clusters.append(new_cluster)
            paired.add(i)

        bundles = []
        for cluster in sorted(clusters, key=lambda x: len(x) * len(self.branches[x[0]]), reverse=True):
            if len(cluster) * len(self.branches[cluster[0]]) < 8:
                break
            bundles.append(cluster)
        return bundles

    def export(self, sorted_clusters, div_leaves):
        for i, cluster in enumerate(sorted_clusters):
            first_leaves = div_leaves[cluster[0]]
            rows = []
            for div in cluster:
                row = []
                other_leaves = div_leaves[div]
                for leaf in first_leaves:
                    best_match = other_leaves[0]
                    best_score = leaf.compare(best_match)
                    for other_leaf in other_leaves:
                        score = leaf.compare(other_leaf)
                        if score > best_score:
                            best_match = other_leaf
                            best_score = score
                    row.append(best_match['.']['text'])
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