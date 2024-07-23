import json
import math
import os
import random

from lxml import etree

from . import Leaf
from .Bundle import Bundle
from .Branch import Branch
import csv
from .LeafPile import LeafPile
from multiprocessing import Pool

from openai import OpenAI

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

    def extract(self, bundles, pile):
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
            yield cleaned_rows

    def label(self, sheets):
        key_name = "OPENAI"
        key = os.environ[key_name]
        assert key, f"Please specify {key_name} environment variable to perform labeling"
        client = OpenAI(api_key=key)

        for sheet in sheets:
            column_count = len(sheet[0])
            CHUNK_SIZE = 16
            MAX_CHARS = 100
            column_names = []
            column_importance = []
            for chunk in range(math.ceil(column_count / CHUNK_SIZE)):
                chunk_data = []
                for row_i in range(3):
                    chunk_data.append([text[:MAX_CHARS] for text in sheet[row_i][chunk*CHUNK_SIZE:(chunk+1)*CHUNK_SIZE]])
                prompt = [{
                    "role": "system",
                    "content": "You are a spreadsheet expert. Your job is to label each column in this spreadsheet. "
                               "Your output must be a JSON object with the key [column_labels] and the value "
                               "of a list of column labels. Additionally, add the JSON object with key [column_importance] "
                               "and the value of a list of integers with 1 = not important and 10 = very important."
                },
                    {
                        "role": "user",
                        "content": json.dumps(chunk_data)
                    }
                ]
                response = json.loads(client.chat.completions.create(
                    messages=prompt,
                    model="gpt-4-1106-preview",
                    response_format={"type": "json_object"},
                    max_tokens=1000
                ).choices[0].message.content)
                chunk_column_names = response["column_labels"]
                chunk_column_importance = [int(imp) for imp in response["column_importance"]]
                assert len(chunk_column_names) == len(chunk_data[0])
                assert len(chunk_column_importance) == len(chunk_data[0])
                column_names.extend(chunk_column_names)
                column_importance.extend(chunk_column_importance)

            sheet.insert(0, column_names)
            # Create a list of (importance, column index) pairs
            importance_with_index = list(enumerate(column_importance))

            # Sort the list of (importance, column index) pairs by importance
            sorted_importance_with_index = sorted(importance_with_index, key=lambda x: x[1], reverse=True)

            # Extract the column indices in the new order
            sorted_indices = [index for index, _ in sorted_importance_with_index]

            # Reorder the rows based on the sorted column indices
            yield (f"some_name{len(column_names)}", [[row[i] for i in sorted_indices] for row in sheet])

    def export(self, sheets):
        for sheet_name, rows in sheets:
            with open(f"{sheet_name}.csv", "w+") as f:
                csv.writer(f).writerows(rows)
