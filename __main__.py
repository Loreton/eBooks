#!/usr/bin/python3
# Progamma per a sincronizzazione dei dati presenti su Drive
#
# updated by ...: Loreto Notarantonio
# Version ......: 19-04-2020 17.49.24
#
import sys; sys.dont_write_bytecode = True
import os
from dotmap import DotMap
from pathlib import Path
import pdb

import Source as Ln

# from eBooks import main as eBooks_main
from eBooks import LnEBooks

TAB1 = '    '




def search_string(substring, data):
    import re
    # All occurrences of substring in string
    res = [i.start() for i in re.finditer(substring, data)]
    return res



######################################
# sample call:
#    python.exe __main__.py
#  // by Loreto VSCode --> https://code.visualstudio.com/docs/python/debugging
######################################
if __name__ == '__main__':
    inpArgs          = Ln.parseInput()
    if 'test' in inpArgs:
        import textwrap
        C           = Ln.Color()
        # pdb.set_trace()
        _before=100
        _after=150
        text='e notti era andato a letto nella stanza degli ospiti con un’erezione che sembrava quella della pubblicità del Viagra, quella che raccomandava ‘ fatti vedere da un dotto'
        word='ospiti'
        lun=len(word)
        pos=text.find(word)
        _from=pos-_before
        if _from<0: _from=0
        print (text)
        xx = C.yellowH(text=word, get=True)
        new_text=text.replace(word, xx)
        print (new_text)
        tb=textwrap.wrap(new_text, 80, break_long_words=True)
        for l in tb: print('    ', l)

        sys.exit()


    fCONSOLE         = inpArgs.log_console
    _data            = Ln.readConfigFile()
    config           = DotMap(_data['content'])
    prj_name         = _data['prjname']
    script_path      = _data['script_path']
    yaml_config_file = _data['yaml_config_file']


    # --- setting logger
    log_dir     = os.path.join(script_path, 'log')
    _basename   = os.path.abspath(os.path.join(log_dir,prj_name))
    log_file    = _basename + inpArgs.action + '.log'
    lnLogger    = Ln.setLogger(filename=log_file, console=fCONSOLE, debug_level=3, dry_run=not inpArgs.go, log_modules=inpArgs.log_modules, color=Ln.Color() )
    # - STDOUT file if required
    # stdout_file = _basename + '_stdout.log'
    # lnStdout    = Ln.setLogger(filename=stdout_file, color=Ln.Color() )
    C           = Ln.Color()
    lnLogger.info('input arguments', vars(inpArgs))
    lnLogger.info('configuration data', _data)
    Path.setLnMonkey(lnLogger)

    if inpArgs.debug:
        C.setColor(color=C._cyanH)
        print('     Input arguments:')
        for k,v in vars(inpArgs).items():
            print('         {k:<15}: {v}'.format(**locals()))
        print()
        C.setColor(color=C._yellowH)
        print('     {0:<15}: {1}'.format('prj_name', prj_name))
        print('     {0:<15}: {1}'.format('ScriptDir', str(script_path)))
        print('     {0:<15}: {1}'.format('config file', yaml_config_file))
        print()
        sys.exit(1)

    # --- set global variables
    gv          = DotMap(_dynamic=False)
    gv.Ln       = Ln
    gv.lnLogger = lnLogger
    gv.Color    = C
    gv.args    = inpArgs


    '''
    # - initialize Mongo
    eBooks = MongoCollection(db_name='eBooks', collection_name='epub', myLogger=lnLogger, server_name='127.0.0.1', server_port='27017')
    eBooks.setFields(['title',
                            'author',
                            "date",
                            "description",
                            "identifier",
                            'chapters',
                            ])

    eBooks.setIdFields(['author', 'title'])
    # eBooks_coll=eBooks.collection

    Dictionary = MongoCollection(db_name='eBooks', collection_name='Dictionary', myLogger=lnLogger, server_name='127.0.0.1', server_port='27017')
    Dictionary.setFields(['word',
                            'ebook',
                            ])
    Dictionary.setIdFields(['word'])
    # dict_coll=Dictionary.collection




    # eBooks_DB = MongoDB.dbConnect(db_name='eBooks', server_name='127.0.0.1', server_port='27017', myLogger=lnLogger)
    # eBooks = MongoDB(db=eBooks_DB, collection_name='epub')
    # Dictionary = MongoDB(db=eBooks_DB, collection_name='dictionary')
    '''


    myDB=LnEBooks(gv, db_name='eBooks')
    if 'update_fieldx' in inpArgs:
        result = myDB.update_field_many( )

    elif 'search' in inpArgs:
        # pdb.set_trace()
        # for substr in inpArgs.words:
        result = myDB.main_search( field_name=inpArgs.fieldname, words=inpArgs.words, ignore_case=True)

        '''
        strToSearch = inpArgs.text_to_search
        ebook_list = myDB.search(regex=strToSearch, field_name=inpArgs.fieldname, ignore_case=True)

        ebook_coll = myDB._ePubs.collection
        for book_id in ebook_list:
            myquery = { "_id": book_id }
            mydoc = ebook_coll.find(myquery)
            for x in mydoc:
                print(x['author'], '-', x['title'])
                STR_FOUND=False
                for chap in x['chapters']:
                    occurrencies = search_string(strToSearch, chap)
                    if occurrencies:
                        STR_FOUND=True
                        _before=60
                        _after=100
                        for pos in occurrencies:
                            lun=len(strToSearch)
                            C.cyan(text=chap[pos-_before:pos], end='')
                            C.cyanH(text=strToSearch, end='')
                            C.cyan(text=chap[pos+lun:pos+lun+_after])
                            print()

                if STR_FOUND:
                    Ln.prompt('continue....')
        '''


    elif 'load' in inpArgs:
        input_dir=inpArgs.dir if inpArgs.dir else config.directories.epub_input_dir
        target_dir=config.directories.epub_target_dir if inpArgs.move_file else None

        myDB.load_eBooks(input_dir, file_pattern='.epub', target_dir=target_dir)

    elif 'dictionary' in inpArgs:
        if inpArgs.optimize:
            myDB.optimize_dictionary()







