# #############################################
#
# updated by ...: Loreto Notarantonio
# Version ......: 03-05-2020 08.45.44
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

    parser_search = subparsers.add_parser ("search", help = "search on several fields")
    parser_search.add_argument('--book-id', help='Book_ID to search only on it', required=False, default=None)
    parser_search.add_argument('--text-size', help='size of the found text to be displayed.', required=False, default=150, type=int)
    parser_search.add_argument('--words',
                                metavar='',
                                required=True,
                                default=[],
                                nargs='*',
                                help="""strings to be searched. BLANK searator""")
    parser_search.add_argument('--field',
                                metavar='',
                                required=False,
                                default='content',
                                choices=['author', 'title', 'content', 'tags'],
                                # nargs='*',
                                help="""field to be searched. BLANK searator [DEFAULT: content] """)

    parser_load = subparsers.add_parser ("load", help = "Load book in DB")
    parser_load.add_argument('--dir', help='input dir [DEFAULT=as defined in config_file]', default=None)
    parser_load.add_argument('--ftype', help='file type to be included [DEFAULT=.epub]', default='*.epub')
    parser_load.add_argument('--indexing', help='update dictionary with words', action='store_true')
    parser_load.add_argument('--move-file', help='move file to destination defined in config file', action='store_true')
    parser_load.add_argument('--max-books', help='max number of books to be loaded', required=False, type=int, default=99999999)

    parser_build = subparsers.add_parser ("build", help = "rebuild dictionary")
    parser_build.add_argument('--force-indexing', help='update all records regardless indexed=true', action='store_true')
    parser_build.add_argument('--fields',
                                metavar='',
                                required=False,
                                default=['content'],
                                choices=['author', 'title', 'content'],
                                nargs='+',
                                help="""fields to be indexed. BLANK searator""")

    parser_update_field = subparsers.add_parser ("update_field", help = "update specific field")
    parser_test_field = subparsers.add_parser ("change_id", help = "change id")

    # -- add common options to all subparsers
    for name, subp in subparsers.choices.items():
        # print(name)
        # print(subp)

        # --- mi serve per avere la entry negli args
        subp.add_argument('--{0}'.format(name), action='store_true', default=True)

        # --- common
        # subp.add_argument('--go', help='specify if command must be executed. (dry-run is default)', action='store_true')
        subp.add_argument('--db-name', help='dbane name. [DEFAULT=as defined in config_file]', default=None)
        subp.add_argument('--go', help='load data. default is --dry-run', action='store_true')

        subp.add_argument('--display-args', help='Display input paramenters', action='store_true')
        subp.add_argument('--debug', help='display paths and input args', action='store_true')
        subp.add_argument('--verbose', help='Display all messages', action='store_true')
        subp.add_argument('--log', help='activate log.', action='store_true')
        subp.add_argument('--log-console', help='activate log and write to console too.', action='store_true')
        subp.add_argument('--log-modules',
                                    metavar='',
                                    required=False,
                                    default=[],
                                    nargs='*',
                                    help="""activate log.
        E' anche possibile indicare una o più stringhe separate da BLANK
        per identificare le funzioni che si vogliono filtrare nel log.
        Possono essere anche porzioni di funcName. Es: --log-module nudule1 modul module3
        """)

    # args = vars(parser.parse_args())
    args = parser.parse_args()
    # print (args); sys.exit()

    # - creiamo una entri 'action' con il nome del subparser scelto
    for name, subp in subparsers.choices.items():
        if name in args:
            args.action = name

    if args.log_console or args.log_modules:
        args.log=True

    if args.display_args:
        import json
        json_data = json.dumps(vars(args), indent=4, sort_keys=True)
        print('input arguments: {json_data}'.format(**locals()))
        sys.exit(0)


    return  args
