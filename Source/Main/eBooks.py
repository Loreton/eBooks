# xxx!/usr/bin/python3
# Progamma per processare un ebook
#
# updated by ...: Loreto Notarantonio
# Version ......: 13-04-2020 16.57.02
#

import sys
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

from LnMongoCollection import MongoCollection
# from Source

class LnEBooks:
    DBs=DotMap(_dynamic=False) # Global var per gestire più DBases
        # ***********************************************
        # ***********************************************
    def __init__(self, db_name):
        # global logger
        # logger = myLogger
        # self._db_name = db_name
        # self._collection_name = collection_name
        # self._client  = self._dbConnect(db_name, server_name, server_port)
        # self._db      = self._client[db_name] # create DB In MongoDB, a database is not created until it gets content
        # self._collection = self._db[collection_name] # create collection. A collection is not created until it gets content!

        # - creazione DB oer contenere libri
        args={
            'db_name':          db_name,
            'collection_name':  'epub',
            'server_name':      '127.0.0.1',
            'server_port':      '27017',
            'myLogger':         logger,
        }

        self._ebooks = MongoCollection(**args)
        self._ebooks.setFields(['title',
                                'author',
                                "date",
                                "description",
                                "identifier",
                                'chapters',
                                ])

        self._ebooks.setIdFields(['author', 'title'])
        # eBooks_coll=eBooks.collection



        # - creazione DB oer contenere dizionario di parole
        args['collection_name'] = 'Dictionary'
        self._Dictionary = MongoCollection(**args)
        self._Dictionary.setFields(['word', 'ebook'])
        self._Dictionary.setIdFields(['word'])



    ####################################################
    # -
    ####################################################
    def _readEbook(self, file):
        this_book = DotMap(_dynamic=False)
        logger.info('working on file', file)
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

        # log without content field (to reduce logging data)
        logger.info('book data', this_book)

        chapters = self._epub2text(file)
        for chap in chapters:
            this_book.chapters.append(chap)



        # write_book(this_book)
        # import sys;sys.exit(1)
        return this_book



    ####################################################
    # -
    ####################################################
    def load_eBooks(self, dir_path, file_pattern):

        # - read list of files
        files = self._listFiles(dir_path, filetype=file_pattern)

        # - try to insert each file
        for index, file in enumerate(files, start=1):
            file_path=Path(file)
            if index > 10: sys.exit(1)
            C.yellowH(text='working on file {index:4}: {file_path}'.format(**locals()), end='')

            # - read the book
            book = self._readEbook(file=file_path._str)
            C.yellowH(text=' - {book.title}'.format(**locals()))

            # - insert book into DBase_collection
            result = self._ebooks.insert(book, replace=True)
            if result['record_0'][0] in ('replaced', 'inserted'):
                target_file='/mnt/k/tmp/{book.author}/{book.title}.epub'.format(**locals())
                # file_path.moveFile(target_file, replace=False)

                content = self.content2words(' '.join(book.chapters))
                for word in content:
                    # rec={
                    #     'word': word,
                    #     'ebook': book._id
                    # }
                    filter = {'_id': word}
                    field = {'ebook': book._id}
                    result = self._Dictionary.updateField(filter, field, create=True)

                sys.exit()




    ####################################################
    # -
    ####################################################
    def content2words(self, content):
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

        words = []
        for word in content:
            word_alfa = [ c for c in word if c.isalpha()]
            word2 = ''.join(word_alfa)
            if not word == word2:
                print(word, word2)
            words.append(word2)

        logger.info("total words (only alpfa)", len(words))
        return words



    ####################################################
    # - https://medium.com/@zazazakaria18/turn-your-ebook-to-text-with-python-in-seconds-2a1e42804913
    ####################################################
    def _epub2text(self, file_path):
        chapters = self._epub2thtml(file_path)
        text = self._thtml2ttext(chapters)
        return text

    def _epub2thtml(self, filename):
        """
        ritorna la lista dei capitoli in formato html
        """
        book = epub.read_epub(filename)
        chapters = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                chapters.append(item.get_content())
        return chapters

    def _thtml2ttext(self, chapters):
        Output = []
        for html in chapters:
            text =  self._chap2text(html)
            Output.append(text)
        return Output

    def _chap2text(self, chap):
        # there may be more elements you don't want, such as "style", etc.
        blacklist = ['[document]', 'noscript', 'header', 'html', 'meta', 'head','input', 'script',]
        output = ''
        soup = BeautifulSoup(chap, 'html.parser')
        text = soup.find_all(text=True)
        for t in text:
            if t.parent.name not in blacklist:
                output += '{} '.format(t)
        return output



    ####################################################
    # -
    ####################################################



    ####################################################
    # -
    ####################################################
    def _listFiles(self, baseDir, filetype):
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
                files.extend(self._listFiles(item.path, filetype))
        return files


####################################################
# -
####################################################
def openDB(db_name):
    # - initialize Mongo
    args={
        'db_name':          db_name,
        'collection_name':  'epub',
        'server_name':      '127.0.0.1',
        'server_port':      '27017',
        'myLogger':         logger,
    }

    eBooks = MongoCollection(**args)

    args['collection_name'] = 'Dictionary'
    Dictionary = MongoCollection(**args)



    eBooks.setFields(['title',
                            'author',
                            "date",
                            "description",
                            "identifier",
                            'chapters',
                            ])

    eBooks.setIdFields(['author', 'title'])
    # eBooks_coll=eBooks.collection
    Dictionary.setFields(['word', 'ebook'])
    Dictionary.setIdFields(['word'])



def main(gVars, dir, file_pattern='.epub'):
    global gv, logger, C
    gv     = gVars
    C      = gVars.Color
    logger = gVars.lnLogger

    Ln          = gv.Ln
    # openDB(db_name='eBooks')
    ebooks=LnEBooks(db_name='eBooks')
    ebooks.load_eBooks(dir, file_pattern)




