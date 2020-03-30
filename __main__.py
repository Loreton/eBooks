#!/usr/bin/python3
# Progamma per a sincronizzazione dei dati presenti su Drive
#
# updated by ...: Loreto Notarantonio
# Version ......: 30-03-2020 17.55.36
#
import sys; sys.dont_write_bytecode = True
import os
from dotmap import DotMap



import Source.LnLib  as Ln
import Source.Main  as Prj
from  Source.Mongo.LnMongo import MongoDB
from  Source.Mongo.LnMongo import LnCollection
import Source.eBookProcess.eBookLib  as Process

TAB1 = '    '


def main1():
    DB_NAME = 'db01'
    MY_COLLECTION = 'posts'
    myDB = MongoDB(db_name=DB_NAME, myLogger=lnLogger)
    myDB.deleteCollection(MY_COLLECTION)
    eBookColl = myDB.openCollection(MY_COLLECTION)

    post_data = {
        'title': 'Python and MongoDB',
        'content': 'PyMongo is fun, you guys',
        'author': 'Scott'
    }
    result = eBookColl.insert_one(post_data)
    print('One post: {0}'.format(result.inserted_id))



def main2():
    DB_NAME = 'db02'
    MY_COLLECTION = 'posts'
    eBookColl = LnCollection(db_name=DB_NAME, coll_name=MY_COLLECTION, myLogger=lnLogger)
    eBookColl = LnCollection(db_name=DB_NAME, coll_name=MY_COLLECTION, myLogger=lnLogger)

    post_data = {
        'title': 'Python and MongoDB',
        'content': 'PyMongo is fun, you guys',
        'author': 'Scott'
    }
    result = eBookColl.insert_one(post_data)
    print('One post: {0}'.format(result.inserted_id))



######################################
# sample call:
#    python.exe __main__.py
#  // by Loreto VSCode --> https://code.visualstudio.com/docs/python/debugging
######################################
if __name__ == '__main__':
    inpArgs          = Prj.ParseInput()
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
    lnLogger    = Ln.setLogger(filename=log_file, debug_level=3, dry_run=not inpArgs.go, log_modules=inpArgs.log_modules, color=Ln.Color() )
    lnStdout    = Ln.setLogger(filename=stdout_file, color=Ln.Color() )
    C           = Ln.Color(filename=stdout_file)
    lnLogger.info('input arguments', vars(inpArgs))


    # --- set global variables
    gv          = DotMap(_dynamic=False)
    gv.Ln       = Ln
    gv.lnLogger = lnLogger
    gv.Color    = C
    gv.search   = inpArgs.search

    main1()


    # for epub_path in config.directories.epub:
    #     Process.eBookLib(gVars=gv, base_path=epub_path, filetype=inpArgs.extension)
    # ePubConverter(script_path)
    # ePubConverter_lineByline(script_path)




