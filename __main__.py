#!/usr/bin/python3
# Progamma per a sincronizzazione dei dati presenti su Drive
#
# updated by ...: Loreto Notarantonio
# Version ......: 21-04-2020 11.52.18
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
    fCONSOLE         = inpArgs.log_console
    _data            = Ln.readConfigFile()
    config           = DotMap(_data['content'])
    prj_name         = _data['prjname']
    script_path      = _data['script_path']
    yaml_config_file = _data['yaml_config_file']


    # --- setting logger
    log_dir     = os.path.join(script_path, 'log')
    log_file   = os.path.abspath(os.path.join(log_dir, '{prj_name}_{inpArgs.action}.log'.format(**locals())))
    # log_file    = _basename + inpArgs.action + '.log'
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




    myDB=LnEBooks(gv, db_name='eBooks')
    if 'update_fieldx' in inpArgs:
        result = myDB.update_field_many( )

    elif 'search' in inpArgs:
        result = myDB.main_search( field_name=inpArgs.fieldname, words=inpArgs.words, ignore_case=True)

    elif 'multi_search' in inpArgs:
        result = myDB.multiple_field_search(fields=inpArgs.fields, words=inpArgs.words, ignore_case=True)

    elif 'book_search' in inpArgs:
        result = myDB.eBook_search(words=inpArgs.words, book_id=inpArgs.id, ignore_case=True)

    elif 'load' in inpArgs:
        input_dir=inpArgs.dir if inpArgs.dir else config.directories.epub_input_dir
        target_dir=config.directories.epub_target_dir if inpArgs.move_file else None

        myDB.load_eBooks(input_dir, file_pattern='.epub', target_dir=target_dir)

    elif 'dictionary' in inpArgs:
        myDB.build_dictionary()




def test():
    '''
    ./__main__.py book_search --words ciao dopo --id Jess_L_Oltre_le_bugie
    ./__main__.py search --field title --words sceglier

    - cerca nei int title + author
    ./__main__.py search --field _id --words domani

    - load book into dictionary
    ./__main__.py  load --author --chapters --title --description
    '''


