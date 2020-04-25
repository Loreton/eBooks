# xxx!/usr/bin/python3
# Progamma per processare un ebook
#
# updated by ...: Loreto Notarantonio
# Version ......: 25-04-2020 14.00.09
#

import sys
import os
from pathlib import Path
# from dotmap import DotMap
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
        self._ePubs.setFields([ '_id',
                                "date",
                                "description",
                                'author',
                                'author_CN', # Cognome+None mi server per l'id
                                'chapters',
                                'filter', # comodo per fare la ricerca
                                'indexed', # True/False id words into dictionary collection
                                'title',
                                'tags',
                                ])

        self._ePubs.setIdFields(['author_CN', 'title'])
        # eBooks_coll=eBooks.collection

        self._Dictionary = MongoCollection(collection_name='Dictionary', **_args)
        self._Dictionary.setFields(['_id', 'filter', 'ebook'])
        # self._Dictionary.setIdFields(['word'])



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

    def author_reverse(self, data):
        # Inversione nome dell'autore
        ret_val = []
        words=data.split()
        words.reverse()
        for word in words:
            c_word=[ c for c in word if c.isalnum()]
            ret_val.append(''.join(c_word))

        return ' '.join(ret_val)



    ####################################################
    # -
    ####################################################
    def _readEbook(self, file, SKIP_UNKNOWN=True):
        ''' SKIP_UNKNOWN:
                ignora Libri che non hanno il  titolo dentro
        '''
        hBook = self._open_book(file)

        # book_data = DotMap(_dynamic=False)
        book_data = {}
        try:
            _title       = hBook.get_metadata('DC', 'title')
            _creator     = hBook.get_metadata('DC', 'creator')
            _description = hBook.get_metadata('DC', 'description')
            _date        = hBook.get_metadata('DC', 'date')
            # _identifier  = hBook.get_metadata('DC', 'identifier')
            # _coverage    = book['get_metadata']('DC', 'coverage')

            # book_data['identifier']  = _identifier[0][0]            if _identifier else 'null'
            book_data['description'] = _description[0][0]           if _description else ''
            book_data['title']       = _title[0][0]                 if _title else ''
            book_data['author']      = _creator[0][0]               if _creator else ""
            book_data['date']        = _date[0][0].split('T', 1)[0] if _date else ""
            book_data['indexed']     = False
            book_data['chapters']    = []
            book_data['tags']        = []

        except Exception as why:
            C.error(text=str(why), tab=12)
            target_file=file + '.err.zip'
            logger.error('renaming file: {file} to {target_file}'.format(**locals()))
            Path(file).rename(target_file)
            return {}


        if not book_data['title']:
            if SKIP_UNKNOWN:
                book_data={}
            else:
                book_data['title'] = Path(file).stem
        else:
            replace_string=['Italian Edition', '#', ':']
            for item in replace_string:
                book_data['title'] = book_data['title'].replace(item, '')
            book_data['title'] = book_data['title'].strip()


        if not book_data['author']: book_data['author'] = 'Unknown'
        book_data['author_CN'] = self.author_reverse(book_data['author'])

        logger.info('book data', book_data)

        return book_data




    ####################################################
    # -
    ####################################################
    def build_dictionary(self, book={}):
        if book:
            # book =self._ePubs.get_record(filter)
            # force flag
            if inp_args.all_records: book['indexed'] = False
            if not book['indexed']:
                C.yellowH(text='[1/1] - working on book: {} [{}]'.format(book['title'],book['author']), tab=4)
                self.add_to_dictionary(book)
                result = self._ePubs.updateField(rec=book, fld_name='indexed')

        else:
            result = self._ePubs._collection.find()
            nrec=result.count()
            for index, book in enumerate(result, start=1):
                # book = DotMap(book)
                # force flag
                if inp_args.all_records: book['indexed'] = False
                # C.yellowH(text='[{index:5}/{nrec:5}] - indexed: {book['indexed']} - book: {book['title']} [{book['author']}]'.format(**locals()), tab=4)
                if not book['indexed']:
                    self.add_to_dictionary(book)
                    _filter = {'_id': book['_id']}
                    result = self._ePubs.updateField(rec=book, fld_name='indexed')



    ####################################################
    # - indexing book content, title author and description
    ####################################################
    def add_to_dictionary(self, book):
        _data = []
        if 'tags'        in inp_args.fields and book['tags']:    _data.extend(book['tags'])
        if 'chapters'    in inp_args.fields and book['chapters']:    _data.extend(book['chapters'])
        if 'title'       in inp_args.fields and book['title']:       _data.append(book['title'])
        if 'author'      in inp_args.fields and book['author']:      _data.append(book['author'])
        if 'description' in inp_args.fields and book['description']: _data.append(book['description'])

        words = self.content2words(' '.join(_data))
        logger.info('inserting {0} words into dictionary'.format(len(words)))
        lun=len(words)
        for index, word in enumerate(words, start=1):
            if not index%500:
                C.white(text='word processed: {index:5}/{lun}'.format(**locals()), tab=8)

            # - preparazione record del dictionary
            rec={
                '_id':    word.lower(),
                'ebook':  [book['_id']],
                'filter': {'_id': word.lower()},
                # 'word': word.lower(), # non serve perché==_id
            }

            # rec=DotMap(
            #     _id = word.lower(),
            #     ebook = [book['_id']],
            #     filter = {'_id':word.lower()},
            #     # 'word': word.lower(), # non serve perché==_id
            # )


            # - updating record o create it if not exists
            result = self._Dictionary.updateField(rec, fld_name='ebook', create=True)

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
        '''
        https://rednafi.github.io/digressions/python/2020/04/13/python-pathlib.html#pathglob
            top_level_py_files = Path("src").glob("*.py")
            all_py_files = Path("src").rglob("*.py")
            print(list(top_level_py_files))
            print(list(all_py_files))
            la lettura di un iterator automaticamente lo azzera.
            quindi utilizzarlo direttamente oppure con list salvare i dati
        '''
        all_files = list(Path(dir_path).rglob(file_pattern))
        nFiles = len(all_files)

        # - try to insert each file
        for index, epub_file in enumerate(sorted(all_files), start=1):
            _dir = epub_file.parent
            if index > inp_args.max_books:
                continue
            book = self._readEbook(file=epub_file)
            if not book: continue # book not valid

            print()
            # C.yellowH(text='[{index:06}/{nFiles:06}] - {book['title']} - [{book['author']}]'.format(**locals()), tab=4)

            self._ePubs.set_id(book)
            curr_book = self._ePubs.exists(rec=book)
            if curr_book:
                C.yellowH(text='already catalogued - indexed: {0}'.format(curr_book['indexed']), tab=16)

            else:   # - insert book into eBooks_collection
                book['chapters'] = self._readContent(filename=epub_file)
                try:
                    _status, _filter = self._ePubs.insert_one(book, replace=False)
                except Exception as why:
                    C.error(text=str(why))
                    C.yellowH(text=epub_file, tab=8)
                    epub_file.rename(epub_file / '.err.zip')
                    continue

                # - forcing dictionary update
            if inp_args.dictionary and not book['indexed']:
                inp_args.fields = ['chapters', 'title', 'tags', 'author', 'description']
                inp_args.all_records = True
                self.build_dictionary(book)


            # move file if required
            if target_dir:
                target_file='{target_dir}/{0}.epub'.format(book['title'], **locals())
                C.yellowH(text='... moving to:', tab=16)
                C.yellowH(text='dir:   {target_dir}'.format(**locals()), tab=18)
                C.yellowH(text='fname: {}'.format(book['title']), tab=18)

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
            C.yellowH(text='Word {0:} found in {1:5} books'.format(regex, len(_list)), tab=4)


        # - AND tra le varie liste
        # pdb.set_trace()
        result = _lists[0][:] # copy the first list
        for l in _lists:
            result = list(set(result) & set(l))

        result = list( dict.fromkeys(result) ) # remove duplicates
        C.yellowH(text='After filter remaining {0} books'.format(len(result)), tab=4)
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
    def multiple_field_search(self, fields=[], words=[], book_id=None, ignore_case=True):
        if 'all' in fields:
            fields=self._ePubs.fields
        # words=['ciao', 'tempo']
        if book_id:
            books = [book_id]
        else:
            books = self.dictionary_search(words=words, ignore_case=ignore_case)

        for book_id in books:
            _filter = { "_id": book_id }
            rec = self._ePubs.get_record(_filter)

            for fld_name in fields:
                res = self._find_words_in_text(data=rec[fld_name], words=words, fPRINT=False)
                if res:
                    rec = DotMap(rec)
                    C.yellowH(text='''
                        result for field [{fld_name}]
                            - id: {rec._id}
                            - book: {rec.title} - [{rec.author}]\
                        '''.format(**locals()), tab=4)

                    for k, v in res.items():
                        for item in v:
                            print(' '*7, item)
                        print()
                    Ln.prompt()




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
        for item in book['get_items']():
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
    def change_ID(self):
        result = self._ePubs._collection.find()
        nrec=result.count()
        for index, book in enumerate(result, start=1):
            # book = DotMap(book)
            book['author_CN']= self.author_reverse(book['author'])
            new_id = self._ePubs.get_id(book)
            C.yellowH(text='''
                record [{index:5}/{nrec:5}]]
                    - book: {book['title']} - [{book['author']}]
                    - author_CN: {book['author_CN']}
                    - id_old: {book['_id']}
                    - id_new: {new_id}\
                '''.format(**locals()), tab=4)


        # db.account_data.find({"_id" : "1232014"}).forEach(function(doc) {
        #     var oldId = doc._id;
        #     var doc._id = doc._id + doc.country;
        #     db.collection.remove({ _id: oldId });
        #     db.collection.save(doc);
        # });


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




