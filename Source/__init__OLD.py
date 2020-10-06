# updated by ...: Loreto Notarantonio
# Version ......: 13-05-2020 08.42.42

from . Main.ReadConfigurationFile import readConfigFile
from . Main.ParseInput import parseInput
from . Main.ListFiles import ListFiles


from . LnLib.LnLogger import setLogger
from . LnLib.LnColor  import LnColor as Color


from . LnLib.LnYamlLoader import LoadYamlFile
from . LnLib.LnYamlLoader import processYamlData
from . LnLib.LnPrompt import set_prompt                 ; set_prompt(Color)
from . LnLib.LnPrompt import prompt
from . LnLib import LnRegex as RegEx
from . LnLib import LnMonkeyFunctions # per Path.LnCopy, Path.LnBackup

# from . LnUtils import TreeList
# from . LnUtils import readTextFile
# from . LnUtils import filesizeFmt

import sys
from pathlib import Path

class LnClass():
    pass
    def __str__(self):
        _str_ = []
        for key,val in self.__dict__.items():
            _str_.append('{:<15}: {}'.format(key, val))

        return '\n'.join(_str_)
# -------------------------
# - Load path with custom modules in modo
# - da poter richiamare facilmente i moduli
_my_path=[]
def set_path():
    _this_path = str(Path(sys.argv[0]).resolve().parent)
    _my_path.append(_this_path + '/Source/Main')
    _my_path.append(_this_path + '/Source/Mongo')
    _my_path.append(_this_path + '/Source/LnLib')
    for path in _my_path:
        sys.path.insert(0, path)

if not _my_path: set_path()
# -------------------------