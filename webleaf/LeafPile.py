from webleaf import Branch, Leaf
import random

from webleaf.Bundle import Bundle

NUM_LEAVES = 16
THRESHOLD = 0.7


class LeafPile:
    def __init__(self):
        self.neighbours = {}
        self.leaves = {}
        self.branches = {}

    def segment(self, branch, leaf_depth):
        for sub in branch.element.iter():
            if sub.text and len(sub.text.strip()) and sub.tag not in ["script", "style"]:
                leaf = Leaf().from_element(branch.tree, sub, leaf_depth)
                if leaf not in self.leaves:
                    self.leaves[leaf] = leaf
                self.leaves[leaf].branches.add(branch)
                for neighbour in leaf.neighbours:
                    if neighbour not in self.neighbours:
                        self.neighbours[neighbour] = neighbour
                    self.neighbours[neighbour].leaves.add(leaf)
                branch.leaves.add(leaf)
                branch.text_values[leaf] = sub.text
        if len(branch.leaves):
            self.branches[branch] = branch

    def bundle(self):
        clusters = []
        paired = set()
        for i, branch in enumerate(self.branches):
            print(f"{i} / {len(self.branches)}")
            if branch in paired:
                continue
            paired.add(branch)
            close = {}
            for leaf in sample(branch.leaves, NUM_LEAVES):
                for neighbour in self.leaves[leaf].neighbours:
                    for other_leaf in self.neighbours[neighbour].leaves:
                        factor = pow(1.5, - neighbour.depth) / (len(self.leaves[other_leaf].neighbours))
                        if other_leaf != leaf:
                            for other_branch in self.leaves[other_leaf].branches:
                                if other_branch not in paired:
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
                if score > THRESHOLD:
                    new_cluster.branches.append(other_branch)
                    paired.add(other_branch)
            clusters.append(new_cluster)

        bundles = []
        for bundle in sorted(clusters, key=lambda x: len(x.branches) * len(self.branches[x.branches[0]].leaves),
                             reverse=True):
            if len(bundle.branches) * len(self.branches[bundle.branches[0]].leaves) < 8:
                break
            bundles.append(bundle)
        return bundles

    def extract(self, bundle, leaf_depth):
        first_branch = self.branches[bundle.branches[0]]
        first_leaves = first_branch.leaves
        rows = []

        for b, branch in enumerate(bundle.branches):
            subpile = LeafPile()
            subpile.segment(branch, leaf_depth)
            subpile.segment(first_branch, leaf_depth)
            row = []
            for l, first_leaf in enumerate(first_leaves):
                print(f"branch {b+1} / {len(bundle.branches)} leaf {l+1} / {len(first_leaves)}")
                leaf_options = {}
                for neighbour in subpile.leaves[first_leaf].neighbours:
                    for other_leaf in subpile.neighbours[neighbour].leaves:
                        if branch in subpile.leaves[other_leaf].branches:
                            if other_leaf not in leaf_options:
                                leaf_options[other_leaf] = 0
                            leaf_options[other_leaf] += 1
                best_leaf = sorted(leaf_options, key=lambda x: leaf_options[x], reverse=True)
                if len(best_leaf):
                    row.append(subpile.branches[branch].text_values[best_leaf[0]])
                else:
                    row.append("")
            rows.append(row)
        return rows


def sample(items, num):
    if len(items) <= num:
        return items
    else:
        return random.sample(items, num)
