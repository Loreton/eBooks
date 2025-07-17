#! /usr/bin/env python3
# updated by ...: Loreto Notarantonio
# Date .........: 17-07-2025 14.21.09
#

import sys; sys.dont_write_bytecode=True
import re


from html.parser import HTMLParser
import ebooklib
from ebooklib import epub


def read_epub(fileIn: str, fileOut: str):
    book = epub.read_epub(fileIn)
    content = ""

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            bodyContent = item.get_body_content().decode()
            f = HTMLFilter()
            f.feed(bodyContent)
            content += f.text

    with open(fileOut, 'w', encoding='utf-8') as fout:
        fout.write(content)
