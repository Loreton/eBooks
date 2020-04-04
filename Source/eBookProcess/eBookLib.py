# xxx!/usr/bin/python3
# Progamma per processare un ebook
#
# updated by ...: Loreto Notarantonio
# Version ......: 04-04-2020 08.31.22
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


def get_files_from_path(baseDir, filetype):
    """
    Recursively returns files matching a filetype from
    a path (e.g. return a list of paths from a folder
    of epub files).
    """
    files = []
    for item in os.scandir(baseDir):
        if item.is_file():
            if item.path.endswith(filetype):
            # full_path = os.path.join(baseDir, item.name)
            # if spec.match_file(full_path):
                files.append(os.path.join(baseDir, item.name))
        else:
            files.extend(get_files_from_path(item.path, filetype))
    return files


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

def eBookLib(gVars, base_path, filetype):
    global gv
    gv = gVars
    Ln = gv.Ln
    C = gVars.Color
    lnLogger = gv.lnLogger
    strToSearch = gv.search

    files = get_files_from_path(base_path, filetype)

    fDEBUG = False
    for file in files:
        C.yellowH(text='working on file: {file}'.format(**locals()))
        lnLogger.info('working on file: {0}'.format(file))
        try:
            book = epub.read_epub(file)
        except Exception as why:
            C.error(text=str(why))
            Ln.prompt('continue....')
            continue

        this_book = {}

        _title = book.get_metadata('DC', 'title')
        _creator = book.get_metadata('DC', 'creator')
        _description = book.get_metadata('DC', 'description')
        _date = book.get_metadata('DC', 'date')
        _identifier = book.get_metadata('DC', 'identifier')
        _coverage = book.get_metadata('DC', 'coverage')

        _description =_description[0][0] if _description else ''
        _identifier =_identifier[0][0] if _identifier else 'null'
        _title = _title[0][0] if _title else Path(file).name
        _creator =_creator[0][0] if _creator else ""
        _date =_date[0][0].split('T', 1)[0] if _date else ""

        # _title = book.get_metadata('DC', 'title')[0][0]
        # _creator = book.get_metadata('DC', 'creator')[0][0]
        # _description = book.get_metadata('DC', 'description')
        # _date = book.get_metadata('DC', 'date')[0][0].split('T', 1)[0]
        # _identifier = book.get_metadata('DC', 'identifier')[0][0]
        # _identifier = book.IDENTIFIER_ID

        this_book['title'] = _title
        this_book['creator'] = _creator
        this_book['identifier'] = _identifier
        # this_book['description'] = _description
        this_book['coverage'] = _coverage
        this_book['date'] = _date

        # lnLogger.info('processing file: {this_book}'.format(**locals()))
        # lnLogger.info('processing book', book)
        lnLogger.console('processing book', this_book)
        # Ln.prompt('continue....')

        # german_corpus=[]
        # for doc in book.get_items():
        #     doc_content = str(doc.content)
        #     for w in nltk.word_tokenize(doc_content):
        #         german_corpus.append(w.lower())
        # Ln.prompt('continue....')
        # if fDEBUG:
        #     print('title        {_title}'.format(**locals()))
        #     print('creator      {_creator}'.format(**locals()))
        #     print('ID           {_identifier}'.format(**locals()))
        #     print('description  {_description}'.format(**locals()))
        #     print('date         {_date}'.format(**locals()))
        #     print()
        '''
        chapters = epub2text(file)
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

