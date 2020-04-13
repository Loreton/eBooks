# xxx!/usr/bin/python3
# Progamma per processare un ebook
#
# updated by ...: Loreto Notarantonio
# Version ......: 12-04-2020 07.48.15
#

import os
from pathlib import Path
from dotmap import DotMap
import string

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

def epub2text(file_path):
    chapters = epub2thtml(file_path)
    text = thtml2ttext(chapters)
    return text

def search_string(substring, data):
    import re
    # All occurrences of substring in string
    res = [i.start() for i in re.finditer(substring, data)]
    return res


def write_book(my_book):
    book = epub.EpubBook()
    book.set_identifier(my_book['identifier'])
    book.set_title(my_book['title'])
    book.set_language('it')
    book.add_author(my_book['author'])
    book.add_metadata('DC', 'description', 'This is description for my book')
    book.add_metadata(None, 'meta', '', {'name': 'key', 'content': 'value'})

    # intro chapter
    c1 = epub.EpubHtml(title='Introduction', file_name='intro.xhtml', lang='it')
    c1.set_content(u'<html><body><h1>Introduction</h1><p>Introduction paragraph.</p></˓→body></html>')
    # about chapter
    c2 = epub.EpubHtml(title='About this book', file_name='about.xhtml')
    c2.set_content('<h1>About this book</h1><p>This is a book.</p>')

    book.add_item(c1)
    book.add_item(c2)

    chaps = my_book['content']
    for index, chap in enumerate(chaps, start=1):
        chapter = epub.EpubHtml(title='chapter {index}'.format(**locals()), file_name='chapter_{index}.xhtml'.format(**locals()))
        chapter.set_content('<h1>Capitolo {index}</h1><p>{chap}</p>'.format(**locals()))
        book.add_item(chapter)




    style = 'body { font-family: Times, Times New Roman, serif; }'
    nav_css = epub.EpubItem(uid="style_nav",
    file_name="style/nav.css",
    media_type="text/css",
    content=style)
    book.add_item(nav_css)


    book.toc = (epub.Link('intro.xhtml', 'Introduction', 'intro'),
                (epub.Section('Languages'),
                (c1, c2) )
                )

    book.spine = ['nav', c1, c2]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub('test.epub', book)



def cleanContent(content):
    chars_to_replace = string.printable.replace(string.ascii_letters, '')
    chars_to_replace += '’'
    words_to_discard=[
                    'dalla', 'dalle', 'dallo', 'dall',
                    'della', 'dello', 'dell',
                    'nella', 'nello', 'nelle', 'nell',
                    'alla',  'alle', 'allo', 'all',
                    'cosa',
                    'loro',
                    ]

    # - rimpiazza i primi con i secondi
    table = ''.maketrans('òàùèìé', 'oaueie')
    content = content.translate(table)
    table = ' '.maketrans(chars_to_replace, ' '*(len(chars_to_replace)))
    content = content.translate(table)

    content = [w for w in content.split() if len(w)>3 and not w.lower() in words_to_discard]
    logger.info("total words", len(content))
    # - remove duplicate
    content = list( dict.fromkeys(content) )
    logger.info("total words (duplicated removed)", len(content))

    result = []
    for word in content:
        word_alfa = [ c for c in word if c.isalpha()]
        word2 = ''.join(word_alfa)
        if not word == word2:
            print(word, word2)
        result.append(word2)

    logger.info("total words (only alpfa)", len(result))
    return result


def eBookLib(gVars, file):
    global gv
    gv          = gVars
    Ln          = gv.Ln
    C           = gVars.Color
    lnLogger    = gv.lnLogger
    # strToSearch = gv.search

    this_book = DotMap(_dynamic=False)
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
    # _coverage    = book.get_metadata('DC', 'coverage')

    this_book.description = _description[0][0]           if _description else ''
    this_book.identifier  = _identifier[0][0]            if _identifier else 'null'
    this_book.title       = _title[0][0]                 if _title else Path(file).stem
    this_book.author      = _creator[0][0]               if _creator else ""
    this_book.date        = _date[0][0].split('T', 1)[0] if _date else ""
    this_book.chapters    = []
    # this_book['coverage']    = _coverage

    # log without content
    lnLogger.info('book data', this_book)



    chapters = epub2text(file)
    for chap in chapters:
        this_book.chapters.append(chap)

    # write_book(this_book)
    # import sys;sys.exit(1)
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

