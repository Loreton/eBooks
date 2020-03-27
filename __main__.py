#!/usr/bin/python3
# Progamma per a sincronizzazione dei dati presenti su Drive
#
# updated by ...: Loreto Notarantonio
# Version ......: 27-03-2020 17.36.08
#
import sys; sys.dont_write_bytecode = True
import os
from dotmap import DotMap



import Source.LnLib  as Ln
import Source.Main  as Prj
from  Source.Mongo.LnMongo import MongoDB
import Source.eBookProcess.eBookLib  as Process

TAB1 = '    '



# import platform
# OS_platform = platform.system()




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

    MY_COLLECTION = 'posts'
    myDB = MongoDB(dbname='db01', logger=lnLogger)
    myDB.deleteCollection(MY_COLLECTION)
    myColl = myDB.openCollection(MY_COLLECTION)



    # for epub_path in config.directories.epub:
    #     Process.eBookLib(gVars=gv, base_path=epub_path, filetype=inpArgs.extension)
    # ePubConverter(script_path)
    # ePubConverter_lineByline(script_path)





