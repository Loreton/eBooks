# #############################################
#
# updated by ...: Loreto Notarantonio
# Version ......: 31-03-2020 10.28.38
#
# #############################################
import sys
import argparse

##############################################################
# - Parse Input
##############################################################
def ParseInput():
    # =============================================
    # = Parsing
    # =============================================
    if len(sys.argv) == 1:
        sys.argv.append('-h')

    parser = argparse.ArgumentParser(description='command line tool to sync gDrive')
    # parser.add_argument('--user-name', help='Specify gmail user_name to be used)', required=True)
    parser.add_argument('--extension', help='specify extension to be searched', required=False, default='.epub')
    parser.add_argument('--search', help='specify text to be searched', required=True, default=None)
    parser.add_argument('--go', help='specify if command must be executed. (dry-run is default)', action='store_true')
    parser.add_argument('--verbose', help='Display all messages', action='store_true')


        # logging and debug options
    parser.add_argument('--display-args', help='Display input paramenters', action='store_true')
    parser.add_argument('--debug', help='display paths and input args', action='store_true')
    parser.add_argument('--log-console', help='log write to console too.', action='store_true')
    parser.add_argument('--log-modules',
                                metavar='',
                                required=False,
                                default=['*'],
                                nargs='*',
                                help="""attivazione log.
    E' anche possibile indicare una o più stringhe
    per identificare le funzioni che si vogliono filtrare nel log.
    Possono essere anche porzioni di funcName separate da ' ' Es: --log-module pippo pluto ciao
    """)




    # args = vars(parser.parse_args())
    args = parser.parse_args()
    # print (args); sys.exit()


    if args.display_args:
        import json
        json_data = json.dumps(vars(args), indent=4, sort_keys=True)
        print('input arguments: {json_data}'.format(**locals()))
        # sys.exit(0)


    return  args

