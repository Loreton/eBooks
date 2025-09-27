#! /usr/bin/env python3
# updated by ...: Loreto Notarantonio
# Date .........: 27-09-2025 11.44.52
#

import sys; sys.dont_write_bytecode=True
import os
from types import SimpleNamespace

from pathlib import Path


import  Source
from    Source import  setupLogger, setMainVars ### definito in __init__.py
from    ParseInput import ParseInput
# from    mainGlobalVars import setMainVars
import  eBooks
from    benedict import benedict


from functionExecutionTime import lnTimeIt




# ######################################################
# # get list of files recursive
# ######################################################
def fileList(root_path, folder='', pattern='*.*'):
    root_path=Path(root_path)
    root_path=root_path / folder
    file_list=list(root_path.glob(f'**/{pattern}'))

    return file_list






###################################################
#    M A I N
###################################################
if __name__ == '__main__':

    ### --- select global vars definition type
    fBENEDICT = False
    gv = SimpleNamespace()
    if fBENEDICT:
        gv = benedict(keyattr_enabled=True, keyattr_dynamic=False)  # copy all input args to gv

    gv.fBENEDICT = fBENEDICT ### --- potrebbe essere utile in altri punti del codice
    gv.project_name = "eBooks"
    gv.version = f"{gv.project_name} version: V2025-09-27_114452"

    ### --- setup logging
    logger = setupLogger(gv.project_name)
    logger.warning(gv.version)
    gv.logger    = logger
    gv.color                = gv.logger.Colors
    gv.logLevels            = list(gv.logger.logLevels.keys())

    ### --- parse Input
    args = ParseInput(gVars=gv)
    gv.args = vars(args) if fBENEDICT else args

    ### --- change current console logging level as input required
    logger.setLoggerLevel(console_level=args.log_console_level)

    ### --- set all main project global variables
    gv = setMainVars(gVars=gv, search_paths=["conf"])

    print(gv.color.red, "ciao", gv.color.reset)
    print(gv.color.yellow, "come stai?\n", gv.color.reset)

    sys.exit()
    eBooks.process(gv)


    '''
    ebookRootDir=Path(args.dir_name).resolve()
    search_string=args.search


    files=fileList(ebookRootDir, pattern=f'*{args.extension}')
    # for file in files[0:3]:
    search_strings = " ".join(gv.args["search"])

    for filepath in files:
        file = Path(filepath)
        fileOut = f"{args.out_dir}/{filepath.stem.replace(' ', '_')}.txt"

        logger.info("reading book: %s", file.name)
        clean_text = eBooks.read_epub(gVars=gv, epub_file=filepath, fileout=fileOut)

        lnTimeIt(fStart=True)
        text_split(clean_text)
        lnTimeIt("fine dello splitting del eBook", fStart=False, fPause=False)



        logger.info("searching string: %s", search_strings)
        wordsFound = eBooks.searchString(source_string=clean_text, search_string=search_strings, exact_match=True, word_distance=5)
        lnTimeIt(fStart=False)
        for item in wordsFound:
            # logger.notify(item)
            print(item)
            print()

        import pdb; pdb.set_trace() # by Loreto
        # print(filepath);
    '''
    #     fileOut = f"{args.out_dir}/{filepath.stem.replace(' ', '_')}.txt"
    #     for name in args.author:
    #         if name == "*" or name.lower() in str(filepath).lower():
    #             process_file(fileIn=filepath, fileOut=fileOut, search_string=search_string, fVerbose=args.verbose)
    '''
    '''
