#!/usr/bin/python3
# Progamma per a sincronizzazione dei dati presenti su Drive
#
# updated by ...: Loreto Notarantonio
# Version ......: 07-04-2020 13.41.26
#
import sys; sys.dont_write_bytecode = True
import os
from dotmap import DotMap



import Source.LnLib  as Ln
import Source.Main  as Prj
from  Source.Mongo.LnMongo import MongoDB
# from  Source.Mongo.LnMongo import Mongo2DB
# from  Source.Mongo.LnMongo import LnCollection
import Source.eBookProcess.eBookLib  as Process

TAB1 = '    '








######################################
# sample call:
#    python.exe __main__.py
#  // by Loreto VSCode --> https://code.visualstudio.com/docs/python/debugging
######################################
if __name__ == '__main__':
    inpArgs          = Prj.ParseInput()
    fCONSOLE         = inpArgs.log_console
    _data            = Prj.readConfigFile()
    config           = DotMap(_data['content'])
    prj_name         = _data['prjname']
    script_path      = _data['script_path']
    yaml_config_file = _data['yaml_config_file']


    # --- setting logger
    log_dir     = os.path.join(script_path, 'log')
    _basename   = os.path.abspath(os.path.join(log_dir,prj_name))
    log_file    = _basename + '.log'
    stdout_file = _basename + '_stdout.log'
    lnLogger    = Ln.setLogger(filename=log_file, console=fCONSOLE, debug_level=3, dry_run=not inpArgs.go, log_modules=inpArgs.log_modules, color=Ln.Color() )
    lnStdout    = Ln.setLogger(filename=stdout_file, color=Ln.Color() )
    C           = Ln.Color(filename=stdout_file)
    lnLogger.info('input arguments', vars(inpArgs))
    lnLogger.info('configuration data', _data)

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
    # gv.search   = inpArgs.search
    # import pymongo
    # mongow3school()
    # sys.exit()
    # - initialize Mongo
    myDB_instance = MongoDB(db_name='eBooks', collection_name='epub', myLogger=lnLogger)
    myDB_instance.setFields(['title',
                            'author',
                            "date",
                            "description",
                            "identifier",
                            'coverage',
                            'content',
                            'chapters',
                            ])

    myDB_instance.setIdFields(['author', 'title'])


    if 'search' in inpArgs:
        # srcStr=inpArgs.search
        mycol=myDB_instance.collection
        # ebook_coll.create_index([('content', 'text')])
        # ebook_coll.create_index([('author', 'text')])
        # cursor = myDB_instance.search(inpArgs.search)

        # myquery = { "content": srcStr }
        # cursor = ebook_coll.find(myquery)
        # print(cursor.count())
        # for x in cursor:
        #     print(x)


        '''
        # https://docs.mongodb.com/manual/reference/operator/query/regex/
        print()
        print('Find documents where the address starts with the letter "C":')
        myquery = { "author": { "$regex": "^C" }}, { "content": 0 }
        # myquery = {"author": { "$regex": "^C" }},{ "address": 0 }
        mydoc = mycol.find({ "author": { "$regex": "^C" }}, { "content": 0 })
        for x in mydoc:
            print(x['_id'])

        print()
        print('Find document(s) with the title "L\'ora tra la donna e la chitarra":')
        myquery = { "title": "L'ora tra la donna e la chitarra" }
        mydoc = mycol.find(myquery)
        for x in mydoc:
            print(x['_id'])

        print()
        myquery = { "author": '/{inpArgs.search}/i'.format(**locals()) }
        print('Find document(s) containing the string:', end='')
        print(myquery)
        mydoc = mycol.find(myquery)
        for x in mydoc:
            print(x['_id'])

        print()
        print('Find document(s) containing the string:')
        mydoc = myDB_instance.search('author', '^Clemens')
        for x in mydoc:
            print(x['_id'])

        '''
        print()
        print('Search word:')
        mydoc = myDB_instance.search(field_name='title', regex='chitarra', ignore_case=True)
        for x in mydoc:
            print(x['_id'])

        print()
        print('Search word:')
        mydoc = myDB_instance.search(field_name='description', regex='impaurita', ignore_case=True)
        for x in mydoc:
            print(x['_id'])

        print()
        print('Search word:')
        mydoc = myDB_instance.search(field_name=inpArgs.fieldname, regex=inpArgs.pattern, ignore_case=True)
        for x in mydoc:
            print(x['_id'])

        '''
        print('Search word in all:')
        mydoc = myDB_instance.searchWord('impaurita')
        for x in mydoc:
            print(x['_id'])
        '''

    elif 'load' in inpArgs:
        for epub_path in config.directories.epub_input:
            files = Prj.ListFiles(epub_path, filetype=inpArgs.extension)
            for index, file in enumerate(files):
                if index > 10: sys.exit(1)
                C.yellowH(text='working on file {index}: {file}'.format(**locals()))
                book = Process.eBookLib(gVars=gv, file=file)
                # lnLogger.console('book data', book)
                result = myDB_instance.insert(book, replace=True)



