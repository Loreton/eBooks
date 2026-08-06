#!/usr/bin/env python33
# ruff: noqa: I001 - Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
# -*- coding: iso-8859-1 -*-

# updated by ...: Loreto Notarantonio
# Date .........: 30-09-2025 18.02.44



import sys
# import os
# from types import SimpleNamespace
import argparse

# from pyLnLib.context import ctx
from pyLnLib.colors import get_colors
from pyLnLib.logger import get_logger

C=get_colors()
logger=get_logger()




##############################################################
# - Parse Input
##############################################################
def parseInput() -> argparse.Namespace:
    global v
    from types import SimpleNamespace
    v=SimpleNamespace(
        default_color=C.yellow,
        metavar_optional=f'{C.white}<optional>{C.reset}',
        metavar_mandatory=f'{C.white}<mandatory>{C.reset}',
    )
    v.default=f'{v.default_color}(default: %(default)s){C.reset}\n\n'


    def common_options(subp):
        logger_levels: list[str]=logger.get_log_levels()

        ### --- mi serve per avere la entry negli args e creare poi la entry "product"
        # subp.add_argument('--{0}'.format(name), action='store_true', default=True)

        execution_flags = subp.add_argument_group(f'{C.white}Execution flags{C.reset}')
        execution_flags.add_argument('--go',            action='store_true', help=f'{C.green}specify if command must be executed. {v.default}')
        execution_flags.add_argument('--display-args',  action='store_true', help=f'{C.green}Display arguments {v.default}')
        # execution_flags.add_argument('--vars-project',  action='store_true', help=f'{C.green}Display project variables {v.default}')
        # execution_flags.add_argument('--editor',        action='store_true', help=f'{C.green}display generated files on editor. {v.default}')
        # execution_flags.add_argument('--test',          action='store_true', help=f'{C.green}skip remote access {v.default}')


        execution_flags.add_argument( "--console-log-level",
                                metavar='',
                                type=str.lower,
                                required=False,
                                default='info',
                                help=f"""{C.green}set console logger level:
                                        {logger_levels}{v.default}
                                        \n\n""".replace('  ', '')
                            )


    def searchingFlags(my_parser):
        flags = my_parser.add_argument_group(f'{C.white}Searching flags{C.reset}')
        flags.add_argument('--boundary',  action='store_true', default=False, required=False,
                help=f'{C.cyan}full words instead of partial strings {v.default}')

        flags.add_argument('--ignore-case',  action='store_true', default=False, required=False,
                help=f'{C.cyan}case insensitive {v.default}')

        flags.add_argument('--normalize-text',  action='store_true', default=False, required=False,
                help=f'{C.cyan}normalize text {v.default}')

        flags.add_argument('--context-length',  type=int, default=0, metavar='', required=False,
                help=f'{C.cyan}text-len of extra Text before and after the searched string {v.default}')

        # wd_required = True if '--near' in sys.argv else False
        flags.add_argument('--max-words-between',  type=int, metavar='', default=None, required=False,
                help=f'{C.cyan}max distance between words 0=adiacent {v.default}')


        flags.add_argument('--any-order',     action='store_true', default=False, help=f'{C.cyan}any order of words (otherwise is sequentiaal){v.default}')
        flags.add_argument('--show-source-text', action='store_true', default=False, help=f'{C.cyan}print text used as source text {v.default}')

        action = my_parser.add_argument_group(f'{C.white}action group (mandatory) {C.reset}')
        action_group = action.add_mutually_exclusive_group(required=True)
        action_group.add_argument('--extract',  action='store_true', default=False, help=f'{C.cyan}extract ebook into "author_name/export" directory {v.default}')
        action_group.add_argument('--terms',  type=str, nargs='*', metavar='', default=[], required=False,
                help=f'{C.cyan}terms to search for {v.default}')

    def operatorsFlags(my_parser):
        if  '--terms' in sys.argv:
            operation = my_parser.add_argument_group(f'{C.white}Operation group (mandatory) {C.reset}')
            operators_group = operation.add_mutually_exclusive_group(required=True)
            operators_group.add_argument('--and',     dest="and_arg", action='store_true',  default=False, help=f'{C.cyan}and between words {v.default}')
            operators_group.add_argument('--or',      dest="or_arg", action='store_true',  default=False, help=f'{C.cyan}or several words {v.default}')
            operators_group.add_argument('--single',  action='store_true', default=False, help=f'{C.cyan}search for a single word/string {v.default}')

    # -----------------------------
    if len(sys.argv) == 1:
        sys.argv.append('-h')


    parser = argparse.ArgumentParser(description='eBooks Manager')
    operatorsFlags(parser)
    searchingFlags(parser)
    common_options(parser)

    # parser.add_argument('--display-args',    action='store_true', default=False, help=f'{C.cyan}display results{C.reset}')
    args = parser.parse_args()

    if args.display_args:
        import json
        json_data = json.dumps(vars(args), indent=4, sort_keys=True)
        print(json_data)
        # print(f'input arguments: {json_data}'.format(**locals()))
        sys.exit(0)


    return  args




# def common_options(subp):
#     logger_levels: list[str]=logger.get_log_levels()

