#
from pathlib import Path
# --- pyLnLib modules
# from eBooks.calibre.test01 import test01_main
from pyLnLib.git.pyproject_class import PyProjectManager
from pyLnLib.context   import ctx, lnContext
from pyLnLib.files     import get_yaml_engine
from pyLnLib.lndict    import lnDict
from pyLnLib.logger    import get_logger
from pyLnLib.system import start_signal_handler


# --- project modules
from . import parseInput

logger=get_logger()




def foo_debug():
    breakpoint()


#=================================================
# setup principali funzioni per il programma
#=================================================
def initialize_program() -> lnContext:
    start_signal_handler(True)

    # 1. initialize context
    pyproject = PyProjectManager(Path.cwd())
    appl_version = pyproject.get_version()
    ctx.initialize(project_name="eBooks", project_temp_dir=f"/tmp/ebooks-{appl_version}", version=appl_version)


    #### 3. read  project configuration file
    config_file = ctx.project_config_dir / "ebooks_config.yaml"
    yaml_engine=get_yaml_engine(search_paths=[ctx.project_config_dir], recursive=True)
    config_data: lnDict = lnDict(yaml_engine.load(str(config_file)))
    config_data.save_yaml(title="processed_config", filepath=ctx.project_log_dir / "ebooks_config.yaml")

    #### 4. insert configuration data into context
    ctx.config.update(config_data)

    #### 5. initialize calibre
    ctx.initialize_calibre(config_data.dirs.calibre_path)
    args = parseInput()
    ctx.args.update(vars(args)) # trasformiamolo in lnDict()

    #### 2. logger initializzation (dobbiamo attendere il parseInput())
    logger.initialize(name="eBooks", logging_dir=ctx.project_log_dir, console_logger_level=args.console_log_level)

    return ctx
