import pytest
from webleaf import Leaf, Neighbour
from lxml import etree
import os

dirname = os.path.dirname(__file__)

EXAMPLE_PATH = os.path.join(dirname, "example.html")

example = open(EXAMPLE_PATH).read()
root = etree.HTML(example)
tree = etree.ElementTree(root)


def test_leaf_from_element():
    link = tree.findall(".//p")[0]
    leaf = Leaf().from_element(tree, link, 3)
    assert leaf == {'.': {'path': '.', 'tag': 'p',
                          'text': 'Description for card 1. This card provides details about the first item.'},
                    './../../h3': {'path': './../../h3', 'tag': 'h3', 'text': 'Title 1'}}


def test_leaf_from_dict():
    dictionary = {'.': {'path': '.',
                        'tag': 'p',
                        'text': 'Description for card 1. This card provides details about the '
                                'first item.'}}
    leaf = Leaf(dictionary)
    assert leaf == dictionary


def test_leaf_equal():
    descriptions = tree.findall(".//p")
    assert len(descriptions) == 3, "wasn't loaded correctly."

    leaves = [Leaf().from_element(tree, target, 3) for target in descriptions]

    assert len(leaves) == 3, "didn't create enough leaves"
    assert len(str(leaves[0])), "the leaf didn't have anything in it"
    assert len(set(str(leaf.keys()) for leaf in leaves)) == 1, "the leaves weren't the same."


def test_leaf_unique():
    link = tree.findall(".//a")[0]
    date = tree.findall(".//span")[0]

    link_leaf = Leaf().from_element(tree, link, 3)
    assert len(str(link_leaf))

    date_leaf = Leaf().from_element(tree, date, 3)
    assert len(str(date_leaf))

    assert link_leaf != date_leaf, "the leaves for the link and date should not be the same"


depths = [
    (1, {'.': {'path': '.', 'tag': 'p',
               'text': 'Description for card 1. This card provides details about the first item.'}}),
    (2, {'.': {'path': '.', 'tag': 'p',
               'text': 'Description for card 1. This card provides details about the first item.'}}),
    (3, {'.': {'path': '.', 'tag': 'p',
               'text': 'Description for card 1. This card provides details about the first item.'},
         './../../h3': {'path': './../../h3', 'tag': 'h3', 'text': 'Title 1'}}),
    (4, {'.': {'path': '.', 'tag': 'p',
               'text': 'Description for card 1. This card provides details about the first item.'},
         './../../div[2]/a': {'path': './../../div[2]/a', 'tag': 'a', 'text': 'Learn more'},
         './../../div[2]/span': {'path': './../../div[2]/span','tag': 'span', 'text': 'June 10, 2024'},
         './../../h3': {'path': './../../h3', 'tag': 'h3', 'text': 'Title 1'}}),
    (5, {'.': {'path': '.', 'tag': 'p',
               'text': 'Description for card 1. This card provides details about the first item.'},
         './../../../div[2]/h3': {'path': './../../../div[2]/h3', 'tag': 'h3', 'text': 'Title 2'},
         './../../../div[3]/h3': {'path': './../../../div[3]/h3','tag': 'h3', 'text': 'Title 2'},
         './../../div[2]/a': {'path': './../../div[2]/a','tag': 'a', 'text': 'Learn more'},
         './../../div[2]/span': {'path': './../../div[2]/span', 'tag': 'span', 'text': 'June 10, 2024'},
         './../../h3': {'path': './../../h3', 'tag': 'h3', 'text': 'Title 1'}}),
]


@pytest.mark.parametrize("depth,expected", depths)
def test_leaf_depths(depth, expected):
    element = tree.findall(".//p")[0]
    expected_leaf = Leaf(expected)
    leaf = Leaf().from_element(tree, element, depth)
    assert leaf == expected_leaf, "leaf was not as expected"


def test_leaf_compare():
    link = tree.findall(".//a")[0]
    desc = tree.findall(".//p")[0]

    link_leaf = Leaf().from_element(tree, link, 4)
    assert len(str(link_leaf))

    desc_leaf = Leaf().from_element(tree, desc, 4)
    assert len(str(desc_leaf))

    compare = desc_leaf.compare(link_leaf)
    assert compare < 1.0


def test_leaf_path():
    link = tree.findall(".//a")[0]

    link_leaf = Leaf().from_element(tree, link, 4)
    for path in link_leaf:
        elements = link.xpath(path)
        assert len(elements), "could not find the path from the leaf"
        assert elements[0].text, "the path from the leaf did not have a text value"


def test_leaf_xpath():
    xpath = "/html/body/div[1]/div[1]/h3"
    title = tree.findall(".//h3")[0]
    expected = Leaf().from_element(tree, title)
    title_leaf = Leaf().from_xpath(tree, xpath)
    assert expected == title_leaf, "did not find css selector correctly"


def test_leaf_css():
    css = "div.card:nth-child(1) > h3:nth-child(1)"
    title = tree.findall(".//h3")[0]
    expected = Leaf().from_element(tree, title)
    title_leaf = Leaf().from_css(tree, css)
    assert expected == title_leaf, "did not find css selector correctly"


def test_leaf_find():
    titles = tree.findall(".//h3")

    for i, title_element in enumerate(Leaf().from_element(tree, titles[0]).find(tree)):
        if i >= len(titles):
            break
        assert title_element.tag == "h3", "did not find titles correctly"
