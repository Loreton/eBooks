#! /usr/bin/env python3
# updated by ...: Loreto Notarantonio
# Date .........: 05-02-2025 15.18.15

import sys; sys.dont_write_bytecode=True
import os


import tika # pip install tika
tika.initVM() # ha bisogno di java... https://stackoverflow.com/questions/51514246/use-tika-with-python-runtimeerror-unable-to-start-tika-server
from tika import parser

from pathlib import Path





TAB2=' '*2
TAB4=' '*4
TAB6=' '*6


import argparse

#
##############################################################
# - Parse Input
##############################################################
def ParseInput():
    def check_dir(path):
        p = Path(path)
        if p.is_dir():
            return str(p.resolve())
        else:
            print('    [Ln] - Input arg ERROR: dir: {p} is not valid.'.format(**locals()))
            sys.exit(1)

    # =============================================
    # = Parsing
    # =============================================
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    # required='openwrt' in sys.argv or 'dnsmasq' in sys.argv,

    parser = argparse.ArgumentParser(description='ebooks management')

    parser.add_argument('--extension', required=False, metavar='', default='.epub',
                help='specify extension to be searched (default: %(default)s)')

    parser.add_argument('--dir-name',  required=False, metavar='', default='.', type=check_dir,
                help='specify root directory (default: %(default)s)')

    parser.add_argument('--out-dir',  required=False, metavar='', default=None, type=check_dir,
                help='specify root directory (default: %(default)s)')

    parser.add_argument('--author', required=False, metavar='', default=["*"], nargs='*',
                help="""author(s) name.
    E' anche possibile indicare una o più stringhe separate da BLANK
    Es: --author author01 author02 ... "author 03"  (default: %(default)s)""")

    parser.add_argument('--search', required=True, metavar='', default=[], nargs='*',
                help="""search string.
    E' anche possibile indicare una o più stringhe separate da BLANK
    Es: --search string01 "string 02" ... "string n" (default: %(default)s)""")

    parser.add_argument('--go',      action='store_true',
                help='specify if command must be executed.  (default: %(default)s)')
    parser.add_argument('--verbose', action='store_true',
                help='Display all messages (default: %(default)s)')



        # logging and debug options
    parser.add_argument('--display-args', help='Display input paramenters', action='store_true')


    # args = vars(parser.parse_args())
    args = parser.parse_args()
    # print (args); sys.exit()
    if not args.out_dir:
        # args.out_dir=Path(args.dir_name).resolve().parent / "tmp"
        args.out_dir=str(Path(args.dir_name).resolve() / "tmp")

    if args.display_args:
        import json
        json_data = json.dumps(vars(args), indent=4, sort_keys=True)
        print('input arguments: {json_data}'.format(**locals()))
        sys.exit(0)


    return  args


# ==============================================
# - funzione utile per usarla nei display....
# - ref https://tldp.org/HOWTO/Bash-Prompt-HOWTO/x329.html
# ==============================================
def getColors():
    from types import SimpleNamespace
    colors=SimpleNamespace(
        red        = '\033[0;31m',
        redH       = '\033[1;31m',
        green      = '\033[0;32m',
        greenH     = '\033[1;32m',
        yellow     = '\033[0;33m',
        yellowH    = '\033[1;33m',
        blue       = '\033[0;34m',
        blueH      = '\033[1;34m',
        purple     = '\033[0;35m',
        purpleH    = '\033[1;35m',
        cyan       = '\033[0;36m',
        cyanH      = '\033[1;36m',
        gray       = '\033[0;37m',
        white      = '\033[1;37m',
        reset      = '\033[0m',
    )
    return colors


# ######################################################
# # original example
# ######################################################
def orig_example():
    fileIn = "berk011veel01_01.epub"
    fileIn = "/media/loreto/LnDisk_SD_ext4/Filu/ln-eBooks/New_books/2025-01/01 - Un matrimonio di convenienza - Felicia Kingsley.epub"
    fileOut = "Felicia Kingsley.txt"

    parsed = parser.from_file(fileIn, service='text')
    content = parsed["content"]

    with open(fileOut, 'w', encoding='utf-8') as fout:
        fout.write(content)


