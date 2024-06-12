<p align="center">
  <img src="https://github.com/thomsn/WebLeaf/raw/main/docs/logo.webp" alt="WebLeaf Logo" style="width: 100%;">
</p>

# WebLeaf Package
#### HTML DOM Tree Leaf Structure Identification Python Package 
Websites are generally built as a composition of components. If you understand the structure of a given website then you
can better understand the data within it. WebLeaf helps you classify elements within the DOM tree by creating a 
set representation of an element's neighbors. This set can then be used to develop robust data scraping logic. WebLeaf 
is an alternative to CSS selectors and XPaths which can often fail. 

### Install
To install the current release
```bash
pip install webleaf
```
### Basic
```python
from webleaf import Leaf
from bs4 import BeautifulSoup

def get_html():
    import requests
    website = requests.get("https://example.com/").text
    return website


html = get_html()
soup = BeautifulSoup(html)
element = soup.find("a")

leaf = Leaf().from_element(element, depth=3)
print(leaf)
```
output
```bash
0.1 0.2
```

### How it works
Here we will walk through the creation of a Leaf. The link "a" element Leaf of depth=3 has two neighbors [0.1] and [0.2] . 
WebLeaf will start from the element and breadth first search for a neighbouring element with text. When it finds a 
neighbour it will trace the relative path using 0 to represent upwards (parent) and 1,2,3... to represent the 1-indexed 
child index of an element. 
```html
<!doctype html>
</head>
    <body>
        <div>                                                                                        
<!-- 0.1 = 1st child --> <h1>Example Domain</h1>                                                            
<!-- 0.2 = 2nd child --> <p>This domain is for use in illustrative examples in documents....     </p>
<!--   0 = parent    --> <p>                                                                                
<!--starting element -->     <a href="https://www.iana.org/domains/example">More information...</a>
                         </p>
        </div>
    </body>
</html>
```

<em>"You become who you surround yourself with."</em> src: Someone Important
