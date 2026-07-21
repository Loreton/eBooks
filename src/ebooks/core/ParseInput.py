#!/usr/bin/env python33
# -*- coding: utf-8 -*-
# -*- coding: iso-8859-1 -*-

# updated by ...: Loreto Notarantonio
# Date .........: 30-09-2025 18.02.44

import sys
import os
from pathlib import Path
from types import SimpleNamespace
import argparse



# -----------------------------
def check_dir(path):
    p = Path(path)
    if (p).is_dir():
        return str(p.resolve())
    else:
        print(f"""\n    Input arg ERROR:  {p} doesn't exists. """)
        sys.exit(1)


def check_tmp_dir(path):
    p = Path(path)
    p.mkdir(parents=False, exist_ok=True) ### non dare errore se esiste....
    ### - verifica
    return check_dir(path)
# -----------------------------

def common_options(subp):
    # -- add common options to all subparsers
    help_color='white'
    # logger_levels=['trace', 'debug', 'notify', 'info', 'function', "caller", 'warning', 'error', 'critical']
    logger_levels=gv.logLevels

    ### --- mi serve per avere la entry negli args e creare poi la entry "product"
    # subp.add_argument('--{0}'.format(name), action='store_true', default=True)

    execution_flags = subp.add_argument_group(f'{Color.white}Execution flags{Color.reset}')
    execution_flags.add_argument('--go',            action='store_true', help=f'{Color.green}specify if command must be executed. {l.default}')
    execution_flags.add_argument('--display-args',  action='store_true', help=f'{Color.green}Display arguments {l.default}')
    execution_flags.add_argument('--editor',        action='store_true', help=f'{Color.green}display generated files on editor. {l.default}')
    execution_flags.add_argument('--test',          action='store_true', help=f'{Color.green}skip remote access {l.default}')


    execution_flags.add_argument( "--console-log-level",
                            # metavar=f'{Color.yellowH}<optional>{Color.reset}',
                            metavar='',
                            type=str.lower,
                            required=False,
                            default='notify',
                            # choices=logger_levels,
                            # nargs="?", # just one entry
                            help=f"""{Color.green}set console logger level:
                                    {logger_levels}{Color.reset}
                                    \n\n""".replace('  ', '')
                        )





def searchingFlags(my_parser):
    flags = my_parser.add_argument_group(f'{Color.white}Searching flags{Color.reset}')
    # flags_group = operation.add_mutually_exclusive_group(required=True)
    flags.add_argument('--boundary',  action='store_true', default=False, required=False,
            help=f'{Color.cyan}full words instead of partial strings {l.default}')

    flags.add_argument('--ignore-case',  action='store_true', default=False, required=False,
            help=f'{Color.cyan}case insensitive {l.default}')

    flags.add_argument('--context-length',  type=int, default=0, metavar='', required=False,
            help=f'{Color.cyan}text-len of extra Text before and after the searched string {l.default}')

    wd_required = True if '--near' in sys.argv else False
    flags.add_argument('--words-dist',  type=int, nargs=2, metavar='', default=[], required=wd_required,
            help=f'{Color.cyan}(MIN MAX) distance between words {l.default_color}(dafault no-limits){Color.reset}')



def operatorsFlags(my_parser):
    operation = my_parser.add_argument_group(f'{Color.white}Operators Group (mandatory) {Color.reset}')
    operators_group = operation.add_mutually_exclusive_group(required=True)
    operators_group.add_argument('--and',    action='store_true', default=False, help=f'{Color.cyan}and between words{Color.reset}')
    operators_group.add_argument('--or',     action='store_true', default=False, help=f'{Color.cyan}or several words{Color.reset}')
    operators_group.add_argument('--near',   action='store_true', default=False, help=f'{Color.cyan}match string{Color.reset}')
    operators_group.add_argument('--string', action='store_true', default=False, help=f'{Color.cyan}match string{Color.reset}')





def argsPostProcess(my_args):
    # Converti i nomi degli attributi in uppercase
    attrs = vars(my_args)

    ### -- convertire tutti gli attibuti in uppercase
    # ns1 = {k.upper(): v for k, v in attrs.items()}

    ### -- convertire alcuni attibuti in uppercase
    new_attrs = {}
    for k, v in attrs.items():
        if k in ["and", "or",  "near", "string"]:
            new_attrs[k.upper()] = v
        else:
            new_attrs[k] = v

    args = argparse.Namespace(**new_attrs)
    return args




##############################################################
# - Parse Input
##############################################################
def ParseInput(gVars: (SimpleNamespace, dict)):
    global gv, Color, _default, l
    l=SimpleNamespace()
    gv=gVars
    logger=gv.logger
    Color=gv.color
    version=gv.version
    l.default_color = Color.yellow

    l.default = f'{l.default_color}(default: %(default)s){Color.reset}\n\n'
    l.metavar_optional=f'{Color.gray}<optional>{Color.reset}'
    l.metavar_mandatory=f'{Color.gray}<mandatory>{Color.reset}'

    # -----------------------------
    if len(sys.argv) == 1:
        sys.argv.append('-h')

    parser = argparse.ArgumentParser(description='ebooks management')
    parser.add_argument('--version', action='version', version=version)



    input_args = parser.add_argument_group(f'{Color.white}Input arguments{Color.reset}')

    input_args.add_argument('--dir-name',  required=False, metavar='', default='/home/loreto/ln-eBooks/lnLibraries', type=check_dir,
                help=f'{Color.cyan}specify root directory {l.default}')

    input_args.add_argument('--out-dir',  required=False, metavar='', default='/tmp/ebooks', type=check_tmp_dir,
                help=f'{Color.cyan}specify output directory to save ebooks converted to txt {l.default}')

    input_args.add_argument('--author', required=False, default=[], nargs='*',
                metavar='',
                help=f"""{Color.cyan}author(s) name.
                            E' anche possibile indicare una o più stringhe separate da BLANK
                            Es: --author author01 author02 ... "author 03"  {l.default}""")

    input_args.add_argument('--words',  nargs="*", metavar=l.metavar_mandatory, default=[], required=True,
            help=f'{Color.cyan}strings to be searched BLANK separated or doubleQoute if "str1 str2"{Color.reset}')

    operatorsFlags(parser)
    searchingFlags(parser)

    # - common options
    common_options(parser)


    ### --- get input
    args = parser.parse_args()


    ### --- process input args
    args = argsPostProcess(args)

    if args.display_args:
        import json
        json_data = json.dumps(vars(args), indent=4, sort_keys=True)
        print('input arguments: {json_data}'.format(**locals()))
        sys.exit(0)


    return  args



