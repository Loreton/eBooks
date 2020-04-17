# xxx!/usr/bin/python3
# Progamma per processare un ebook
#
# updated by ...: Loreto Notarantonio
# Version ......: 17-04-2020 17.31.59
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
# import nltk
# nltk.download('punkt')

from LnMongoCollection import MongoCollection

class LnEBooks:
        # ***********************************************
        # ***********************************************
    def __init__(self, gVars, db_name):
        global gv, logger, C, Ln, inp_args
        gv     = gVars
        C      = gVars.Color
        logger = gVars.lnLogger
        Ln     = gVars.Ln
        inp_args   = gVars.args

        # - creazione DB oer contenere libri
        _args={
            'db_name':          db_name,
            'server_name':      '127.0.0.1',
            'server_port':      '27017',
            'myLogger':         logger,
        }

        self._ePubs = MongoCollection(collection_name='ePubs', **_args)
        self._ePubs.setFields(['title',
                                'author',
                                "date",
                                "description",
                                "identifier",
                                'chapters',
                                'indexed', # True/False id words into dictionary collection
                                ])

        self._ePubs.setIdFields(['author', 'title'])
        # eBooks_coll=eBooks.collection

        self._Dictionary = MongoCollection(collection_name='Dictionary', **_args)
        self._Dictionary.setFields(['word', 'ebook'])
        self._Dictionary.setIdFields(['word'])

        # solo per merge
        # self._wk_Dictionary = MongoCollection(collection_name='wk_Dictionary', **_args)
        # self._wk_Dictionary.setFields(['word', 'ebook'])
        # self._wk_Dictionary.setIdFields(['word'])


    ####################################################
    # -
    ####################################################
    def _open_book(self, file):
        book = None
        logger.info('opening ebook', file)
        try:
            book = epub.read_epub(file)
        except Exception as why:
            C.yellowH(text="Error reading file: {file}".format(**locals()), tab=8)
            C.error(text=str(why), tab=12)
            target_file=file + '.err.zip'
            logger.error('renaming file: {file} to {target_file}'.format(**locals()))
            Path(file).rename(target_file)

        return book

    ####################################################
    # -
    ####################################################
    def _readMetadata(self, book):
        book_data = DotMap(_dynamic=False)
        _title       = book.get_metadata('DC', 'title')
        _creator     = book.get_metadata('DC', 'creator')
        _description = book.get_metadata('DC', 'description')
        _date        = book.get_metadata('DC', 'date')
        _identifier  = book.get_metadata('DC', 'identifier')
        # _coverage    = book.get_metadata('DC', 'coverage')


        book_data.description = _description[0][0]           if _description else ''
        book_data.identifier  = _identifier[0][0]            if _identifier else 'null'
        book_data.title       = _title[0][0]                 if _title else ''
        book_data.author      = _creator[0][0]               if _creator else ""
        book_data.date        = _date[0][0].split('T', 1)[0] if _date else ""
        book_data.indexed     = False
        book_data.chapters    = []
        book_data.title = book_data.title.replace('(Italian Edition)', '').replace('#', '').strip()
        # log without content field (to reduce logging data)
        logger.info('book data', book_data)

        return book_data


    ####################################################
    # -
    ####################################################
    def _readContent(self, hBook=None, filename=None):
        if not hBook:
            hBook = self._open_book(filename)

        # - capitoli in formato html
        html_chapters = []
        for item in hBook.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                html_chapters.append(item.get_content())

        # - convert html[] to text[]
        text_chapters = self._thtml2ttext(html_chapters)

        return text_chapters






    ####################################################
    # -
    ####################################################
    def _readEbook(self, file):
        hBook = self._open_book(file)

        try:
            _data = self._readMetadata(hBook)
        except Exception as why:
            C.error(text=str(why), tab=12)
            target_file=file + '.err.zip'
            logger.error('renaming file: {file} to {target_file}'.format(**locals()))
            Path(file).rename(target_file)
            return {}

        if not _data.title:
            _data.title = Path(file).stem
        _data.chapters = self._readContent(hBook)

        return _data



    ####################################################
    # -
    ####################################################
    def rebuild_dictionary(self, chapters):
        pass



    ####################################################
    # -
    ####################################################
    def optimize_dictionary(self):
        records = self._Dictionary.collection.find()
        nRec=records.count()
        # import pdb;pdb.set_trace()
        for index, _rec in enumerate(records, start=1):
            # print('{0:6} {1}- {2}'.format(index, nRec, _rec['word']))
            if not index%500:
                C.white(text='word processed: {index:5}/{nRec}'.format(**locals()), tab=18)

            rec={
                'word': _rec['word'].lower(),
                'ebook': _rec['ebook']
            }
            filter = {'_id': self._wk_Dictionary.get_id(rec)}
            if self._wk_Dictionary._collection.count_documents(filter, limit = 1):
                result = self._wk_Dictionary.updateField(filter=filter, fld={'ebook': rec['ebook']})
            else:
                result = self._wk_Dictionary.insert_one(rec)



    ####################################################
    # -
    ####################################################
    def index_to_dictionary(self, book, book_id):
        # query = {'_id': {"$regex": 'isbn', "$options" : 'i'}
        words = self.content2words(' '.join(book.chapters))
        logger.info('inserting {0} words into dictionary'.format(len(words)))
        lun=len(words)
        for index, word in enumerate(words):
            if not index%500:
                C.white(text='word processed: {index:5}/{lun}'.format(**locals()), tab=18)

            rec={
                'word': word.lower(),
                'ebook': [book_id]
            }
            filter = {'_id': self._Dictionary.get_id(rec)}
            if self._Dictionary._collection.count_documents(filter, limit = 1):
                result = self._Dictionary.updateField(filter=filter, fld={'ebook': rec['ebook']})
            else:
                result = self._Dictionary.insert_one(rec)

        print()

    ####################################################
    # -
    ####################################################
    def load_eBooks(self, dir_path, file_pattern, target_dir=None):

        # - read list of files
        files = self._listFiles(dir_path, filetype=file_pattern)
        nFiles = len(files)

        # - try to insert each file
        # import pdb;pdb.set_trace()
        for index, file in enumerate(files, start=1):
            epub_file=Path(file)
            _dir = epub_file.parent
            if inp_args.max_books>0 and index > inp_args.max_books:
                continue
            print()
            C.yellowH(text='''working on file {index:3}/{nFiles:03}:
                dir:   {epub_file.parent}'''.format(**locals()))

            # - read the book
            book = self._readEbook(file=epub_file.toStr())
            if not book: continue
            C.yellowH(text='fname: {book.title}'.format(**locals()), tab=16)

            # - insert book into eBooks_collection
            try:
                _status, _filter = self._ePubs.insert_one(book, replace=False)
                (book_id_fld, book_id_val), = _filter.items()
                # import pdb;pdb.set_trace()
            except Exception as why:
                C.error(text=str(why))
                C.yellowH(text=epub_file, tab=8)
                epub_file.rename(str(epub_file) + '.err.zip')
                continue

            # - if document exists get indexed_flag from existing document
            if _status == 'exists':
                _rec=self._ePubs.get_record(_filter) # get current record
                book.indexed = _rec['indexed']

            if target_dir:
                target_file='{target_dir}/{book.title}.epub'.format(**locals())
                C.yellowH(text='... moving to:', tab=16)
                C.yellowH(text='dir:   {target_dir}'.format(**locals()), tab=18)
                C.yellowH(text='fname: {book.title}'.format(**locals()), tab=18)

                if not epub_file.moveTo(target_file, replace=False):
                    epub_file.rename(str(epub_file) + '.not_moved')


            if inp_args.dictionary and not book.indexed:
                C.yellowH(text='... updating dictionary', tab=16)
                self.index_to_dictionary(book, book_id_val)
                result = self._ePubs.updateField(filter=_filter, fld={'indexed': True})


            # elif result[0] in ('exists'):
            #     epub_file.rename(str(epub_file) + '.exists')




    ####################################################
    # -
    ####################################################
    def search(self, regex, field_name='word', ignore_case=True):
        ebook_list = []
        if field_name in self._Dictionary.fields:
            result = self._Dictionary.search(field_name=field_name, regex=regex, ignore_case=ignore_case)
            for x in result:
                ebook_list.extend(x['ebook'])
            ebook_list = list( dict.fromkeys(ebook_list) ) # remove duplicates

        elif field_name in self._ePubs.fields:
            result = self._ePubs.search(field_name=field_name, regex=regex, ignore_case=ignore_case)
            for x in result:
                # ebook_list.append(x['_id'])
                print(x['author'], ' - ', x['title'] )
            return []

        else:
            print('Field: {field_name} NOT found'.format(**locals()))
            return []

        logger.console("lista", ebook_list)
        return ebook_list


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
        logger.info("   after removing duplicated", len(content))

        words = []
        for word in content:
            word_alfa = [ c for c in word if c.isalpha()]
            word2 = ''.join(word_alfa)
            if not word == word2:
                # print(word, word2)
                pass
                # logger.debug3('alpha word', [word, word2])
            words.append(word2)

        # logger.info("   Words", words)
        logger.info("   after only_alpha filter", len(words))
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






def main(gVars, dir, file_pattern='.epub', move_file=False):
    global gv, logger, C
    gv     = gVars
    C      = gVars.Color
    logger = gVars.lnLogger
    args = gVars.args

    Ln          = gv.Ln
    # ebooks=LnEBooks(db_name='eBooks')
    # ebooks.load_eBooks(dir, file_pattern, move_file)




