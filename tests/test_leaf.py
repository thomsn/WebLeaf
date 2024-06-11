import pytest
from webleaf import Leaf
from bs4 import BeautifulSoup


EXAMPLE_PATH = "example.html"


example = open(EXAMPLE_PATH).read()
soup = BeautifulSoup(example, "html.parser")


def test_leaf_from_element():
    link = soup.find("p")
    leaf = Leaf().from_element(link, 3)
    assert leaf == {"0.1", "0.3.1", "0.3.2"}


def test_leaf_from_str():
    leaf = Leaf().from_str("0.1 0.2 0.3 1.0.3.2")
    assert leaf == {"0.1", "0.2", "0.3", "1.0.3.2"}


def test_leaf_equal():
    descriptions = list(soup.find_all("p"))
    assert len(descriptions) == 3, "soup wasn't loaded correctly."

    leaves = [Leaf().from_element(target, 3) for target in descriptions]

    assert len(leaves) == 3, "didn't create enough leaves"
    assert len(str(leaves[0])), "the leaf didn't have anything in it"
    assert len(set(str(leaf) for leaf in leaves)) == 1, "the leaves weren't the same."


def test_leaf_unique():
    link = soup.find("a")
    date = soup.find("span")

    link_leaf = Leaf().from_element(link, 3)
    assert len(str(link_leaf))

    date_leaf = Leaf().from_element(date, 3)
    assert len(str(date_leaf))

    assert link_leaf != date_leaf, "the leaves for the link and date should not be the same"


depths = [
    (1, ""),
    (2, "0.1"),
    (3, "0.1 0.3.1 0.3.2"),
    (4, "0.1 0.3.1 0.3.2 0.0.2.1 0.0.3.1"),
    (5, "0.1 0.3.1 0.3.2 0.0.2.1 0.0.3.1 0.0.2.2.1 0.0.2.3.1 0.0.2.3.2 0.0.3.2.1 0.0.3.3.1 0.0.3.3.2"),
]


@pytest.mark.parametrize("depth,expected", depths)
def test_leaf_depths(depth, expected):
    element = soup.find("p")
    expected_leaf = Leaf().from_str(expected)
    leaf = Leaf().from_element(element, depth)
    assert leaf == expected_leaf, "leaf was not as expected"


def test_leaf_compare():
    link = soup.find("a")
    desc = soup.find("p")

    link_leaf = Leaf().from_element(link, 4)
    assert len(str(link_leaf))

    desc_leaf = Leaf().from_element(desc, 4)
    assert len(str(desc_leaf))

    compare = desc_leaf.compare(link_leaf)
    assert compare < 1.0
