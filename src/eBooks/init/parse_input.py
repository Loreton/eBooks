# updated by ...: Loreto Notarantonio
import sys
from types import SimpleNamespace
import argparse

from pyLnLib.context import ctx
from pyLnLib.colors import get_colors
from pyLnLib.logger import get_logger

C=get_colors()
logger=get_logger()


# -- add common options to specific parser
def common_options(parser, name: str):
    logger_levels: list[str]=logger.get_log_levels()

    _extra_descr=f'{C.white}arguments description{C.reset}'
    extra_descr= None
    group=parser.add_argument_group(f'{C.white}{name} common arguments{C.reset}', extra_descr)
    # input_args = parser.add_argument_group(f'{C.white}Common input arguments{C.reset}')
    # group.add_argument('--config-file',  required=False, metavar='', default='config.yaml', type=str,
                # help=f'{C.cyan}specify root directory {v.default}')

    group.add_argument('--show-log-function-name',action='store_true', help=f'{C.green}show function on log line {v.default}')
    group.add_argument( "--console-log-level",
                            # metavar=f'{C.yellowH}<optional>{C.reset}',
                            metavar='',
                            type=str.lower,
                            required=False,
                            default='info',
                            choices=logger_levels,
                            nargs="?", # just one entry
                            help=f"""{C.cyan}set logger console level:
                                    {logger_levels} {v.default} """.replace('  ', '')
                        )

    # common_flags = parser.add_argument_group(f'{C.white}execution flags{C.reset}')
    # if parser_name in ['no_path']:
    # group.add_argument('--force-trace',   action='store_true', help=f'{C.green}force trace    level on log {v.default}')
    # group.add_argument('--force-notify',  action='store_true', help=f'{C.green}force notify   level on log {v.default}')
    group.add_argument('--go',            action='store_true', help=f'{C.green}specify if command must be executed. {v.default}')
    group.add_argument('--display-args',  action='store_true', help=f'{C.green}Display arguments {v.default}')




# ==================
# define group for excel
# ==================
def duplicated(parser, name: str):
    excel_parser   = parser.add_parser(name=name, help=f"{C.cyan}visualizza tutti i libri che sono duplicati{C.reset}")
    _extra_descr=f'{C.white}arguments description{C.reset}'
    extra_descr= None
    group=excel_parser.add_argument_group(f'{C.white}{name} group {C.reset}', extra_descr)

    # define exclusive_group for excel
    exclusive_group=group.add_mutually_exclusive_group(required=True)
    exclusive_group.add_argument('--print', action='store_true', help=f'{C.cyan}print all files {v.default}')
    exclusive_group.add_argument('--prompt', action='store_true', help=f'{C.cyan}prompt for each file to allow delection{v.default}')
    common_options(parser=excel_parser, name=name)



# ==================
# define group for no_path
# ==================
def no_path(parser, name: str):
    no_path_parser = parser.add_parser(name=name, help=f"{C.cyan}visualizza tutti i libri che non hanno un link ad un file{C.reset}")
    group=no_path_parser.add_argument_group(f'{C.white}{name} group {C.reset}', f'{C.white}arguments description{C.reset}')
    group.add_argument('--wan', action='store_true', help=f'{C.cyan}access via WAN  {v.default}')

    # define exclusive_group for no_path
    exclusive_group=group.add_mutually_exclusive_group(required=True)
    exclusive_group.add_argument('--backup', action='store_true', help=f'{C.cyan}backup all file from no_path  {v.default}')
    exclusive_group.add_argument('--generate', action='store_true', help=f'{C.cyan}create all file from no_path  {v.default}')
    exclusive_group.add_argument('--dhcp', action='store_true', help=f'{C.cyan}export dhcp in no_path format  {v.default}')
    exclusive_group.add_argument('--firewall', action='store_true', help=f'{C.cyan}export firewall in no_path format  {v.default}')

    common_options(parser=no_path_parser, name=name)



# ==================
# define group for extract
# ==================
def extract(parser, name: str):
    this_parser = parser.add_parser(name=name, help=f"{C.cyan}extract full textfrom ebook and save them as .txt in extraction_top_dir{C.reset}")
    this_parser.add_argument('--extraction-top-dir',  required=False, metavar='', default=ctx.config.dirs.extract_dir, type=str,
                help=f'{C.cyan}specify root directory {v.default}')
    common_options(parser=this_parser, name=name)

# ==================
# define group for search menu
# ==================
def search(parser, name: str):
    my_parser = parser.add_parser(name=name, help=f"{C.cyan}search for specific string/words{C.reset}")
    # my_parser = parser.add_argument_group(f'{C.white}Searching flags{C.reset}')
    my_parser.add_argument('--terms',  type=str, nargs='*', metavar='', default=[], required=True, help=f'{C.cyan}terms to search for {v.default}')

    my_parser.add_argument('--boundary',  action='store_true', default=False, required=False,
            help=f'{C.cyan}full words instead of partial strings {v.default}')

    my_parser.add_argument('--ignore-case',  action='store_true', default=False, required=False,
            help=f'{C.cyan}case insensitive {v.default}')

    my_parser.add_argument('--normalize-text',  action='store_true', default=False, required=False,
            help=f'{C.cyan}normalize text {v.default}')

    my_parser.add_argument('--context-length',  type=int, default=0, metavar='', required=False,
            help=f'{C.cyan}text-len of extra Text before and after the searched string {v.default}')

    # wd_required = True if '--near' in sys.argv else False
    my_parser.add_argument('--max-words-between',  type=int, metavar='', default=None, required=False,
            help=f'{C.cyan}max distance between words 0=adiacent {v.default}')

    my_parser.add_argument('--and',     dest="and_arg", action='store_true',  default=False, help=f'{C.cyan}and between words (default OR){v.default}')

    common_options(parser=my_parser, name=name)





##############################################################
# - Parse Input
##############################################################
def parseInput() -> argparse.Namespace:
    global v
    v=SimpleNamespace(
        default_color=C.yellow,
        metavar_optional=f'{C.white}<optional>{C.reset}',
        metavar_mandatory=f'{C.white}<mandatory>{C.reset}',
    )
    v.default=f'{v.default_color}(default: %(default)s){C.reset}\n\n'



    # -----------------------------
    import argparse
    if len(sys.argv) == 1:
        sys.argv.append('-h')

    parser = argparse.ArgumentParser(description='devices management')
    # parser.add_argument('--version', action='version', version=version)



    # ===================================
    # - Main positional arguments
    # -    choice conterrà l'argomento posizionale
    # ===================================
    positional_arguments = ["duplicated", "no_path", "extract", "search"]
    for item in positional_arguments:
        if sys.argv[1].startswith(item[:3]):
            sys.argv[1] = item
            break

    pos_parser     = parser.add_subparsers(dest='choice',required=True, title=f'{C.white}choices - required positional arguments{C.reset}')
    duplicated(parser=pos_parser, name='duplicated')
    no_path(parser=pos_parser, name="no_path")
    extract(parser=pos_parser, name="extract")
    search(parser=pos_parser, name="search")


    # - common options for all subparsers
    # common_options(subparsers=subparsers)




    args = parser.parse_args()
    if args.display_args:
        import json
        json_data = json.dumps(vars(args), indent=4, sort_keys=True)
        print('input arguments: {json_data}'.format(**locals()))
        sys.exit(0)

    if args.show_log_function_name:
        logger.show_function_name(True)
    return  args
