# xxx!/usr/bin/python3
# Progamma per processare un ebook
#
# updated by ...: Loreto Notarantonio
# Version ......: 29-04-2020 09.04.42
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
    def __init__(self, gVars, db_name, execute=False):
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
        self._execute = execute
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
            logger.error('renaming file', file, 'to:', target_file, console=True)
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
        book_data = {}
        hBook = self._open_book(str(file))
        if not hBook:
            return book_data

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
            logger.error('renaming file: {file} to {target_file}'.format(**locals()), console=True)
            Path(file).rename(target_file)
            return {}


        if not book_data['title']:
            if SKIP_UNKNOWN:
                C.warning(text="{file} does't contain valid  metadata".format(**locals()), tab=4)
                file.rename(file.parent / '{file.stem}{file.suffix}.no_metadata'.format(**locals()) )
                return {}
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
    # - input:
    ####################################################
    def build_dictionary(self, book={}, force_indexing=False):
        if book:
            self.book_indexing(book, force_indexing)

        else:
            result = self._ePubs._collection.find()
            nrec=result.count()
            for counter, book in enumerate(result, start=1):
                C.yellowH(text='''
                    [{counter:5}/{nrec:5}] - {id}
                        book:      {title} - [{author}]
                        indexed:   {indexed}\
                    '''.format( title=book['title'],
                                author=book['author'],
                                id=book['_id'],
                                indexed=book['indexed'],
                                **locals()), tab=4)
                self.book_indexing(book, force_indexing)



    ####################################################
    # - indexing book content, title author and description
    ####################################################
    def book_indexing(self, book, force_indexing):
        if force_indexing: book['indexed'] = False # force flag

        if not book['indexed']:
            C.yellowH(text='indexing...', tab=8)

            _data = []
            if 'tags'        in inp_args.fields and book['tags']:        _data.extend(book['tags'])
            if 'chapters'    in inp_args.fields and book['chapters']:    _data.extend(book['chapters'])
            if 'title'       in inp_args.fields and book['title']:       _data.append(book['title'])
            if 'author'      in inp_args.fields and book['author']:      _data.append(book['author'])
            if 'description' in inp_args.fields and book['description']: _data.append(book['description'])

            words = self.content2words(' '.join(_data))
            logger.info('inserting {0} words into dictionary'.format(len(words)))
            lun=len(words)
            index=0
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


                # - updating record o create it if not exists
                if self._execute:
                    result = self._Dictionary.updateField(rec, fld_name='ebook', create=True)
                else:
                    logger.console('[DRY-RUN] - record updated.', rec)

            book['indexed'] = True
            if self._execute: self._ePubs.updateField(rec=book, fld_name='indexed')

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
        if not all_files:
            logger.critical('no files found on {dir_path}/{file_pattern}'.format(**locals()))

        nFiles = len(all_files)
        loaded_books=0  # counter
        indexed_books=0 # counter
        # - insert each file
        for index, epub_file in enumerate(sorted(all_files), start=1):
            _dir = epub_file.parent
            book = self._readEbook(file=epub_file)
            if not book: continue # book not valid
            if inp_args.indexing and indexed_books >= inp_args.max_books:
                return
            elif loaded_books >= inp_args.max_books:
                return


            print()
            self._ePubs.set_id(book)

            # C.yellowH(text='[{index:06}/{nFiles:06}] - {0} - [{1}]'.format(book['title'], book['author'], **locals()), tab=4)
            curr_book = self._ePubs.exists(rec=book)

            if curr_book:
                _msg='already catalogued'
                book = curr_book

            else:   # - insert book into eBooks_collection
                book['chapters'] = self._readContent(filename=epub_file)
                try:
                    if self._execute:
                        self._ePubs.insert_one(book, replace=False)
                        _msg='inserted as new book'
                    else:
                        _msg='[DRY-RUN] - inserted as new book'

                    loaded_books += 1
                except Exception as why:
                    C.error(text=str(why))
                    C.yellowH(text=epub_file, tab=8)
                    epub_file.rename(epub_file / '.err.zip')
                    continue

            dmBook = DotMap(book, _dynamic=False)
            C.yellowH(text='''
                [{index:05}/{nFiles:05}]
                    _id:       {dmBook._id}
                    book:      {dmBook.title} - [{dmBook.author}]
                    {_msg}
                    indexed:   {dmBook.indexed}\
                '''.format(**locals()), tab=4)


                # - forcing dictionary update
            if inp_args.indexing and not dmBook.indexed:
                inp_args.fields = ['chapters', 'title', 'tags', 'author', 'description']
                if self._execute: self.build_dictionary(book)
                indexed_books += 1


            # move file if required
            if target_dir:
                target_file='{target_dir}/{dmBook.title}.epub'.format(**locals())
                target_file='{target_dir}/{dmBook.title}.epub'.format(**locals())
                C.yellowH(text='... moving to:', tab=16)
                C.yellowH(text='dir:   {target_dir}'.format(**locals()), tab=18)
                C.yellowH(text='fname: {dmBook.title}'.format(**locals()), tab=18)

                if self._execute:
                    moved, reason = epub_file.moveTo(target_file, replace=False)
                    if not moved:
                        # - rename source
                        epub_file.rename(epub_file.parent / '{dmBook.title}{epub_file.suffix}_{reason}'.format(**locals()) )






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
        ret_list = []

        # - una search per ogni word
        for word in words:
            # - search in all fields of all books
            result = self._Dictionary.search(field_name='_id', regex=word, ignore_case=ignore_case)
            _list = []
            for x in result:
                _list.extend(x['ebook'])

            # - ANDing tra le varie liste
            C.yellowH(text='Word {0:} found in {1:5} books'.format(word, len(_list)), tab=4)
            if ret_list:
                ret_list = list(set(ret_list) & set(_list))
            else:
                ret_list = _list[:]

        # result = list( dict.fromkeys(result) ) # remove duplicates
        C.cyanH(text='''After AND remaining {0} potential books containing all your words in some field.
        It's not sure they are contained into your requested fields.'''.format(len(ret_list)), tab=4)
        print()

        return ret_list


    ####################################################
    # - return dict{
    #               1: [res1, res2]
    #               2: [res1, res2, res3]
    #               ...
    #              }
    # - return dict{
    #               word1 {
    #                       counter: x
    #                       index: []
    #                      }
    #               word2 {
    #                       counter: x
    #                       index: []
    #                      }
    #               wordn...
    ####################################################
    def _find_words_in_text(self, data=[], words=[], fPRINT=True):
        if isinstance(data, (str)):
            data=[data]

        _before=100
        _after=150
        result2 = {}

        # - preparazione word colorate
        colored_word = {}
        colors = [C.magentaH, C.yellowH, C.cyanH, C.redH, C.greenH, C.blueH, C.whiteH]
        for index, word in enumerate(words):
            result2[word] = {}
            result2[word]['counter'] = 0
            result2[word]['data'] = {}
            colored_word[word] =colors[index](text=word, get=True)

        index=0
        for item in data: # sono capitoli, descrizione, titoli o altro
            for word in words:
                occurrencies = [i.start() for i in re.finditer(word, item)]
                word_len=len(word)
                for pos in occurrencies:
                    # incr counter for specific word
                    result2[word]['counter'] += 1
                    index = result2[word]['counter']

                    # prepare list
                    result2[word]['data'][index] = []

                    # - search word and replace with colored_word
                    _from=0 if pos-_before<0 else pos-_before
                    _to=pos+word_len+_after
                    text=item[_from:_to]
                    text = ' '.join(text.split()) # remove multiple blanks
                    new_text=text.replace(word, colored_word[word])

                    # - wrap text to easy displaying
                    tb=textwrap.wrap(new_text, 80, break_long_words=True)

                    # - save it into result list
                    result2[word]['data'][index].extend(tb)

                    if fPRINT:
                        for l in tb:
                            print('    ', l)
                        print()

        return result2





    ####################################################
    # - Input:
    # -    fields:  campo/i dove effettuare la ricerca
    # -    words:   stringa/stringhe da ricercare (in AND)
    # -    book_id: se presente si cerca solo al suo interno
    ####################################################
    def multiple_field_search(self, fields=[], words=[], book_id=None, ignore_case=True):
        if 'all' in fields:
            fields=self._ePubs.fields
        # words=['gatto', 'tempo', 'iggulden', 'porte', 'roma']
        if book_id:
            books = [book_id]
        else:
            # - torna la lista dei libri che contengono le words (in AND)
            books = sorted(self.dictionary_search(words=words, ignore_case=ignore_case))


        # ###  D I S P L A Y    data
        prev_book_id = 0

        while True:
            # for index, book in enumerate(sorted(books), start=1):
            for index, book in enumerate(books, start=1):
                print('     [{index:4}] - {book}'.format(**locals()))
            print()

            choice = Ln.prompt('please select book number', validKeys=range(1, len(books)+1))
            book_id = books[int(choice)-1]
            # print(book_id);continue

                # - prendiamo il libro per avere i metadati
            if not book_id == prev_book_id:
                _filter = { "_id": book_id }
                book = self._ePubs.get_record(_filter)
                dmBook=DotMap(book, _dynamic=False) # di comodo
                prev_book_id = book_id



            for fld_name in fields:
                result = self._find_words_in_text(data=book[fld_name], words=words, fPRINT=False)
                """
                    res dict{
                       word1 {counter: x data: {(1: [], 2: []} }
                       word2 {counter: x data: {(1: [], 2: []} } }
                       wordn...
                       }
                """
                if result:
                    result=DotMap(result, _dynamic=False)
                    for word in words:
                        ptr=result[word]
                        if ptr.counter < 1: continue
                        if choice=='b': break # return to book_list

                        C.yellowH(text='''
                            result for field [{fld_name}]
                                - id: {dmBook._id}
                                - book: {dmBook.title} - [{dmBook.author}]
                                - word: {word} - instances: {ptr.counter}\
                            '''.format(**locals()),
                                    tab=4)

                        ''' Display data.
                            ruoto all'interno della lista visualizzando
                            [step] results per volta'''
                        _max = ptr.counter
                        _min = 0
                        _from=_min
                        _step=6
                        while True:
                            C.yellowH(text='word: [{word}: {_max}] - {dmBook.title} - [{dmBook.author}]'.format(**locals()), tab=4)
                            if _from>=_max: _from=_max-_step
                            if _from<0: _from=0
                            _to=_from+_step
                            if _to>_max: _to=_max

                            for index in range(_from, _to):
                                item = ptr.data[index+1]
                                print('{0:5} - {1}'.format(index+1, item[0]))
                                for line in item[1:]:
                                    print(' '*7, line)
                                print()

                            choice=Ln.prompt('[n]ext_word [b]ooks_list [+] [-] [t]ag', validKeys='t|n|+|-|b')
                            if   choice in ['n', 'b']: break
                            elif choice in ['+']: _from+=_step
                            elif choice in ['-']: _from-=_step
                            elif choice in ['t']:
                                tags=Ln.prompt('Please enter TAGs (BLANK separator)')
                                book['tags'] = tags.split()
                                if self._execute:
                                    result = self._ePubs.updateField(rec=book, fld_name='tags')
                                    if result.matched_count:
                                        print()
                                        C.cyanH(text='tags {dmBook.tags} have been added'.format(**locals()), tab=4)
                                        print()
                                else:
                                    C.cyanH(text='[DRY-RUN] - tags {dmBook.tags} have been added'.format(**locals()), tab=4)





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
                # logger.debug3('alpha word', [word, word2])
                pass
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




