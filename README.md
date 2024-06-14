<p align="center">
  <img src="https://github.com/thomsn/WebLeaf/raw/main/docs/logo.webp" alt="WebLeaf Logo" style="width: 100%;">
</p>

# WebLeaf Package
#### HTML DOM Tree Leaf Structure Identification Python Package 
Websites are generally built as a composition of components. If you understand the structure of a given website then you
can better understand the data within it. WebLeaf helps you classify elements within the DOM tree by creating a 
dict representation of an element's neighbors. This dict can then be used to develop robust data scraping logic. WebLeaf 
is an alternative to CSS selectors and XPaths which can often fail. 

### Install
To install the current release
```bash
pip install webleaf
```
### Basic
Here we will compute the Leaf for the link "a" element in example.com
```python
from webleaf import Leaf
from lxml import etree

def get_html():
    import requests
    website = requests.get("https://example.com/").text
    return website


html = get_html()
root = etree.HTML(html)
tree = etree.ElementTree(root)

leaf = Leaf().from_xpath(tree, xpath=".//a", depth=3)
print(leaf)
```
output
```json
{"./../../h1": "Example Domain", "./../../p[1]": "This domain is for use in illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission."}
```
### Comparing Leaves
Leaves can be compared with each other, so you can find similar elements within the document. 
```python
from webleaf import Leaf

leaf_one = Leaf({"./../../h1": "Example Domain", "./../../p[1]": "example description"})
leaf_two = Leaf({"./../../h1": "Example Domain", "./../../p[1]": "example description modified"})
leaf_three = Leaf({"./../h1": "Example Domain", "./../../p[3]": "example description"})

print("compare leaf one and two", leaf_one.compare(leaf_two))
print("compare leaf one and three", leaf_one.compare(leaf_three))
```
output
```bash
compare leaf one and two 0.9375
compare leaf one and three 0.50244140625
```

### How it works
Here we will walk through the creation of a Leaf. The link "a" element Leaf of depth=3 has two neighbors "./../../h1" and 
 "./../../p[1]". WebLeaf will start from the element and breadth first search for a neighbouring element with text. When it finds a 
neighbour it will create a relative XPath to it. 
```html
<!doctype html>
    <body>
        <div>
            <h1>Example Domain</h1>                                                             <!--  ./../../h1  -->
            <p>This domain is for use in illustrative examples in documents....     </p>        <!-- ./../../p[1] -->
            <p>
                <a href="https://www.iana.org/domains/example">More information...</a>          <!--    start     -->
            </p>
        </div>
    </body>
</html>
```

<p align="center">
  <img src="https://github.com/thomsn/WebLeaf/raw/main/docs/WebLeaf.png" alt="WebLeaf How it Works" style="width: 80%;">
</p>

In the above DOM tree you can see how WebLeaf encoded the tree structure around the chosen element "a". This Leaf can 
then be used to locate the link.

<em>"You become who you surround yourself with."</em> src: Someone Important
