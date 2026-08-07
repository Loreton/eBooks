#
from pathlib import Path
# --- pyLnLib modules
# from eBooks.calibre.test01 import test01_main
from pyLnLib.git.pyproject_class import PyProjectManager
from pyLnLib.context   import ctx, lnContext
from pyLnLib.files     import get_yaml_engine
from pyLnLib.lndict    import lnDict
from pyLnLib.logger    import get_logger
from pyLnLib.colors    import get_colors
from pyLnLib.system import start_signal_handler
# from pyLnLib import keyboardPrompt
from pyLnLib.varie import menu_select_from_list


# --- project modules
from . import parseInput

logger=get_logger()
C=get_colors()



#==================================
def _read_pyproject() -> str:
    """
         read pyproject.toml filr to extract program version

         Args:
             None

         return:
             application version (str)
    """
    pyproject = PyProjectManager(Path.cwd())
    return pyproject.get_version()


#==================================
def _read_configuration() -> lnDict:
    """
         read application configuration file

         Args:
             None

         return:
             configuration (lnDict)
    """

    config_file = ctx.project_config_dir / "ebooks_config.yaml"
    yaml_engine=get_yaml_engine(search_paths=[ctx.project_config_dir], recursive=True)
    config_data: lnDict = lnDict(yaml_engine.load(str(config_file)))
    config_data.save_yaml(title="processed_config", filepath=ctx.project_log_dir / "ebooks_config.yaml")
    return config_data

#=================================================
# setup principali funzioni per il programma
#   crx.project_name        project name
#   crx.project_temp_dir    project temp dir
#   crx.project_config_dir  project config dir
#   crx.config_data         project configuration data
#   crx.args                input arguments
#   logger                  initialize logger
#=================================================
def initialize_program() -> lnContext:
    start_signal_handler(True)

    #read=============================================
    # 1. initialize context
    #================================================
    appl_version = _read_pyproject()
    ctx.initialize(project_name="eBooks", project_temp_dir=f"/tmp/ebooks-{appl_version}", version=appl_version)


    #### 2. logger initializzation
    default_console_logger_level="info"
    logger.initialize(name="eBooks", logging_dir=ctx.project_log_dir, console_logger_level=default_console_logger_level)


    #================================================
    # 3.  read  project configuration file
    # 3a. insert configuration data into context
    #================================================
    config_data=_read_configuration()
    ctx.config.update(config_data)


    #================================================
    # 2. read inout args
    #================================================
    args = parseInput()
    ctx.args.update(vars(args)) # trasformiamolo in lnDict()
    if args.console_log_level != default_console_logger_level:
        logger.setConsoleLoggerLevel(args.console_log_level)


    #================================================
    # 4. initialize calibre
    #  - legge potenziali librerie salla configurazione
    #  - li esplode in un mneu per permettere la scela
    #  - initializza calibre sulla libreria richiesta
    #================================================
    libraries: list[str] = config_data.libraries
    choice = menu_select_from_list(libraries)
    ctx.initialize_calibre(libraries[choice])
    return ctx
