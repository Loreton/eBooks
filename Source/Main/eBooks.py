# xxx!/usr/bin/python3
# Progamma per processare un ebook
#
# updated by ...: Loreto Notarantonio
# Version ......: 21-04-2020 17.10.28
#

import sys
import os
from pathlib import Path
from dotmap import DotMap
import string
import pdb
import re
import textwrap


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

        # - contiene la lista dei libri indicizzati
        self._Indexed = MongoCollection(collection_name='Indexed', **_args)
        self._Indexed.setFields(['author', 'title'])
        self._Indexed.setIdFields(['author', 'title'])

        # solo per merge
        # self._wk_Dictionary = MongoCollection(collection_name='wk_Dictionary', **_args)
        # self._wk_Dictionary.setFields(['word', 'ebook'])
        # self._wk_Dictionary.setIdFields(['word'])



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
    def _open_book(self, file):
        hBook = None
        logger.info('opening ebook', file)
        try:
            hBook = epub.read_epub(file)
        except Exception as why:
            C.yellowH(text="Error reading file: {file}".format(**locals()), tab=8)
            C.error(text=str(why), tab=12)
            target_file=file + '.err.zip'
            logger.error('renaming file: {file} to {target_file}'.format(**locals()))
            Path(file).rename(target_file)

        return hBook





    ####################################################
    # -
    ####################################################
    def _readEbook(self, file, IGNORE_UNKNOWN=True):
        ''' IGNORE_UNKNOWN:
                ignora Libri che non hanno il  titolo dentro
        '''
        hBook = self._open_book(file)

        book_data = DotMap(_dynamic=False)
        try:
            _title       = hBook.get_metadata('DC', 'title')
            _creator     = hBook.get_metadata('DC', 'creator')
            _description = hBook.get_metadata('DC', 'description')
            _date        = hBook.get_metadata('DC', 'date')
            _identifier  = hBook.get_metadata('DC', 'identifier')
            # _coverage    = book.get_metadata('DC', 'coverage')

            book_data.description = _description[0][0]           if _description else ''
            book_data.identifier  = _identifier[0][0]            if _identifier else 'null'
            book_data.title       = _title[0][0]                 if _title else ''
            book_data.author      = _creator[0][0]               if _creator else ""
            book_data.date        = _date[0][0].split('T', 1)[0] if _date else ""
            book_data.indexed     = False
            book_data.chapters    = []

        except Exception as why:
            C.error(text=str(why), tab=12)
            target_file=file + '.err.zip'
            logger.error('renaming file: {file} to {target_file}'.format(**locals()))
            Path(file).rename(target_file)
            return {}


        if not book_data.title:
            if IGNORE_UNKNOWN:
                book_data={}
            else:
                book_data.title = Path(file).stem
                if not book_data.author:
                    book_data.author = 'Unknown'
        else:
            book_data.title = book_data.title.replace('(Italian Edition)', '').replace('#', '').strip()
            ''' per fare il reverse del nome dell'autore, ma non conviene
            _a=book_data.author.split()
            _a.reverse
            book_data.author = '_'.join(_a)
            '''

        logger.info('book data', book_data)

        return book_data




    ####################################################
    # -
    ####################################################
    def build_dictionary(self, book={}):
        if book:
            book = DotMap(book)
            C.yellowH(text='[1/1] - working on book: {book.title} [{book.author}]'.format(**locals()), tab=4)
            self.add_to_dictionary(book)
            _filter = {'_id': book['_id']}
            result = self._ePubs.updateField(filter=_filter, fld={'indexed': True})

        else:
            result = self._ePubs._collection.find()
            nrec=result.count()
            for index, book in enumerate(result, start=1):
                book = DotMap(book)
                C.yellowH(text='[{index:5}/{nrec:5}] - working on book: {book.title} [{book.author}]'.format(**locals()), tab=4)
                self.add_to_dictionary(book)
                _filter = {'_id': book['_id']}
                result = self._ePubs.updateField(filter=_filter, fld={'indexed': True})



    ####################################################
    # - indexing book content, title author and description
    ####################################################
    def add_to_dictionary(self, book):
        book_id = book._id
        _data = []
        if inp_args.chapters    and book.chapters:        _data.extend(book.chapters)
        if inp_args.title       and book.title:           _data.append(book.title)
        if inp_args.author      and book.author:          _data.append(book.author)
        if inp_args.description and book.description:     _data.append(book.description)

        words = self.content2words(' '.join(_data))
        logger.info('inserting {0} words into dictionary'.format(len(words)))
        lun=len(words)
        for index, word in enumerate(words, start=1):
            if not index%500:
                C.white(text='word processed: {index:5}/{lun}'.format(**locals()), tab=8)

            rec={
                'word': word.lower(),
                'ebook': [book_id]
            }
            filter = {'_id': self._Dictionary.get_id(rec)}
            if self._Dictionary._collection.count_documents(filter, limit = 1):
                result = self._Dictionary.updateField(filter=filter, fld={'ebook': rec['ebook']})
            else:
                result = self._Dictionary.insert_one(rec)

        C.white(text='word processed: {index:5}/{lun:5}'.format(**locals()), tab=8)
        print()

    ####################################################
    # -
    ####################################################
    def update_field_many(self):
        result = self._ePubs.updateField_many(
                {'indexed': False},
                {'$set': {'indexed': False}}
            )
        print(result.matched_count)
        print(result.modified_count)
        sys.exit()

    ####################################################
    # -
    ####################################################
    def load_eBooks(self, dir_path, file_pattern, target_dir=None):
        # - read list of files
        files = self._listFiles(dir_path, filetype=file_pattern)
        nFiles = len(files)

        # - try to insert each file
        for index, file in enumerate(sorted(files), start=1):
            epub_file=Path(file)
            _dir = epub_file.parent
            if index > inp_args.max_books:
                continue
            book = self._readEbook(file=epub_file.toStr())
            if not book: continue # book not valid

            print()
            C.yellowH(text='[{index:6}/{nFiles:6}] - {book.title} - [{book.author}]'.format(**locals()), tab=4)

            _book = self._ePubs.exists(rec=book)
            if _book.exists:
                C.yellowH(text='already catalogued - indexed: {0}'.format(_book.data['indexed']), tab=16)

            else:   # - insert book into eBooks_collection
                book.chapters = self._readContent(filename=epub_file.toStr())
                try:
                    _status, _filter = self._ePubs.insert_one(book, replace=False)
                except Exception as why:
                    C.error(text=str(why))
                    C.yellowH(text=epub_file, tab=8)
                    epub_file.rename(str(epub_file) + '.err.zip')
                    continue

            if inp_args.dictionary and not book.indexed:
                # - forcing dictionary update
                inp_args.chapters = True
                inp_args.title = True
                inp_args.author = True
                inp_args.description = True
                self.build_dictionary(book)


            # move file if required
            if target_dir:
                target_file='{target_dir}/{book.title}.epub'.format(**locals())
                C.yellowH(text='... moving to:', tab=16)
                C.yellowH(text='dir:   {target_dir}'.format(**locals()), tab=18)
                C.yellowH(text='fname: {book.title}'.format(**locals()), tab=18)

                if not epub_file.moveTo(target_file, replace=False):
                    epub_file.rename(str(epub_file) + '.not_moved')






        # All occurrences of substring in string
    def search_string(self, substring, data):
        import re
        res = [i.start() for i in re.finditer(substring, data)]
        return res

    ####################################################
    # -
    # metodi per mandare in AND più liste
    #   result = list(set(a) & set(b) & set(c))
    #   result = list(set(a).intersection(b))
    # return: list of book_id
    ####################################################
    def dictionary_search(self, words, ignore_case=True):
        _lists = []

        # - una search per ogni word
        for regex in words:
            result = self._Dictionary.search(field_name='word', regex=regex, ignore_case=ignore_case)
            _list = []
            for x in result:
                _list.extend(x['ebook'])

            # - append and remove duplicates
            _lists.append(list( dict.fromkeys(_list) ))
            C.yellowH(text='Word {0:<20} FOUND {1:5} books'.format(regex, len(_list)), tab=4)


        # - AND tra le varie liste
        # pdb.set_trace()
        result = _lists[0][:] # copy the first list
        for l in _lists:
            result = list(set(result) & set(l))

        result = list( dict.fromkeys(result) ) # remove duplicates
        C.yellowH(text='After AND FOUND {0} books'.format(len(result)), tab=4)
        print()

        return result


    ####################################################
    # - return dict{
    #               1: [res1, res2]
    #               2: [res1, res2, res3]
    #               ...
    #              }
    ####################################################
    def _find_words_in_text(self, data=[], words=[], fPRINT=True):
        if isinstance(data, (str)):
            data=[data]

        _before=100
        _after=150
        STR_FOUND=False
        result_data={}
        index=0
        for item in data:
            for word in words:
                colored_word = C.magentaH(text=word, get=True)
                occurrencies = [i.start() for i in re.finditer(word, item)]
                if occurrencies:
                    STR_FOUND=True
                    index += 1
                    for pos in occurrencies:
                        lun=len(word)
                        _from=0 if pos-_before<0 else pos-_before
                        _to=pos+lun+_after
                        text=item[_from:_to]
                        text = ' '.join(text.split()) # remove multiple blanks
                        new_text=text.replace(word, colored_word)
                        tb=textwrap.wrap(new_text, 80, break_long_words=True)
                        result_data[index] = tb
                        if fPRINT:
                            for l in tb:
                                print('    ', l)
                            print()
        return result_data


    ####################################################
    # -
    ####################################################
    def multiple_field_search(self, fields=[], words=[], ignore_case=True):
        if 'all' in fields:
            fields=self._ePubs.fields
        # words=['ciao', 'tempo']
        books = self.dictionary_search(words=words, ignore_case=ignore_case)
        for book_id in books:
            _filter = { "_id": book_id }
            rec = self._ePubs.get_record(_filter)

            for fld_name in fields:
                res = self._find_words_in_text(data=rec[fld_name], words=words, fPRINT=False)
                if res:
                    C.yellowH(text='result for field [{0}] - book: {1} - [{2}]'.format(fld_name, rec['title'], rec['author']), tab=4)
                    for k, v in res.items():
                        for item in v:
                            print('     ', item)
                        print()
                    Ln.prompt()


    ####################################################
    # -
    # metodi per mandare in AND più liste
    #   result = list(set(a) & set(b) & set(c))
    #   result = list(set(a).intersection(b))
    ####################################################
    def display_searched_result(self, result, words, book_id=None):
        import textwrap
        if not book_id: logger.console("lista", result)
        nRec = len(result)

        _before=100
        _after=150
        _filter = None
        for index, _id in enumerate(result):
            if book_id and _id in [book_id]:
                _filter = { "_id": _id }
                rec = DotMap(self._ePubs.get_record(_filter), _dynamic=False)
                C.magentaH(text='[{index:6}/{nRec:6}] - {rec.title} - [{rec.author}]'.format(**locals()))
                STR_FOUND=False
                for chap in rec['chapters']:
                    for word in words:
                        colored_word = C.yellowH(text=word, get=True)
                        occurrencies = self.search_string(word, chap)
                        if occurrencies:
                            STR_FOUND=True
                            for pos in occurrencies:
                                lun=len(word)
                                _from=0 if pos-_before<0 else pos-_before
                                _to=pos+lun+_after
                                text=chap[_from:_to]
                                text = ' '.join(text.split()) # remove multiple blanks
                                new_text=text.replace(word, colored_word)
                                tb=textwrap.wrap(new_text, 80, break_long_words=True)
                                for l in tb:
                                    print('    ', l)
                                print()

                if STR_FOUND and not book_id:
                    Ln.prompt()

        if not _filter:
            logger.console('NO records found for words', words)

    ####################################################
    # -
    ####################################################
    def ePubs_search(self, words, field_name='word',ignore_case=True):
        ebook_list = []
        for regex in words:
            result = self._ePubs.search(field_name=field_name, regex=regex, ignore_case=ignore_case)
            for x in result:
                print(x['author'], ' - ', x['title'] )
            return []

        logger.console("lista", ebook_list)
        return ebook_list






    ####################################################
    # -
    ####################################################
    def eBook_search(self, book_id, words ,ignore_case=True):
        result = self.dictionary_search(words=words, ignore_case=ignore_case)
        self.display_searched_result( result, words=words, book_id=book_id)



    ####################################################
    # -
    ####################################################
    def main_search(self, field_name, words=[], ignore_case=True):
        ebook_list = []
        if field_name in self._Dictionary.fields:
            result = self.dictionary_search(words=words, ignore_case=ignore_case)
            self.display_searched_result( result, words)

        elif field_name in self._ePubs.fields:
            result = self.ePubs_search(field_name=field_name, words=words, ignore_case=ignore_case)

        elif field_name in ['id', '_id']:
            import json
            _my_list=[]
            remove_fields=['chapters', 'description','identifier',]
            for regex in words:
                result = self._ePubs.search(field_name='_id', regex=regex, ignore_case=ignore_case)
                for x in result:
                    _my_list.append(x['author'] + ' - ' + x['title'])
                    for fld in remove_fields: x.pop(fld, None)
                    C.yellowH(text=json.dumps(x, indent=4, sort_keys=True), tab=4)

                for index, item in enumerate(sorted(_my_list)):
                    print('{index} - {item}'.format(**locals()))

        else:
            logger.console('Field: {field_name} NOT found'.format(**locals()))
            return []

        return 0


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




