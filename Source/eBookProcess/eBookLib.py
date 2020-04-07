# xxx!/usr/bin/python3
# Progamma per processare un ebook
#
# updated by ...: Loreto Notarantonio
# Version ......: 07-04-2020 13.43.53
#

import os
from pathlib import Path

import ebooklib
from ebooklib import epub
from ebooklib.utils import parse_html_string
import ebooklib.utils as epubUtil
from bs4 import BeautifulSoup
import nltk
# nltk.download('punkt')




# https://pypi.org/project/EbookLib/
# https://medium.com/@zazazakaria18/turn-your-ebook-to-text-with-python-in-seconds-2a1e42804913
def epub2thtml(filename):
    """
    ritorna la lista dei capitoli in formato html
    """
    book = epub.read_epub(filename)
    chapters = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapters.append(item.get_content())
    return chapters


def chap2text(chap):
    # there may be more elements you don't want, such as "style", etc.
    blacklist = [   '[document]',   'noscript', 'header',   'html', 'meta', 'head','input', 'script',   ]
    output = ''
    soup = BeautifulSoup(chap, 'html.parser')
    text = soup.find_all(text=True)
    for t in text:
        if t.parent.name not in blacklist:
            output += '{} '.format(t)
    return output

def thtml2ttext(chapters):
    Output = []
    for html in chapters:
        text =  chap2text(html)
        Output.append(text)
    return Output

def epub2text(epub_path):
    chapters = epub2thtml(epub_path)
    text = thtml2ttext(chapters)
    return text

def search_string(substring, data):
    import re
    # All occurrences of substring in string
    res = [i.start() for i in re.finditer(substring, data)]
    return res

def eBookLib(gVars, file):
    global gv
    gv          = gVars
    Ln          = gv.Ln
    C           = gVars.Color
    lnLogger    = gv.lnLogger
    # strToSearch = gv.search

    this_book = {}
    lnLogger.info('working on file: {0}'.format(file))
    try:
        book = epub.read_epub(file)
    except Exception as why:
        C.error(text=str(why))
        Ln.prompt('continue....')
        return this_book


    _title       = book.get_metadata('DC', 'title')
    _creator     = book.get_metadata('DC', 'creator')
    _description = book.get_metadata('DC', 'description')
    _date        = book.get_metadata('DC', 'date')
    _identifier  = book.get_metadata('DC', 'identifier')
    _coverage    = book.get_metadata('DC', 'coverage')

    this_book['description'] = _description[0][0]           if _description else ''
    this_book['identifier']  = _identifier[0][0]            if _identifier else 'null'
    this_book['title']       = _title[0][0]                 if _title else Path(file).stem
    this_book['author']      = _creator[0][0]               if _creator else ""
    this_book['date']        = _date[0][0].split('T', 1)[0] if _date else ""
    this_book['coverage']    = _coverage
    # this_book['content']     = {}
    # this_book['content']['chapters'] = []
    # chaps = this_book['content']['chapters']

    this_book['content'] = []
    chaps = this_book['content']

    lnLogger.info('book data', this_book)

    chapters = epub2text(file)
    for chap in chapters:
        chaps.append(chap)
    return this_book

    '''
    STR_FOUND=False
    for chap in chapters:
        occurrencies = search_string(strToSearch, chap)
        if occurrencies:
            STR_FOUND=True
            for pos in occurrencies:
                lun=len(strToSearch)
                C.cyan(text=chap[pos-60:pos], end='')
                C.cyanH(text=strToSearch, end='')
                C.cyan(text=chap[pos+lun:pos+lun+60])

    if STR_FOUND:
        Ln.prompt('continue....')
    '''

