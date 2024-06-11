from webleaf.Tree import Tree
from bs4 import BeautifulSoup, Tag


EXAMPLE_PATH = "example.html"


def test_tree():
    example = open(EXAMPLE_PATH).read()
    soup = BeautifulSoup(example, "html.parser")
    tree = Tree(depth=2).load(soup)
    print(tree)
