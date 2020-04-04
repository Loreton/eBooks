#!/usr/bin/python3
# Progamma per a sincronizzazione dei dati presenti su Drive
#
# updated by ...: Loreto Notarantonio
# Version ......: 03-04-2020 16.56.11
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




def mongo():
    myDB_instance = MongoDB(db_name='db01', collection_name='posts', myLogger=lnLogger)
    # eBookColl = myDB_instance.collection

    myDB_instance.setFields(['title', 'content', 'author'])
    myDB_instance.setIdFields(['author', 'title'])

    post_data = {
        'title': 'Python and MongoDB',
        'content': 'PyMongo is fun, you guys',
        'author': 'Scott'
    }
    result = myDB_instance.insert(post_data, replace=True)
    print('posts: {0}'.format(result[0]))



    post_data = {
        'title': 'Python and MongoDB2',
        'content': 'PyMongo is fun, you guys',
        'author': 'Scott'
    }
    result = myDB_instance.insert(post_data, replace=True)
    print('posts: {0}'.format(result[0]))





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


    # --- set global variables
    gv          = DotMap(_dynamic=False)
    gv.Ln       = Ln
    gv.lnLogger = lnLogger
    gv.Color    = C
    gv.search   = inpArgs.search


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


    # mongo()


    for epub_path in config.directories.epub:
        Process.eBookLib(gVars=gv, base_path=epub_path, filetype=inpArgs.extension)
    # ePubConverter(script_path)
    # ePubConverter_lineByline(script_path)




