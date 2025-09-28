#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- coding: iso-8859-1 -*-

# updated by ...: Loreto Notarantonio
# Date .........: 27-09-2025 15.53.54


import sys; this=sys.modules[__name__]
import os
from pathlib import Path

from datetime import datetime
import platform
import socket
# from pathlib import Path


_my_path = []



# -------------------------
# - Load syspath with custom modules paths in modo
# - da poter richiamare facilmente i moduli con il solo nome
# - anche con il progetto zipped
# -------------------------
def set_path():
    script_name = Path(sys.argv[0]).resolve()

    if script_name.suffix == '.zip':  # sono all'interno dello zip
        _my_path.append(script_name.parent.parent)
        prj_dir = script_name  # ... nome dello zip_file
        # my_path.extend(extractZip(script_name)) # extract lnLib.zip from project.zip file and get its path
    else:
        prj_dir = script_name.parent # nome della prj directory
        _my_path.append(script_name.parent)

    _my_path.append(prj_dir)
    _my_path.append(f'{prj_dir}/Source')
    _my_path.append(f'{prj_dir}/Source/main')
    _my_path.append(f'{prj_dir}/Source/Modules')
    _my_path.append(f'{prj_dir}/Source/Process')
    _my_path.append(f'{prj_dir}/Source/lnLib')
    # _my_path.append(f'{prj_dir}/Source/LnLib.zip')

    for path in _my_path:
        # print(str(path))
        sys.path.insert(0, str(path))

if not _my_path: set_path()





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



# ----------------------------
# ----- logging
# ----------------------------
def setupLogger(prj_name: str):
    from ColoredLogger import setColoredLogger, testLogger

    project_log_levels={
        "notset":    0,
        "trace":     5,
        "debug":    10,
        "notify":   15,
        "info":     20,
        "function": 22,
        "caller":   24,
        "warning":  30,
        "error":    40,
        "critical": 50,
    }


    logger=setColoredLogger(logger_name=prj_name,
                            console_logger_level="info", ### --- default
                            file_logger_level="critical",
                            logging_dir=None, # no filehandler
                            threads=False,
                            create_logging_dir=False,
                            prj_log_levels=project_log_levels)


    testLogger(logger)

    logger.info('------- Starting -----------')
    return logger





#####################################################################
#
#####################################################################
def setMainVars(gVars: dict, search_paths: list=["conf"]):
    global gv
    gv=gVars

    # ----- project variables
    gv.color                = gv.logger.Colors
    gv.logLevels            = gv.logger.logLevels
    gv.dry_run              =  not gv.args.go
    gv.run_env              =  "prod" if gv.args.go else "dry_run"
    gv.fExecute             =  gv.args.go
    gv.search_paths: list   = search_paths


    # ----- standard variables
    gv.OpSys: str           = platform.system()
    gv.date_time: str       = datetime.now().strftime("%Y%m%d_%H%M")
    gv.YYMMDD: str          = datetime.now().strftime("%Y%m%d")
    gv.time: str            = datetime.now().strftime("%H%M%S")
    gv.HHMMSS: str          = datetime.now().strftime("%H%M%S")
    gv.HHMM: str            = datetime.now().strftime("%H%M")
    gv.date:      str       = datetime.now().strftime("%Y%m%d")
    gv.now: str             = datetime.now().strftime("%d-%m-%Y_%H:%M")
    gv.script_path          = Path(sys.argv[0]).resolve()
    gv.tmp_dir              = f"/tmp/{gv.project_name}"
    gv.hostname             = socket.gethostname().split()[0]



    # - set env variables
    os.environ['DATE_TIME'] = gv.date_time
    os.environ['DATE']      = gv.date
    os.environ['TIME']      = gv.time
    os.environ['HHMM']      = gv.HHMM
    os.environ['HOST_NAME'] = gv.hostname



    # import FileLoader;       FileLoader.setup(gVars=gv)
    # import lnUtils;          lnUtils.setup(gVars=gv)
    # import subprocessLN;     subprocessLN.setup(gVars=gv)
    # import dictUtils;        dictUtils.setup(gVars=gv)
    # # import checkDuplicates;  checkDuplicates.setup(gVars=gv)
    # import ln_Excel_Class;   ln_Excel_Class.setup(gVars=gv)
    # # import openwrtUtils;     openwrtUtils.setup(gVars=gv)
    # import processData;     processData.setup(gVars=gv)
    import functionExecutionTime;     functionExecutionTime.setup(gVars=gv)


    return gv


