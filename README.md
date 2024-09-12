<p align="center">
  <img src="https://github.com/thomsn/WebLeaf/raw/main/docs/logo.webp" alt="WebLeaf Logo" style="width: 62%;">
</p>

# 🌿 WebLeaf - A Graph-Based HTML Parsing and Comparison Tool

[![PyPI version](https://badge.fury.io/py/webleaf.svg)](https://badge.fury.io/py/webleaf)  
[![Build Status](https://travis-ci.org/yourusername/webleaf.svg?branch=main)](https://travis-ci.org/yourusername/webleaf)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**WebLeaf** is a Python package that brings the power of **graph neural networks (GNNs)** to HTML parsing and element comparison. It encodes HTML elements into feature-rich graph embeddings, allowing for advanced tasks like element extraction, structural comparison, and distance measurement between elements. WebLeaf is perfect for web scraping, semantic HTML analysis, and automated web page comparison tasks.

## Key Features

- 🌟 **Graph-Based HTML Representation**: Treats the HTML structure as a graph, encoding elements as nodes and relationships as edges.
- 📄 **Tag and Text Embeddings**: Leverages embeddings for both HTML tags and textual content to capture meaningful semantic and structural representations.
- 🔍 **Element Extraction**: Retrieve elements using XPath or CSS selectors.
- 🛠️ **Element Comparison**: Measure similarity between elements based on their content and structure using graph embeddings.
- 📈 **Pretrained GCN Model**: Built on top of a pretrained **Graph Convolutional Network (GCN)**, enabling rich semantic and structural analysis out of the box.

## Installation

You can install WebLeaf using pip:

```bash
pip install webleaf
```

## How It Works

WebLeaf represents an HTML document as a **graph**, where each HTML element is a node, and the parent-child relationships between elements form the edges of the graph. The graph is then processed by a **GCN (Graph Convolutional Network)** that creates embeddings for each HTML element. These embeddings capture both the semantic content and structural relationships of the elements, allowing for tasks like element comparison, similarity measurement, and extraction.

The model also combines **tag embeddings** (representing HTML tags) and **text embeddings** (representing the textual content of elements), creating a powerful representation of the HTML page.

## Basic Usage

Here's a quick example of how to use WebLeaf:

```python
from webleaf import Web

# Load your HTML content
html_content = open('example.html').read()

# Create a Web object
web = Web(html_content)

# Extract an element using XPath
leaf = web.leaf(xpath=".//p")

# Extract an element using CSS selectors
leaf_css = web.leaf(css_select="div.card:nth-child(1) > div:nth-child(2) > p:nth-child(1)")

# Compare two elements
similarity = leaf.similarity(leaf_css)
print(f"Similarity: {similarity}")
>>> Similarity: 1.0

# Find the closest match for an element
path = web.find(leaf)
print(f"Element found at: {path}")
>>> Element found at: /html/body/div/div/div[1]/div[1]/p
```

### Advanced Features

- **Find Similar Elements**: You can also find the top `n` most similar elements to a given one:

    ```python
    similar_paths = web.find_n(leaf, n=3)
    print(f"Top 3 similar elements: {similar_paths}")
    >>> Top 3 similar elements: ['/html/body/div/div/div[1]/div[1]/p', '/html/body/div/div/div[2]/div[1]/p', '/html/body/div/div/div[3]/div[1]/span']

    ```
  

- **Distance Measurement**: Measure how unique or similar two elements are using `mdist()`:

    ```python
    distance = leaf.mdist(leaf_css)
    print(f"Distance: {distance}")
   >>>
  Distance: 0.0
    ```

## API Documentation

### `Web(html)`
- **Description**: Initializes the WebLeaf model with the HTML content, parses the document, and encodes it into a graph representation.
- **Arguments**:
  - `html` (str): The HTML content as a string.

### `leaf(xpath=None, css_select=None)`
- **Description**: Retrieves an HTML element as a `Leaf` object using either an XPath or CSS selector.
- **Arguments**:
  - `xpath` (str): The XPath of the desired element.
  - `css_select` (str): The CSS selector for the desired element.

### `similarity(leaf)`
- **Description**: Computes the similarity score between two `Leaf` objects based on their embeddings.
- **Returns**: A similarity score between 0 and 1.

### `mdist(leaf)`
- **Description**: Measures the "distance" between two `Leaf` objects, representing how unique or different they are.

### `find(leaf)`
- **Description**: Finds the closest match for a given `Leaf` object within the HTML structure.
- **Returns**: The XPath of the closest matching element.

### `find_n(leaf, n)`
- **Description**: Finds the top `n` most similar elements to a given `Leaf` object, sorted by similarity.
- **Returns**: A list of XPaths for the top `n` most similar elements.

## Running Tests

WebLeaf comes with a suite of unit tests to ensure everything works as expected. These tests cover basic operations like element extraction, similarity comparisons, and graph encoding. To run the tests:

1. Clone this repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Run the tests using `pytest`:

```bash
pytest
```

## Example Test

```python
def test_leaf_extraction():
    web = Web(example_html)
    leaf = web.leaf(xpath=".//p")
    assert leaf

def test_element_comparison():
    web = Web(example_html)
    leaf1 = web.leaf(xpath=".//p")
    leaf2 = web.leaf(css_select="div.card:nth-child(1) > div:nth-child(2) > p:nth-child(1)")
    assert leaf1.similarity(leaf2) > 0.9
```

## Pretrained Model

The WebLeaf model uses a pretrained **Graph Convolutional Network (GCN)** that has been trained on a diverse set of web pages to learn the structure and semantic relationships within HTML. The model is loaded from `product_page_model_4_80.torch` and is used to encode HTML elements into embeddings.

## Performance

<p align="center">
  <img src="https://github.com/thomsn/WebLeaf/raw/main/docs/tsne.png" alt="WebLeaf Performance" style="width: 62%;">
</p>
This t-SNE (t-Distributed Stochastic Neighbor Embedding) plot provides a 2D visualization of the WebLeaf-encoded web elements, which have been projected into a lower-dimensional space. The purpose of t-SNE is to represent high-dimensional data (such as the embeddings generated by WebLeaf) in two dimensions, allowing us to better visualize relationships and groupings among different types of web elements.

## Contributing

We welcome contributions! Feel free to submit issues, feature requests, or pull requests. Here's how you can contribute:

1. Fork the repository.
2. Create your feature branch: `git checkout -b feature/new-feature`.
3. Commit your changes: `git commit -m 'Add new feature'`.
4. Push to the branch: `git push origin feature/new-feature`.
5. Open a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

🌿 **WebLeaf** is a powerful and flexible tool for working with HTML as structured graph data. Give it a try and start leveraging the power of graph neural networks for your web scraping and analysis needs!