#     ### --- mi serve per avere la entry negli args e creare poi la entry "product"
#     # subp.add_argument('--{0}'.format(name), action='store_true', default=True)

#     execution_flags = subp.add_argument_group(f'{C.white}Execution flags{C.reset}')
#     execution_flags.add_argument('--go',            action='store_true', help=f'{C.green}specify if command must be executed. {l.default}')
#     execution_flags.add_argument('--display-args',  action='store_true', help=f'{C.green}Display arguments {l.default}')
#     execution_flags.add_argument('--vars-project',  action='store_true', help=f'{C.green}Display project variables {l.default}')
#     execution_flags.add_argument('--editor',        action='store_true', help=f'{C.green}display generated files on editor. {l.default}')
#     execution_flags.add_argument('--test',          action='store_true', help=f'{C.green}skip remote access {l.default}')


#     execution_flags.add_argument( "--console-log-level",
#                             metavar='',
#                             type=str.lower,
#                             required=False,
#                             default='notify',
#                             help=f"""{C.green}set console logger level:
#                                     {logger_levels}{C.reset}
#                                     \n\n""".replace('  ', '')
#                         )





# def searchingFlags(my_parser):
#     flags = my_parser.add_argument_group(f'{C.white}Searching flags{C.reset}')
#     # flags_group = operation.add_mutually_exclusive_group(required=True)
#     flags.add_argument('--boundary',  action='store_true', default=False, required=False,
#             help=f'{C.cyan}full words instead of partial strings {l.default}')

#     flags.add_argument('--ignore-case',  action='store_true', default=False, required=False,
#             help=f'{C.cyan}case insensitive {l.default}')

#     flags.add_argument('--context-length',  type=int, default=0, metavar='', required=False,
#             help=f'{C.cyan}text-len of extra Text before and after the searched string {l.default}')

#     wd_required = True if '--near' in sys.argv else False
#     flags.add_argument('--words-dist',  type=int, nargs=2, metavar='', default=[], required=wd_required,
#             help=f'{C.cyan}(MIN MAX) distance between words {l.default_color}(dafault no-limits){C.reset}')



# def operatorsFlags(my_parser):
#     operation = my_parser.add_argument_group(f'{C.white}Operators Group (mandatory) {C.reset}')
#     operators_group = operation.add_mutually_exclusive_group(required=True)
#     operators_group.add_argument('--and',    action='store_true', default=False, help=f'{C.cyan}and between words{C.reset}')
#     operators_group.add_argument('--or',     action='store_true', default=False, help=f'{C.cyan}or several words{C.reset}')
#     operators_group.add_argument('--near',   action='store_true', default=False, help=f'{C.cyan}match string{C.reset}')
#     operators_group.add_argument('--string', action='store_true', default=False, help=f'{C.cyan}match string{C.reset}')





# def argsPostProcess(my_args):
#     # Converti i nomi degli attributi in uppercase
#     attrs = vars(my_args)

#     ### -- convertire tutti gli attibuti in uppercase
#     # ns1 = {k.upper(): v for k, v in attrs.items()}

#     ### -- convertire alcuni attibuti in uppercase
#     new_attrs = {}
#     for k, v in attrs.items():
#         if k in ["and", "or",  "near", "string"]:
#             new_attrs[k.upper()] = v
#         else:
#             new_attrs[k] = v

#     args = argparse.Namespace(**new_attrs)
#     return args




# ##############################################################
# # - Parse Input
# ##############################################################
# def parseInput():
#     global  _default, l
#     l=SimpleNamespace()
#     # gv=gVars
#     # logger=gv.logger
#     # Color=gv.color
#     # version=gv.version
#     l.default_color = C.yellow

#     l.default = f'{l.default_color}(default: %(default)s){C.reset}\n\n'
#     l.metavar_optional=f'{C.white}<optional>{C.reset}'
#     l.metavar_mandatory=f'{C.white}<mandatory>{C.reset}'

#     # -----------------------------
#     if len(sys.argv) == 1:
#         sys.argv.append('-h')

#     parser = argparse.ArgumentParser(description='ebooks management')
#     parser.add_argument('--version', action='version', version=ctx.version)



#     input_args = parser.add_argument_group(f'{C.white}Input arguments{C.reset}')
#     input_args.add_argument('--author', required=False, default=[], nargs='*',
#                 metavar='',
#                 help=f"""{C.cyan}author(s) name.
#                             E' anche possibile indicare una o più stringhe separate da BLANK
#                             Es: --author author01 author02 ... "author 03"  {l.default}""")

#     input_args.add_argument('--words',  nargs="*", metavar=l.metavar_mandatory, default=[], required=True,
#             help=f'{C.cyan}strings to be searched BLANK separated or doubleQoute if "str1 str2"{C.reset}')

#     operatorsFlags(parser)
#     searchingFlags(parser)

#     # - common options
#     common_options(parser)


#     ### --- get input
#     args = parser.parse_args()


#     ### --- process input args
#     args = argsPostProcess(args)

#     if args.display_args:
#         import json
#         json_data = json.dumps(vars(args), indent=4, sort_keys=True)
#         print(f'input arguments: {json_data}'.format(**locals()))
#         sys.exit(0)


#     return  args
