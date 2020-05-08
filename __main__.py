#!/usr/bin/python3
# Progamma per a sincronizzazione dei dati presenti su Drive
#
# updated by ...: Loreto Notarantonio
# Version ......: 08-05-2020 08.57.49
#
import sys; sys.dont_write_bytecode = True
import os
from dotmap import DotMap
from pathlib import Path
import pdb

import Source as Ln

# from eBooks import main as eBooks_main
from eBooks import LnEBooks



######################################
# sample call:
#    python.exe __main__.py
#  // by Loreto VSCode --> https://code.visualstudio.com/docs/python/debugging
######################################
if __name__ == '__main__':
    inpArgs          = Ln.parseInput()
    _data            = Ln.readConfigFile()
    fCONSOLE         = inpArgs.log_console
    config           = DotMap(_data['content'])
    prj_name         = _data['prjname']
    script_path      = _data['script_path']
    yaml_config_file = _data['yaml_config_file']


    # --- setting logger
    if inpArgs.log:
        log_dir  = os.path.join(script_path, 'log')
        log_file = os.path.abspath(os.path.join(log_dir, '{prj_name}_{inpArgs.action}.log'.format(**locals())))
    else:
        log_file = None
    lnLogger = Ln.setLogger(filename=log_file, console=fCONSOLE, debug_level=3, log_modules=inpArgs.log_modules, color=Ln.Color() )

    # - STDOUT file if required
    # stdout_file = _basename + '_stdout.log'
    # lnStdout    = Ln.setLogger(filename=stdout_file, color=Ln.Color() )
    #
    # --- setting logger

    # data1 = ['uno', 'due']
    # data2 = [1,2,3,4]
    # lnLogger.error('renaming file', 'pippo', 'pluto', data1, console=True)
    # lnLogger.error('renaming file', data1, data2, console=True)
    # sys.exit()

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

    C    = Ln.Color()
    # --- set global variables
    gv          = DotMap(_dynamic=False)
    gv.Ln       = Ln
    gv.lnLogger = lnLogger
    gv.Color    = C
    gv.args     = inpArgs


    dbname=inpArgs.db_name if inpArgs.db_name else config.main.dbase_name
    myDB=LnEBooks(gv, db_name=dbname)
    if 'update_fieldx' in inpArgs:
        result = myDB.update_field_many( )

    # elif 'search' in inpArgs:
    #     result = myDB.main_search( field_name=inpArgs.fieldname, words=inpArgs.words, ignore_case=True)

    elif 'search' in inpArgs:
        result = myDB.field_search(
                        fld_name=inpArgs.field,
                        words=inpArgs.words,
                        book_id=inpArgs.book_id,
                        ignore_case=True)

    elif 'regex' in inpArgs:
        # result = myDB.search_perf(
        result = myDB.regex_near_search(
        # result = myDB.regex_near_search_step2(
                        fld_name=inpArgs.field,
                        near=inpArgs.near,
                        ignore_case=True)

    # elif 'book_search' in inpArgs:
    #     result = myDB.eBook_search(words=inpArgs.words, book_id=inpArgs.id, ignore_case=True)

    elif 'load' in inpArgs:
        input_dir=inpArgs.dir if inpArgs.dir else config.main.epub_input_dir
        target_dir=config.main.epub_target_dir if inpArgs.move_file else None

        myDB.load_eBooks(input_dir, file_pattern=inpArgs.ftype, target_dir=target_dir)

    elif 'build' in inpArgs:
        myDB.build_dictionary(fields=inpArgs.fields, force_indexing=inpArgs.force_indexing)

    elif 'change_id' in inpArgs:
        myDB.change_ID()




def test():
    '''
    ./__main__.py book_search --words ciao dopo --id Jess_L_Oltre_le_bugie
    ./__main__.py search --field title --words sceglier

    - cerca nei int title + author
    ./__main__.py search --field _id --words domani

    - load book into dictionary
    ./__main__.py  load --author --chapters --title --description
    '''


