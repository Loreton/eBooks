# /home/loreto/filu/Programming/gitREPO/eBooks/src/eBooks/parse_input/common_options.py

from types import SimpleNamespace

from pyLnLib.colors import get_colors
from pyLnLib.logger import get_logger

C=get_colors()
logger=get_logger()


# -- add common options to specific parser
def common_options(v:SimpleNamespace, parser, func_name: str):
    """
        Aggiunge le opzioni comuni a un parser specifico.
    """
    logger_levels: list[str]=logger.get_log_levels()

    _extra_descr=f'{C.white}arguments description{C.reset}'
    extra_descr= None
    group=parser.add_argument_group(f'{C.white}common arguments{C.reset}', extra_descr)

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

    # if parser_name in ['no_path']:
    # group.add_argument('--force-trace',   action='store_true', help=f'{C.green}force trace    level on log {v.default}')
    # group.add_argument('--force-notify',  action='store_true', help=f'{C.green}force notify   level on log {v.default}')
    group.add_argument('--go',            action='store_true', help=f'{C.green}specify if command must be executed. {v.default}')
    group.add_argument('--display-args',  action='store_true', help=f'{C.green}Display arguments {v.default}')