# ######################################################
# # get directory tree
# ######################################################
def TreeList(root_path, folder=None):
    root_path=Path(root_path)
    tree_list=list(root_path.glob('**'))

    return tree_list

# ######################################################
# # get list of files recursive
# ######################################################
def fileList(root_path, folder='', pattern='*.*'):
    root_path=Path(root_path)
    root_path=root_path / folder
    file_list=list(root_path.glob(f'**/{pattern}'))

    return file_list



# ######################################################
# # se newSTR == '' andiamo in FIND only
# ######################################################
def findText(content: list= [], search_string: list=[], fVerbose: bool=False):
    # nMatches=len(search_string)
    for index, line in enumerate(content):
        found_in_line=False
        for string in search_string:
            if string in line:
                cur_line = line.replace(string, color.yellowH + string + color.reset) # inseriamo il colore
                found_in_line=True


        if found_in_line:
            if fVerbose: print (f"{TAB6}[{index+0:3}]: {content[index-1]}")
            print (f"{TAB6}[{index+1:3}]: {cur_line}")
            if fVerbose: print (f"{TAB6}[{index+2:3}]: {content[index+1]}")
            print()
    print()





###################################################
#    process current epub file
###################################################
def process_file(fileIn: str, fileOut: str, search_string: list=[], write_file: bool=False, fVerbose: bool=False):
    separator='-'*80
    try:
        parsed = parser.from_file(str(fileIn), service='text')
        content = parsed["content"]
    except AttributeError as e:
        print ("ERROR:", e)
        sys.exit(1)

    if not content:
        print(f"{color.redH}ERROR reading file: {fileIn}")
        return

    # --- calcolo se tutte le parole sono trovate
    n_matches=0
    for string in search_string:
        if string in  content:
            n_matches+=1

    if n_matches == len(search_string):
        print(f'{color.green}{TAB2}{separator}{color.reset}')
        print(f"{color.green}{TAB2}- processing.... {fileIn}{color.reset}")
        print(f'{color.green}{TAB2}{separator}{color.reset}')

        content_list = [line.strip() for line in  content.split('\n') if line.strip() != ""]

        if write_file:
            with open(fileOut, 'w', encoding='utf-8') as fout:
                fout.write('\n'.join(content_list))

        findText(content=content_list, search_string=search_string, fVerbose=fVerbose)
    else:
        if fVerbose:
            print(color.gray + f'skipping.... {fileIn}', color.reset)



###################################################
#    Ctrl-C capture
###################################################
import signal
def signal_handler(signalLevel, frame):
    ### Ctrl-c
    if int(signalLevel)==2:
        print('\n'*3)
        choice = input("       Ctrl-c was pressed. [q]quit [any-key] restart \n\n")
        if choice == 'q':
            os.kill(int(os.getpid()), signal.SIGTERM)
            os.system("clear")
            sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)


###################################################
#    M A I N
###################################################
if __name__ == '__main__':
    color=getColors()
    args = ParseInput()
    ebookRootDir=Path(args.dir_name).resolve()
    search_string=args.search
    # print(ebookRootDir)
    # print(search_string)


    # ebookRootDir='/media/loreto/LnDisk_SD_ext4/Filu/ln-eBooks/New_books'
    # outDir=ebookRootDir.parent / "tmp"

    # import pdb; pdb.set_trace() # by Loreto
    # tree=TreeList(ebookRootDir)
    # for dir_path in tree:
    #     print(dir_path)
    files=fileList(ebookRootDir, pattern=f'*{args.extension}')
    # for file in files[0:3]:
    for filepath in files:
        fileOut = f"{args.out_dir}/{filepath.stem.replace(' ', '_')}.txt"
        for name in args.author:
            if name == "*" or name.lower() in str(filepath).lower():
                process_file(fileIn=filepath, fileOut=fileOut, search_string=search_string, fVerbose=args.verbose)
