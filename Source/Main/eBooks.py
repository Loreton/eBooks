# xxx!/usr/bin/python3
# Progamma per processare un ebook
#
# updated by ...: Loreto Notarantonio
# Version ......: 05-05-2020 17.36.52
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
    def update_field_many(self):
        result = self._ePubs.updateField_many(
                {'indexed': False},
                {'$set': {'indexed': []}}
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
                    epub_file.rename(epub_file / '.err.zip')
                    continue

            dmBook = DotMap(book, _dynamic=False)
            C.yellowH(text='''
                [{index:05}/{nFiles:05}]
                    _id:       {dmBook._id}
                    book:      {dmBook.title} - [{dmBook.author}]
                    {_msg}
                    indexed:   {dmBook.indexed_fields}\
                '''.format(**locals()), tab=4)


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

                if self._execute:
                    moved, reason = epub_file.moveTo(target_file, replace=False)
                    if not moved:
                        # - rename source
                        epub_file.rename(epub_file.parent / '{dmBook.title}{epub_file.suffix}_{reason}'.format(**locals()) )






        # All occurrencies of substring in string
    def search_string(self, substring, data):
        import re
        res = [i.start() for i in re.finditer(substring, data)]
        return res




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
    def _find_words_in_text(self, data=[], words=[], near=False, fPRINT=False):
        if isinstance(data, (str)):
            data=[data]

        _before=inp_args.text_size
        _after=inp_args.text_size
        result = {}

        # - preparazione word colorate
        colors = [C.magentaH, C.yellowH, C.cyanH, C.redH, C.greenH, C.blueH, C.whiteH]

        for word in words:
            result[word] = {}
            result[word]['counter'] = 0
            result['data'] = {}

        counter=0
        for item in data: # sono capitoli, descrizione, titoli o altro
            for word in words:
                occurrencies = [i.start() for i in re.finditer(word, item, flags=re.IGNORECASE)]
                word_len=len(word)

                for pos in occurrencies:
                    # incr counter for specific word
                    result[word]['counter'] += 1
                    counter += 1 # counter totale

                    # - get text around the found word
                    _from=0 if pos-_before<0 else pos-_before
                    _to=pos+word_len+_after
                    text=item[_from:_to].replace('\n', ' ')
                    new_text = ' '.join(text.split()) # remove multiple blanks

                    '''
                    new_text=text.replace(cur_word, colored_word) # no good perché case-sensitive

                    redata = re.compile(re.escape(cur_word), re.IGNORECASE)
                    new_text = redata.sub(colored_word, text)

                    '''

                    # replace word(s) with colored_word
                    # ruotiamo sulle word in modo da colorarle
                    # se fossero presenti nello stesso testo
                    for i, w in enumerate(words):
                        colored_word = colors[i](text=w, get=True)
                        new_text = re.sub(w, colored_word, new_text, flags=re.IGNORECASE)

                    # - wrap text to easy displaying
                    tb=textwrap.wrap(new_text, 80, break_long_words=True)

                    # - save it into result list
                    result['data'][counter] = []
                    result['data'][counter].extend(tb)

                    if fPRINT:
                        for l in tb:
                            print('    ', l)
                        print()


        return result





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


    def Export_words(self, file_out):
        f = Path(file_out)



    ####################################################
    # - Search the words for a specific field
    # -
    # - data = {
    # -           word_name1: counter
    # -           word_name2: counter
    # -           word_name..n: counter
    # -           ebooks: [] (book_id list cvontainig all the words)
    # -         }
    ####################################################
    def _displayResults(self, book, data):
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
        dis_data = data.pop('data', [])
        words = data.keys()
        choice = ''
        _max = len(dis_data)
        _min = 0
        _step=4
        _from=_min

        # - prepard book info display data
        dmBook=DotMap(book, _dynamic=False) # di comodo
        dis_line=[]
        dis_line.append('')
        dis_line.append('book: {dmBook.title} - [{dmBook.author}]'.format(**locals()))
        dis_line.append('    - id: {dmBook._id}'.format(**locals()))
        dis_line.append('    - tags: {dmBook.tags}'.format(**locals()))
        for word in words:
            counter = data[word]['counter']
            dis_line.append('        - word: {word} - instances: {counter}'.format(**locals()))

        while True:
            if choice=='b': break # return to book_list

            # - display book metadata
            for line in dis_line:
                C.yellowH(text=line, tab=8)


            ''' Display data.
                ruoto all'interno della lista visualizzando
                [step] results per volta'''

            # - set range to display menu
            if _from>=_max: _from=_max-_step
            if _from<0:     _from=0
            _to = _from+_step
            if _to>_max:    _to=_max

            # - display data
            for index in range(_from, _to):
                item = dis_data[index+1]
                print('{0:5} - {1}'.format(index+1, item[0]))
                for line in item[1:]:
                    print(' '*7, line)
                print()

            # - Get keybord input
            choice=Ln.prompt('[n]ext [p]rev [b]ooks_list [t]ag', validKeys='n|p|b|t')
            if   choice in ['b']: break
            elif choice in ['n']: _from+=_step
            elif choice in ['p']: _from-=_step
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




    ####################################################
    # - Search the words for a specific field
    # - using dictionary collection
    # return: list of book_id
    ####################################################
    def _dictionary_search(self, words, field, ignore_case=True):
        bookid_list = []
        ret_dict = {}
        ret_dict['books'] = []
        ret_dict['rec_found'] = 0

        # - Search the words for a specific field
        fld = field+'_word'
        for word in words:
            # - search in all Dictionary words
            result = self._Dictionary.search(field_name='_id', regex=word, ignore_case=ignore_case)
            word_list = []
            for x in result:
                word_list.extend(x[fld])

            ret_dict[word] = len(word_list) # save result

            # - ANDing tra le varie word_list
            C.yellowH(text='Word {0:<10} found in {1:5} books'.format(word, len(word_list)), tab=4)
            if bookid_list:
                bookid_list = list(set(bookid_list) & set(word_list))
            else: # just the first time
                bookid_list = word_list[:]


        ret_dict['books'] = bookid_list
        ret_dict['rec_found'] = len(bookid_list)
        C.cyanH(text='After ANDing remain {0} book(s) containing all your words.'.format(len(bookid_list)), tab=4)
        print()
        return ret_dict

    ####################################################
    # - Search the words for a specific field
    # - using dictionary collection
    # return: list of book_id
    ####################################################
    def _ePub_direct_search(self, fld_name, words, ignore_case=True):
        bookid_list = []
        ret_dict = {}

        # - Search the words for a specific field
        for word in words:
            # - search in all Dictionary words
            result = self._ePubs.search(field_name=fld_name, regex=word, ignore_case=ignore_case)
            print(result.count())
            word_list = []
            for x in result:
                print(x['_id'])
                word_list.append(x['_id'])

            ret_dict[word] = len(word_list) # save result

            # - ANDing tra le varie word_list
            C.yellowH(text='Word {0:<10} found in {1:5} books'.format(word, len(word_list)), tab=4)
            if bookid_list:
                bookid_list = list(set(bookid_list) & set(word_list))
            else: # just the first time
                bookid_list = word_list[:]


        ret_dict['books'] = bookid_list
        ret_dict['rec_found'] = len(bookid_list)
        C.cyanH(text='After ANDing remain {0} book(s) containing all your words.'.format(len(bookid_list)), tab=4)
        print()
        return ret_dict


    def dict_to_json(self, my_dict, indent=4, sort_keys=True):
        my_json = json.dumps(my_dict, indent=indent, sort_keys=sort_keys)
        return my_json

    ####################################################
    # - Search books using dictionary collection
    # - Input:
    # -    fields:  campo/i dove effettuare la ricerca
    # -    words:   stringa/stringhe da ricercare (in AND)
    # -    book_id: se presente si cerca solo al suo interno
    ####################################################
    def field_search(self, fld_name, words=[], book_id=None, ignore_case=True):
        # if 'all' in fields:

            # fields=self._ePubs.fields
        # words=['gatto', 'tempo', 'iggulden', 'porte', 'roma']
        # words=['child', 'lee']

        # - torna la lista dei libri che contengono le words (in AND)
        result = self._dictionary_search(words=words, field=fld_name, ignore_case=ignore_case)
        '''
            result = {
                      word_name1: counter
                      word_name2: counter
                      word_name..n: counter
                      ebooks: [] (book_id list cvontainig all the words)
                    }
        '''
        prev_book_id = None
        bookid_list = sorted(result['books'])
        nRecs=len(bookid_list)+1
        while True:
            for index, _book_id in enumerate(bookid_list, start=1):
                print('     [{index:4}] - {_book_id}'.format(**locals()))
            print()

            # - select book to see results
            choice = Ln.prompt('please select book number', validKeys=range(1, nRecs))
            book_id = bookid_list[int(choice)-1]

                # - prendiamo il libro per avere i metadati
            if not book_id == prev_book_id:
                _filter = { "_id": book_id }
                book = self._ePubs.get_record(_filter)
                dmBook=DotMap(book, _dynamic=False) # di comodo
                prev_book_id = book_id

            result = self._find_words_in_text(data=book[fld_name], words=words, fPRINT=False)
            self._displayResults(book, result)

        return ret_list


    ####################################################
    # - Input:
    # -    fld_name: campo dove effettuare la ricerca
    # -    words:   stringa/stringhe da ricercare (in AND)
    # - NO Dictionary will be used
    # - cerca due parole
    # - \bsono\W+(?:\w+\W+){1,4}?passati\b
    # -
    # -  p=re.compile(r'\b{0}\W+(?:\w+\W+){2}?{1}\b'.format('degli', 'ospiti', '{0,5}'), re.IGNORECASE);p.findall(text)
    ####################################################
    def regex_search(self, fld_name, regex=[], near=[], ignore_case=True):
        # - torna la lista dei libri che contengono le words (in AND)
        # regex=r'\b{0}\W+(?:\w+\W+){1,4}?{0}\b'.format(words[0], words[1])
        if near:
            _word1, _minmax, _word2 = near[0].split()
            # minmax='{'+'{_min},{_max}'.format(**locals())+'}'
            # minmax='{'+'{_minmax}'.format(**locals())+'}'
            pattern=re.compile(r'\b{_word1}\W+(?:\w+\W+){_minmax}?{_word2}\b'.format(**locals()), re.IGNORECASE)
            # pattern.findall()
            words = [_word1, _word2]


        my_query = {fld_name: {"$regex": pattern, "$options" : "i" } }
        self._ePubs.set_query(my_query)
        index = self._ePubs.set_range(start=1, range=10)
        # result = self._ePubs.get_next(query=my_query)
        # nRecs=self._ePubs.count()
        bookid_list=[]
        records = self._ePubs.get_next()
        while records:
            for book in records:
                bookid_list.append(book['_id'])
            records = None
            # records = self._ePubs.get_next()

        # - loop trought the books
        prev_book_id = None
        bookid_list = sorted(bookid_list)
        nRecs=len(bookid_list)+1
        while True:
            for index, _book_id in enumerate(bookid_list, start=1):
                print('     [{index:4}] - {_book_id}'.format(**locals()))
            print()

            # - select book to see results
            choice = Ln.prompt('please select book number', validKeys=range(1, nRecs))
            book_id = bookid_list[int(choice)-1]

                # - prendiamo il libro per avere i metadati
            if not book_id == prev_book_id:
                _filter = { "_id": book_id }
                book = self._ePubs.get_record(_filter)
                dmBook=DotMap(book, _dynamic=False) # di comodo
                prev_book_id = book_id


            result = self.text_near_occurrencies(regex=pattern, data=book['content'])
            # for item in data: # sono capitoli, descrizione, titoli o altro
            #     occurrencies = [i.start() for i in pattern.finditer(item)]
            #     item_len=len(item)
            #     result = {}
            # result = self._find_words_in_text(data=book[fld_name], words=words, fPRINT=False)
            # occurrencies = [i.start() for i in re.finditer(word, item, flags=re.IGNORECASE)]
            self._displayResults(book, result)

        return ret_list


    #################################################
    # - near...
    # p=re.compile(r'\b{0}\W+(?:\w+\W+){2}?{1}\b'.format('stanza', 'ospiti', '{0,5}'))
    # p=re.compile('stanza', re.IGNORECASE)
    # -----
    # p.findall(text)
    # p.findall(text, re.IGNORECASE)
    #################################################
    def text_near_occurrencies(self, regex, data=[], fPRINT=False):
        if isinstance(data, (str)):
            data=[data]

        _before=inp_args.text_size
        _after=inp_args.text_size
        result = {}

        result['data'] = {}

        counter=0
        for item in data: # sono capitoli, descrizione, titoli o altro
            occurrencies = [(i.start(), i.end(), i.group()) for i in regex.finditer(item)]
            for res in occurrencies:
                near_start, near_end, near_str = res
                near_len=len(near_str)
                regex_01 = re.compile(re.escape(near_str), re.IGNORECASE)

                # - create entry in result
                if not near_str in result.keys():
                    result[near_str] = {}
                    result[near_str]['counter'] = 0

                # - get text around the near string
                _from=near_start if near_start-_before<0 else near_start-_before
                _to=near_start+near_len+_after
                text=item[_from:_to].replace('\n', ' ')
                new_text = ' '.join(text.split()) # remove multiple blanks

                # incr counter for specific word
                result[near_str]['counter'] += 1
                counter += 1 # counter totale

                # replace near_string with colored_str
                colored_str = C.magentaH(text=near_str, get=True)
                new_text = regex_01.sub(colored_str, new_text)

                # - wrap text to easy displaying
                tb=textwrap.wrap(new_text, 80, break_long_words=True)

                # - save it into result list
                result['data'][counter] = []
                result['data'][counter].extend(tb)

                if fPRINT:
                    for l in tb:
                        print('    ', l)
                    print()


        return result


def main(gVars, dir, file_pattern='.epub', move_file=False):
    global gv, logger, C
    gv     = gVars
    C      = gVars.Color
    logger = gVars.lnLogger
    args = gVars.args

    Ln          = gv.Ln
    # ebooks=LnEBooks(db_name='eBooks')
    # ebooks.load_eBooks(dir, file_pattern, move_file)




