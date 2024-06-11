from bs4 import Tag
import unicodedata
from html import unescape


def element_text(element: Tag):
    text = element.find(text=True, recursive=False)
    if text:
        text = unescape(text.text)
        text = unicodedata.normalize('NFKC', text).strip()
    return text
