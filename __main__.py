#!/usr/bin/python3
# Progamma per a sincronizzazione dei dati presenti su Drive
#
# updated by ...: Loreto Notarantonio
# Version ......: 14-04-2020 10.08.11
#
import sys; sys.dont_write_bytecode = True
import os
from dotmap import DotMap
from pathlib import Path

import Source as Ln

from eBooks import main as eBooks_main

TAB1 = '    '








######################################
# sample call:
#    python.exe __main__.py
#  // by Loreto VSCode --> https://code.visualstudio.com/docs/python/debugging
######################################
if __name__ == '__main__':
    inpArgs          = Ln.parseInput()
    fCONSOLE         = inpArgs.log_console
    _data            = Ln.readConfigFile()
    config           = DotMap(_data['content'])
    prj_name         = _data['prjname']
    script_path      = _data['script_path']
    yaml_config_file = _data['yaml_config_file']


    # --- setting logger
    log_dir     = os.path.join(script_path, 'log')
    _basename   = os.path.abspath(os.path.join(log_dir,prj_name))
    log_file    = _basename + '.log'
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

    if 'search' in inpArgs:
        pass
        '''
        mycol=eBooks_coll.collection

        print()
        print('Search word:')
        mydoc = eBooks_coll.search(field_name='title', regex='chitarra', ignore_case=True)
        for x in mydoc:
            print(x['_id'])

        print()
        print('Search word:')
        mydoc = eBooks_coll.search(field_name='description', regex='impaurita', ignore_case=True)
        for x in mydoc:
            print(x['_id'])

        print()
        print('Search word:')
        mydoc = eBooks_coll.search(field_name=inpArgs.fieldname, regex=inpArgs.pattern, ignore_case=True)
        for x in mydoc:
            print(x['_id'])
        '''


    elif 'load' in inpArgs:
        input_dir=inpArgs.dir if inpArgs.dir else config.directories.epub_input
        eBooks_main(gv, input_dir, file_pattern='.epub', move_file=inpArgs.move_file)
        '''
        for epub_path in config.directories.epub_input:

            # - read list of files
            files = Prj.ListFiles(epub_path, filetype=inpArgs.extension)

            # - try to insert each file
            for index, file in enumerate(files, start=1):
                file_path=Path(file)
                if index > 10: sys.exit(1)
                C.yellowH(text='working on file {index:4}: {file_path}'.format(**locals()), end='')

                # - read the book
                book = Process.eBookLib(gVars=gv, file=file_path._str)
                C.yellowH(text=' - {book.title}'.format(**locals()))

                # - insert book into DBase_collection
                result = eBooks.insert(book, replace=True)
                if result['record_0'][0] in ('replaced', 'inserted'):
                    target_file='/mnt/k/tmp/{book.author}/{book.title}.epub'.format(**locals())
                    file_path.moveFile(target_file, replace=False)

                    content = Process.cleanContent(' '.join(book.chapters))
                    for word in content:
                        rec={
                            'word': word,
                            'ebook': book._id
                        }
                        result = Dictionary.updateField(rec, create=True)
        '''

    # sys.exit()



