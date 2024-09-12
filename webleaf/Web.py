from .Leaf import Leaf
from .model.WebGraphAutoEncoder import WebGraphAutoEncoder
from lxml import etree
from lxml.cssselect import CSSSelector

# Global variable to hold the WebGraphAutoEncoder instance
web_graph_auto_encoder = None


class Web:
    """
    The Web class provides an interface for parsing and interacting with HTML content.
    It uses the WebGraphAutoEncoder to convert the HTML structure into graph-based embeddings,
    allowing for extraction and comparison of elements.

    Attributes:
    -----------
    html : str
        The raw HTML content passed during initialization.
    tree : lxml.etree.ElementTree
        Parsed HTML tree.
    features : list
        The encoded feature vectors for each HTML element.
    paths : list
        The XPath for each HTML element in the document.
    leaves : list of Leaf
        Leaf objects representing the elements of the HTML tree, based on their embeddings.
    path_leaves : dict
        A dictionary mapping XPaths to their corresponding Leaf objects.
    """
    def __init__(self, html: str):
        """
        Initialize the Web object by parsing the provided HTML and encoding it into embeddings.

        Parameters:
        -----------
        html : str
            The HTML content to be parsed and encoded.

        Raises:
        -------
        AssertionError if the HTML content is invalid.
        """
        global web_graph_auto_encoder
        self.html = html
        if not web_graph_auto_encoder:
            web_graph_auto_encoder = WebGraphAutoEncoder()
        self.tree = etree.ElementTree(etree.HTML(html))
        self.features, self.paths = web_graph_auto_encoder.extract(self.tree)
        self.leaves = [Leaf(feat) for feat in self.features]
        self.path_leaves = {path: leaf for path, leaf in zip(self.paths, self.leaves)}

    def leaf(self, xpath: str = "", css_select: str = "") -> Leaf:
        """
        Extracts a specific element from the HTML tree based on an XPath or CSS selector
        and returns it as a Leaf object.

        Parameters:
        -----------
        xpath : str, optional
            The XPath query to locate the element. (default is "")
        css_select : str, optional
            A CSS selector to locate the element. If provided, it is converted to XPath. (default is "")

        Returns:
        --------
        Leaf
            The corresponding Leaf object for the element.

        Raises:
        -------
        AssertionError if neither an XPath nor a CSS selector is provided, or if the element is not found.
        """
        if css_select:
            xpath = CSSSelector(css_select).path
        assert xpath, "When creating a WebLeaf please provide either a xpath or css selector."
        elements = self.tree.xpath(xpath)
        assert len(elements), f"Could not find elements at xpath [{xpath}] in html."
        path = self.tree.getpath(elements[0])
        assert path in self.path_leaves, f"The element at [{path}] was not processed by webleaf."
        return self.path_leaves[path]

    def find(self, leaf: Leaf):
        """
         Finds the closest matching element in the HTML tree for the given Leaf object.

         Parameters:
         -----------
         leaf : Leaf
             The Leaf object to be matched against the elements in the HTML tree.

         Returns:
         --------
         str
             The XPath of the closest matching element.
         """
        return self.find_n(leaf, 1)[0]

    def find_n(self, leaf: Leaf, n):
        """
        Finds the top N most similar elements to the given Leaf object,
        based on their embeddings' distance.

        Parameters:
        -----------
        leaf : Leaf
            The Leaf object to compare against other elements in the tree.
        n : int
            The number of top similar elements to return.

        Returns:
        --------
        list of str
            A list of XPaths corresponding to the top N most similar elements.
        """
        path_dists = [(path, leaf.mdist(other)) for other, path in zip(self.leaves, self.paths)]
        sorted_path_dists = sorted(path_dists, key=lambda path_dist: path_dist[1])
        sorted_paths = [path for path, dist in sorted_path_dists]
        return sorted_paths[:n]
