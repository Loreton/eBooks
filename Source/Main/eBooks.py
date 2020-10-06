# xxx!/usr/bin/python3
# Progamma per processare un ebook
#
# updated by ...: Loreto Notarantonio
# Version ......: 15-05-2020 18.20.48
#

import sys
import os
from pathlib import Path
from dotmap import DotMap
import string
import pdb
import re
import textwrap
import yaml, json
import time


import ebooklib
from ebooklib import epub
from ebooklib.utils import parse_html_string
import ebooklib.utils as epubUtil
from bs4 import BeautifulSoup
from Menu import main as Menu

# import nltk
# nltk.download('punkt')

from LnMongoCollection_V02 import MongoCollection

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
        self._execute = inp_args.go

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
                                '_filter', # comodo per fare la ricerca
                                'content',
                                'indexed_fields', # True/False id words into dictionary collection
                                'title',
                                'tags',
                                ])

        self._ePubs.setIdFields(['author_CN', 'title'])
        # eBooks_coll=eBooks.collection

        self._Dictionary = MongoCollection(collection_name='Dictionary', **_args)
        self._Dictionary.setFields(['_id',
                                    '_filter',
                                    'author_word',
                                    'title_word',
                                    'content_word'
                                    'tags_word'
                                    ])
        self._Dictionary.setIdFields(['_id'])




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
            if inp_args.move_file:
                target_file=file + '.err.zip'
                logger.error('renaming file', file, 'to:', target_file, console=True)
                Path(file).rename(target_file)

        return hBook

    def _author_reverse(self, data):
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
            book_data['title']          = _title[0][0]                 if _title else ''
            book_data['author']         = _creator[0][0]               if _creator else ""
            book_data['content']        = []
            book_data['tags']           = []
            book_data['indexed_fields'] = []
            book_data['date']           = _date[0][0].split('T', 1)[0] if _date else ""
            book_data['description']    = _description[0][0]           if _description else ''

        except Exception as why:
            C.error(text=str(why), tab=12, console=True)
            if inp_args.move_file:
                target_file=file + '.err.zip'
                logger.error('renaming file: {file} to {target_file}'.format(**locals()), console=True)
                Path(file).rename(target_file)
            return {}


        if not book_data['title']:
            if SKIP_UNKNOWN:
                C.warning(text="{file} does't contain valid  metadata".format(**locals()), tab=4)
                if inp_args.move_file:
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
        book_data['author_CN'] = self._author_reverse(book_data['author'])

        logger.info('book data', book_data)

        return book_data




    ####################################################
    # - input:
    ####################################################
    def build_dictionary(self, book={}, fields=[], force_indexing=False):
        if book:
            self._book_indexing(book=book, fields=fields, force_indexing=force_indexing)

        else:
            nrec = self._ePubs._collection.find().count()
            index = self._ePubs.set_range(start=0, range=1)
            records = self._ePubs.get_next()
            while records:
                for book in records:
                    index+=1
                    C.yellowH(text='''
                        [{index:5}/{nrec:5}] - {id}
                            book:      {title} - [{author}]
                            indexed:   {indexed}\
                        '''.format( title=book['title'],
                                    author=book['author'],
                                    id=book['_id'],
                                    indexed=book['indexed_fields'],
                                    **locals()), tab=4)
                    # print()
                    self._book_indexing(book=book, fields=fields, force_indexing=force_indexing)
                # Ln.prompt()
                records = self._ePubs.get_next()


    ####################################################
    # - indexing book content
    # -   field indexed: conterrà la lista dei campi indicizzati
    ####################################################
    def _book_indexing(self, book={}, fields=[], force_indexing=False):
        for fld_name in fields:
            if (fld_name in book['indexed_fields']) and not force_indexing:
                C.white(text='field {fld_name} already indexed'.format(**locals()), tab=8)
                continue

            # pdb.set_trace()
            fld_data = []

            # - se ci sono dati nel campo
            if book[fld_name]:
                C.white(text='indexing field {fld_name}'.format(**locals()), tab=8)
                if isinstance(book[fld_name], list):
                    fld_data.extend(book[fld_name])
                else:
                    fld_data.append(book[fld_name])

                min_len=3
                if fld_name in ['author', 'title']: min_len=2
                words = self._content2words(' '.join(fld_data), min_len=min_len)

                lun=len(words)
                logger.info('inserting {lun} words into dictionary'.format(**locals()))
                index=0
                for index, word in enumerate(words, start=1):
                    if not index%500:
                        C.white(text='word processed: {index:5}/{lun}'.format(**locals()), tab=8)

                    # - preparazione default record del dictionary
                    rec={
                        '_id':    word.lower(),
                        '_filter': {'_id': word.lower()},
                        'title_word':  [],
                        'author_word':  [],
                        'content_word':  [],
                        'tags_word':  [],
                    }
                    # modifichiamo il campo che ci interessa
                    dictionary_field_name=fld_name+'_word'
                    rec[dictionary_field_name].append(book['_id']),

                    # - updating record o create it if not exists
                    if self._execute:
                        result = self._Dictionary.updateField(rec, fld_name=dictionary_field_name, create=True)
                    else:
                        logger.console('[DRY-RUN] - record updated.', rec)

                C.white(text='word processed: {index:5}/{lun:5}'.format(**locals()), tab=8)
                if not fld_name in book['indexed_fields']:
                    book['indexed_fields'].append(fld_name)
                    if self._execute: self._ePubs.updateField(rec=book, fld_name='indexed_fields')
            else:
                C.white(text='no word in field {fld_name}'.format(**locals()), tab=8)
        print()


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


            self._ePubs.set_id(book)

            # C.yellowH(text='[{index:06}/{nFiles:06}] - {0} - [{1}]'.format(book['title'], book['author'], **locals()), tab=4)
            curr_book = self._ePubs.exists(rec=book)

            if curr_book:
                _msg='already catalogued'
                book = curr_book
                # printColor=None
                printColor=C.white
                # if inp_args.verbose:
            else:   # - insert book into eBooks_collection
                printColor=C.yellowH
                book['content'] = self._readContent(filename=epub_file)
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
                    if inp_args.move_file:
                        epub_file.rename(epub_file / '.err.zip')
                    continue


            dmBook = DotMap(book, _dynamic=False)
            if inp_args.verbose:
                print()
                printColor(text='''
                [{index:05}/{nFiles:05}]
                    _id:       {dmBook._id}
                    book:      {dmBook.title} - [{dmBook.author}]
                    {_msg}
                    indexed:   {dmBook.indexed_fields}\
                '''.format(**locals()), tab=4)
            else:
                printColor(text='''[{index:05}/{nFiles:05}] book: {dmBook.title} - [{dmBook.author}] '''.format(**locals()), tab=4)


                # - forcing dictionary update
            if inp_args.indexing and not dmBook.indexed_fields:
                _fields = ['content', 'title', 'tags', 'author']
                if self._execute: self._book_indexing(book, fields=_fields )
                indexed_books += 1



            # move file if required
            if target_dir:
                target_file='{target_dir}/{dmBook.title}.epub'.format(**locals())
                target_file='{target_dir}/{dmBook.title}.epub'.format(**locals())
                C.yellowH(text='... moving to:', tab=16)
                C.yellowH(text='dir:   {target_dir}'.format(**locals()), tab=18)
                C.yellowH(text='fname: {dmBook.title}'.format(**locals()), tab=18)

                if self._execute and inp_args.move_file:
                    moved, reason = epub_file.moveTo(target_file, replace=False)
                    if not moved:
                        # - rename source
                        epub_file.rename(epub_file.parent / '{dmBook.title}{epub_file.suffix}_{reason}'.format(**locals()) )





    ####################################################
    # -
    ####################################################
    def _content2words(self, content, min_len=3):
        chars_to_replace = string.printable.replace(string.ascii_letters, '')
        chars_to_replace += '’'
        words_to_discard=[
                        'dalla', 'dalle', 'dallo', 'dall',
                        'della', 'dello', 'dell',
                        'nella', 'nello', 'nelle', 'nell',
                        'alla',  'alle', 'allo', 'all',
                        'il',  'lo', 'la', 'i','gli','le',
                        ]

        # - rimpiazza i primi con i secondi
        table = ''.maketrans('òàùèìé', 'oaueie')
        content = content.translate(table)
        table = ' '.maketrans(chars_to_replace, ' '*(len(chars_to_replace)))
        content = content.translate(table)

        content = [w for w in content.split() if len(w)>=min_len and not w.lower() in words_to_discard]
        logger.info("total words", len(content))
        # - remove duplicates
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
    # - Input:
    # -    fld_name: campo dove effettuare la ricerca
    # -    near:   [word1 {0,5} word2]
    # - NO Dictionary will be used
    # - cerca due parole
    # - \bsono\W+(?:\w+\W+){1,4}?passati\b
    # -
    # -  p=re.compile(r'\b{0}\W+(?:\w+\W+){2}?{1}\b'.format('degli', 'ospiti', '{0,5}'), re.IGNORECASE);p.findall(text)
    ####################################################
    def search_words(self, fld_name, words, ret_full=False, ignore_case=True):
        # pattern = re.compile(word, re.IGNORECASE)
        bookid_list=[]
        fld=fld_name+'_word'
        for word in words:
            _filter = {'_id': word}
            rec = self._Dictionary.get_record(_filter)
            _list = rec[fld]
            print('books for word:', word, ':',len(_list))
            if bookid_list:
                bookid_list = list(set(bookid_list) & set(_list))
            else: # just the first time
                bookid_list.extend(_list)

        if ret_full:
            book_list=[]
            for _id in bookid_list:
                book_list.append(self._ePubs.get_record({'_id': _id}))
            return book_list

        return bookid_list

    ####################################################
    # - Input:
    # -    fld_name: campo dove effettuare la ricerca
    # -    near:   [word1 {0,5} word2]
    # - single word:
    # -     \b(miei|ragazzi)\b
    # -     ^(.*?)(\bpass\b)(.*)$  first occurrency
    # -     ^(.*)(\bpass\b)(.*?)$  last  occurrency
    # - two words:
    # -     \bpass\b.*\btacchi\b
    # - any string:
    # -     (miei|pass2|sono)gi
    # - any words:
    # -     (\bmiei\b|\bpass\b|\bsono\b)gi
    # -     \b(?:miei|pass|sono)\b
    # - AND string:
    # -     \b(miei|pass)\b gi
    # -     (?i)(?s)miei.*?pass.*?sono gi
    # - AND words:
    # -     (?i)(?s)\bmiei\b.*?\bpass\b.*?\bsono\b gi
    # - cerca le parole in ordine
    # - ^(.*?(\bsono\b)(.*?(\btacchi\b)(.*?(\bsono\b)))[^$]*)$
    # - cerca due parole
    # - \bsono\W+(?:\w+\W+){1,4}?passati\b
    # -
    # -  p=re.compile(r'\b{0}\W+(?:\w+\W+){2}?{1}\b'.format('degli', 'ospiti', '{0,5}'), re.IGNORECASE);p.findall(text)
    ####################################################
    def search_more_words_regex(self, fld_name, words, ret_full=False, ignore_case=True):
        # pattern = re.compile(word, re.IGNORECASE)
        # pdb.set_trace()
        bookid_list=[]
        fld=fld_name+'_word'

        _p=r'\b({0})\b'.format('|'.join(words))
        pattern=re.compile(_p, re.IGNORECASE)


        start = time.time()
        my_query = {fld_name: {"$regex": pattern, "$options" : "i" } }
        self._ePubs.set_query(my_query, start=1, range=10)
        records = self._ePubs.get_next(nrecs=9999)
        print(f'Time: {time.time() - start}')


        # if ret_full:
        #     book_list=[]
        #     for _id in bookid_list:
        #         book_list.append(self._ePubs.get_record({'_id': _id}))
        #     return book_list

        return records

    ####################################################
    # - Input:
    # -    fld_name: campo dove effettuare la ricerca
    # -    near:   [word1 {0,5} word2]
    # - NO Dictionary will be used
    # - cerca due parole
    # - \bsono\W+(?:\w+\W+){1,4}?passati\b
    # -
    # -  p=re.compile(r'\b{0}\W+(?:\w+\W+){2}?{1}\b'.format('degli', 'ospiti', '{0,5}'), re.IGNORECASE);p.findall(text)
    ####################################################
    def search_two_near_words(self, fld_name, words, near_val, ignore_case=True):
        _min, _max, = near_val
        if _max<_min: _max=_min
        near = '{0}{1},{2}{3}'.format('{', _min, _max, '}') # {m,M}
        pattern=re.compile(r'\b{words[0]}\W+(?:\w+\W+){near}?{words[1]}\b'.format(**locals()), re.IGNORECASE)

        # - prepare search
        # start = time.time()
        my_query = {fld_name: {"$regex": pattern, "$options" : "i" } }
        self._ePubs.set_query(my_query, start=1, range=10)

        # - run query and return just '_id' field
        records = self._ePubs.get_next(nrecs=9999, ret_field=['_id'], skip_field=[])
        print('record:\n      ', json.dumps(records[0], indent=4, sort_keys=True))

        menu_list=[]
        for book in records:
            menu_list.append(book['_id'])
        self.manage_display(menu_list, pattern)


    def manage_display(self, menu_list, pattern):
        _sep_str = ' #-# '

        STEP=10
        choice = 'f' #default
        # menu_list={}
        # book_list={}

        # pdb.set_trace()
        while True:
            """ ricreiamo la lista per il menu ogni volta che passiamo di qui
                perché aggiorniamo eventuali tags modificati durante
                lo scorrere del menu
            """
            _list=[]
            for item in menu_list:
                book_id = item.split(_sep_str)[0]
                book = self._ePubs.get_record({'_id': book_id})
                entry ='{}{_sep_str}{}'.format(book['_id'], book['tags'], **locals())
                _list.append(entry)

            # - prepara il menu_list
            menu_list = {}
            _list = sorted(_list)
            for index, entry in enumerate(_list, start=1):
                menu_list[index]=entry

            # - menu looping trought the book list
            if not menu_list: break
            choice = Menu(menu_list, return_on_fw=False)

            if choice == 'f':
                continue
            else:
                # - prendiamo il libro selezionato per avere i metadati
                # pdb.set_trace()
                book_id = menu_list[int(choice)].split(_sep_str)[0]
                book = self._ePubs.get_record( {"_id": book_id} )

                # result = RegEx.two_near_words(data=book['content'], regex=pattern, )
                occurrencies=Ln.RegEx.FindIter(pattern, data=book['content'], fPRINT=True)
                self._display_occurrencies(book, occurrencies)

    ####################################################
    # - occurrencies = {
    #        "miei, poi gir\u00f2 bruscamente sui tacchi": [
    #            [ 878, 890 ],
    #            [ 166684, 166721 ],
    #        ]
    #       }
    ####################################################
    def _display_occurrencies(self, book, occurrencies):
        ''' Sample
            {
                "word1": {"counter": 1 },
                "word2": {"counter": 1 },
                "data": {
                            "1": ["Lee Child"],
                            "2": ["Child pippo"],
                        }
            }
        '''
        keys = occurrencies.keys()
        choice = ''
        _max = len(items)
        _min = 0
        _step=4
        inx_from=_min

        # - prepard book info display data
        dmBook=DotMap(book, _dynamic=False) # di comodo
        dis_line=[]
        dis_line.append('')
        dis_line.append('book: {dmBook.title} - [{dmBook.author}]'.format(**locals()))
        dis_line.append('    - id: {dmBook._id}'.format(**locals()))
        dis_line.append('    - tags: {dmBook.tags}'.format(**locals()))
        for item in items:
            counter = len(occurrencies[item])
            dis_line.append('        - item: {item} - instances: {counter}'.format(**locals()))

        while True:
            if choice=='b': break # return to book_list

            # - display book metadata
            for line in dis_line:
                C.yellowH(text=line, tab=8)

            pdb.set_trace()

            ''' Display data.
                ruoto all'interno della lista visualizzando
                [step] results per volta'''

            # - set range to display menu
            if inx_from>=_max: inx_from=_max-_step
            if inx_from<0:     inx_from=0
            inx_to = inx_from+_step
            if inx_to>_max:    inx_to=_max

            # - display data
            for index in range(inx_from, inx_to):
                item = items[index+1]
                print('{0:5} - {1}'.format(index+1, item[0]))
                for line in item[1:]:
                    print(' '*7, line)
                print()

            # - Get keybord input
            choice=Ln.prompt('[n]ext [p]rev [b]ooks_list [t]ag', validKeys='n|p|b|t')
            if   choice in ['b']: break
            elif choice in ['n']: inx_from+=_step
            elif choice in ['p']: inx_from-=_step
            elif choice in ['t']:
                if self._execute:
                    tags=Ln.prompt('Please enter TAGs (BLANK separator)')
                    book['tags'] = tags.split()
                    result = self._ePubs.updateField(rec=book, fld_name='tags')
                    # pdb.set_trace()
                    if result.matched_count:
                        C.cyanH(text='tags {0} have been added'.format(book['tags']), tab=4)
                        self._book_indexing(book, fields=['tags'])
                        print()
                else:
                    C.cyanH(text='in DRY-RUN mode, tag setting not available', tab=4)
                    Ln.prompt()




def main(gVars, dir, file_pattern='.epub', move_file=False):
    global gv, logger, C
    gv     = gVars
    C      = gVars.Color
    logger = gVars.lnLogger
    # args = gVars.args

    # Ln          = gv.Ln
    # ebooks=LnEBooks(db_name='eBooks')
    # ebooks.load_eBooks(dir, file_pattern, move_file)




