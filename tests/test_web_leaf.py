from webleaf import Web
import os

dirname = os.path.dirname(__file__)

EXAMPLE_PATH = os.path.join(dirname, "example.html")

example = open(EXAMPLE_PATH).read()


def test_leaf_from_xpath():
    web = Web(example)
    leaf = web.leaf(xpath=".//p")
    assert leaf


def test_leaf_from_css():
    web = Web(example)
    leaf = web.leaf(css_select="div.card:nth-child(1) > div:nth-child(2) > p:nth-child(1)")
    assert leaf


def test_leaf_equal():
    web = Web(example)
    leaf1 = web.leaf(css_select="div.card:nth-child(1) > div:nth-child(2) > p:nth-child(1)")
    leaf2 = web.leaf(xpath="/html/body/div[1]/div/div[1]/div[1]/p")
    similarity = leaf1.similarity(leaf2)
    assert similarity > 0.99


def test_leaf_unique():
    web = Web(example)
    description = web.leaf(xpath="/html/body/div[1]/div/div[1]/div[1]/p")
    date = web.leaf(xpath='/html/body/div[1]/div/div[1]/div[2]/span')
    distance = description.mdist(date)
    assert distance > 0.1


def test_leaf_similar():
    web = Web(example)
    link1 = web.leaf(xpath="/html/body/div[1]/div/div[1]/div[2]/a")
    link2 = web.leaf(xpath="/html/body/div[1]/div/div[2]/div[2]/a")
    distance = link1.mdist(link2)
    assert distance < 0.1


def test_leaf_similar_but_different():
    web = Web(example)
    description_p = web.leaf(xpath="/html/body/div[1]/div/div[1]/div[1]/p")
    description_span = web.leaf(xpath="/html/body/div[1]/div/div[3]/div[1]/span")
    distance = description_p.mdist(description_span)
    assert distance < 1.0


def test_leaf_find():
    web = Web(example)
    path = "/html/body/div/div/div[3]/h3"
    link1 = web.leaf(xpath=path)
    found = web.find(link1)
    assert found == path


def test_leaf_find_n():
    web = Web(example)
    date_leaf = web.leaf(xpath="/html/body/div[1]/div/div[1]/div[1]/p")
    paths = web.find_n(date_leaf, 3)
    for path in ["/html/body/div/div/div[1]/div[1]/p",
                 "/html/body/div/div/div[2]/div[1]/p",
                 "/html/body/div/div/div[3]/div[1]/span"]:
        assert path in paths
