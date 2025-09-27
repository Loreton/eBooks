#!/usr/bin/env python33.5
#
# updated by ...: Loreto Notarantonio
# Version ......: 09-06-2020 17.45.11
#
# -----------------------------------------------

import sys
import argparse
# from types import SimpleNamespace


def common_options(my_parser):

    # -- add common options to my_parser
    help_color='white'


    # --- common
    my_parser.add_argument('--go', action='store_true', help=f'{Color.green}load data. default is --dry-run{Color.reset}')
    my_parser.add_argument('--display-args', action='store_true', help=f'{Color.green}Display input paramenters{Color.reset}')



# Funzione per convertire gli attributi stringa in uppercase
def namespace_to_uppercase(ns):
    attrs = vars(ns)
    new_attrs = {}
    for key, value in attrs.items():
        if isinstance(value, str) and value is not None:
            new_attrs[key] = value.upper()
        elif isinstance(value, list):
            # Converte solo le stringhe all'interno della lista in uppercase
            new_attrs[key] = [v.upper() if isinstance(v, str) else v for v in value]
        else:
            new_attrs[key] = value
    return SimpleNamespace(**new_attrs)


##############################################################
# - Parse Input
##############################################################
def parseInput(color=None):
    global Color
    Color=color
    # =============================================
    # = Parsing
    # =============================================
    # if len(sys.argv) == 1:
    #     sys.argv.append('list')

    parser = argparse.ArgumentParser(description='Main parser')

    operation_group = parser.add_mutually_exclusive_group(required=True)
    operation_group.add_argument('--and',    action='store_true', default=False, help=f'{Color.cyanH}and between words{Color.reset}')
    operation_group.add_argument('--or',     action='store_true', default=False, help=f'{Color.cyanH}or several words{Color.reset}')
    # operation_group.add_argument('--word',   action='store_true', default=False, help=f'{Color.cyanH}match word{Color.reset}')
    # operation_group.add_argument('--string', action='store_true', default=False, help=f'{Color.cyanH}match string{Color.reset}')
    operation_group.add_argument('--near',   action='store_true', default=False, help=f'{Color.cyanH}match string{Color.reset}')

    parser.add_argument('--boundary',  action='store_true', default=False, required=False,
            help=f'{Color.cyanH}word intere oppure partial strings{Color.reset}')

    parser.add_argument('--ignore-case',  action='store_true', default=False, required=False,
            help=f'{Color.cyanH}case insensitive{Color.reset}')

    parser.add_argument('--context-length',  type=int, default=0, required=False,
            help=f'{Color.cyanH}lunghezza testo prima e dopo la stringa{Color.reset}')

    parser.add_argument('--words',  nargs="*", metavar='', default=[], required=True,
            help=f'{Color.cyanH}words BLANK separated{Color.reset}')

    wd_required = True if '--near' in sys.argv else False
    parser.add_argument('--words-dist',  type=int, nargs=2, metavar='', default=[], required=wd_required,
            help=f'{Color.cyanH}(MIN MAX) distance between words{Color.reset}')

    # - common options
    common_options(parser)


    args = parser.parse_args()

    # ns_upper = namespace_to_uppercase(args)

    # Converti i nomi degli attributi in uppercase
    attrs = vars(args)


    ### -- convertire tutti gli attibuti in uppercase
    # ns1 = {k.upper(): v for k, v in attrs.items()}
    new_attrs = {}
    for k, v in attrs.items():
        if k in ["and", "or", "word", "string", "near", ""]:
            new_attrs[k.upper()] = v
        else:
            new_attrs[k] = v

    args = argparse.Namespace(**new_attrs)


    if args.display_args:
        import json
        json_data = json.dumps(vars(args), indent=4, sort_keys=True)
        print('input arguments: {json_data}'.format(**locals()))
        sys.exit(0)


    return  args

