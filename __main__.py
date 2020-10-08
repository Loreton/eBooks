#!/usr/bin/python3
#
# updated by ...: Loreto Notarantonio
# Version ......: 08-10-2020 11.53.36
#
import  sys; sys.dont_write_bytecode = True
import  os
from    pathlib import Path

from    lnLib.colorLN import LnColor; C=LnColor()
from    lnLib.promptLN import prompt; prompt(gVars={"color":LnColor()})
from    lnLib.loggerLN import setLogger

import  lnLib.monkeyPathLN as PathLN
import  lnLib.monkeyBenedictLN # per caricare i miei metodi

from    Source.parseInputLN import parseInput
from    lnLib.configurationLoader import LoadConfigFile
from    lnLib.resolveDictVars import ResolveDictVars

from    Source.eBooksLN import eBooksLN



######################################
# sample call:
#
######################################
if __name__ == '__main__':
    """ read Main configuration file hust for logger info"""
    myConf=LoadConfigFile(filename=f'config/eBooks.yml')

    """ logger """
    log_cfg=myConf.pop('main.logger') # remove logger tree
    logger=setLogger(log_cfg)
    PathLN.setLoggerLN(logger)

    script_path=Path(sys.argv[0]).resolve().parent # ... then up one level
    os.environ['script_path']=str(script_path) # potrebbe essere usata nel config_file

    ResolveDictVars(d=myConf, myLogger=logger, value_sep='/')
    ebooks=myConf['ebooks']

    """ parsing input """
    args, inp_log, dbg=parseInput(color=LnColor())

    """ override logger with input parameters """
    if inp_log.level:   logger.set_level(inp_log.level)
    if inp_log.console: logger.set_console(inp_log.console)
    if inp_log.modules: logger.set_modules(inp_log.modules)

    logger.info('input   arguments', vars(args))
    logger.debug3('logging arguments', inp_log)
    logger.debug3('debug   arguments', vars(dbg))
    # -------------------------------


    dbname=args.db_name if args.db_name else ebooks['dbase_name']
    myDB=eBooksLN(db_name=dbname, inp_args=args)
    if 'update_fieldx' in args:
        result = myDB.update_field_many( )

    # elif 'search' in args:
    #     result = myDB.main_search( field_name=args.fieldname, words=args.words, ignore_case=True)

    # elif 'search' in args:
    #     result = myDB.field_search(
    #                     fld_name=args.field,
    #                     words=args.words,
    #                     book_id=args.book_id,
    #                     ignore_case=True)

    elif 'search' in args.action:
        # if len(args.words) == 1:
        #     result = myDB.search_one_word(
        #             fld_name=args.field,
        #             word=args.words,
        #             )
        #     for item in result:
        #         print(item)
        #     print(len(result))

        if args.near and len(args.words)==2:
            records = myDB.search_two_near_words(
                    fld_name=args.field,
                    words=args.words,
                    near_val=args.near,
                    )
            myDB.manage_display(records)



            # for item in result:
            #     if '_id' in item:
            #         print(item['_id'])
            #     else:
            #         print(item)
            print(len(result))

        elif len(args.words) > 0 and args.regex:
            records = myDB.search_more_words_regex(
                    fld_name=args.field,
                    words=args.words,
                    )
            print(len(records))

            #     if '_id' in item:
            #         print(item['_id'])
            #     else:
            #         print(item)

        # elif len(args.words) > 0:
        #     result = myDB.search_more_words(
        #             fld_name=args.field,
        #             words=args.words,
        #             )
        #     # for item in result:
        #     #     if '_id' in item:
        #     #         print(item['_id'])
        #     #     else:
        #     #         print(item)
        #     print(len(result))



    # elif 'regex' in args:
    #     # result = myDB.search_perf(
    #     result = myDB.regex_near_search(
    #     # result = myDB.regex_near_search_step2(
    #     # result = myDB.regex_near_search_OK(
    #                     fld_name=args.field,
    #                     words=args.words,
    #                     near=args.near,
    #                     ignore_case=True)

    # elif 'book_search' in args:
    #     result = myDB.eBook_search(words=args.words, book_id=args.id, ignore_case=True)

    elif 'load' in args:
        input_dir=args.dir if args.dir else config.main.epub_input_dir
        target_dir=config.main.epub_target_dir if args.move_file else None

        myDB.load_eBooks(input_dir, file_pattern=args.ftype, target_dir=target_dir)

    elif 'build' in args:
        myDB.build_dictionary(fields=args.fields, force_indexing=args.force_indexing)

    elif 'change_id' in args:
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


