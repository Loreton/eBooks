# #############################################
#
# updated by ...: Loreto Notarantonio
# Version ......: 14-04-2020 10.05.00
#
# #############################################

import sys
import argparse

##############################################################
# - Parse Input
##############################################################
def parseInput():

    # =============================================
    # = Parsing
    # =============================================
    if len(sys.argv) == 1:
        sys.argv.append('-h')

    parser = argparse.ArgumentParser(description='Main parser')

    subparsers = parser.add_subparsers(title="actions")
    parser_search = subparsers.add_parser ("search", help = "search books")
    parser_search.add_argument('--fieldname', help='specify field where text must be searched', required=True, default=None)
    parser_search.add_argument('--pattern', help='specify text to be searched (regex syntax)', required=True, default=None)

    parser_load = subparsers.add_parser ("load", help = "create the orbix environment")
    parser_load.add_argument('--extension', help='specify extension to be searched', required=False, default='.epub')
    parser_load.add_argument('--dir', help='Directory containing ebooks to be loaded', required=False, default=None)
    parser_load.add_argument('--move-file', help='move file to destination as in config file', action='store_true')

    # -- add common options to all subparsers
    for name, subp in subparsers.choices.items():
        # print(name)
        # print(subp)

        # --- mi serve per avere la entry negli args
        subp.add_argument('--{0}'.format(name), action='store_true', default=True)

        # --- common
        subp.add_argument('--go', help='specify if command must be executed. (dry-run is default)', action='store_true')
        subp.add_argument('--display-args', help='Display input paramenters', action='store_true')
        subp.add_argument('--debug', help='display paths and input args', action='store_true')
        subp.add_argument('--verbose', help='Display all messages', action='store_true')
        subp.add_argument('--log-console', help='log write to console too.', action='store_true')
        subp.add_argument('--log-modules',
                                    metavar='',
                                    required=False,
                                    default=['*'],
                                    nargs='*',
                                    help="""attivazione log.
        E' anche possibile indicare una o più stringhe separate da BLANK
        per identificare le funzioni che si vogliono filtrare nel log.
        Possono essere anche porzioni di funcName. Es: --log-module pippo pluto ciao
        """)

    # args = vars(parser.parse_args())
    args = parser.parse_args()
    # print (args); sys.exit()


    if args.display_args:
        import json
        json_data = json.dumps(vars(args), indent=4, sort_keys=True)
        print('input arguments: {json_data}'.format(**locals()))
        sys.exit(0)


    return  args
