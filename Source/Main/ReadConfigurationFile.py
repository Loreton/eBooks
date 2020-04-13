# #############################################
#
# updated by ...: Loreto Notarantonio
# Version ......: 13-04-2020 10.53.58
#
# #############################################

import  sys; sys.dont_write_bytecode = True
# import  os
# import  yaml
import  pdb
# from    collections import OrderedDict
# from    dotmap import DotMap


from    pathlib import Path
from    zipfile import ZipFile
import  io
import  yaml

def readConfigFile():
    _this_path          = Path(sys.argv[0]).resolve()
    #_this_path = Path('K:\\Filu\\LnDisk\\LnStart\\LnStartProgram_New.zip').resolve()
    script_path = _this_path.parent # ... then up one level

    if _this_path.suffix == '.zip':
        _I_AM_ZIP = True
        prj_name    = _this_path.stem # get name of zip file
        zip_filename = _this_path

    else:
        _I_AM_ZIP = False
        prj_name  = script_path.name # get name of path

    yaml_filenames = [
            '{0}.yml'.format(prj_name),
            'conf/{0}.yml'.format(prj_name),
            'config/{0}.yml'.format(prj_name),
        ]

    content = None
    if _I_AM_ZIP:
        z = ZipFile(zip_filename, "r")
        #zinfo = z.namelist()
        for name in yaml_filenames:
            if name in z.namelist():
                yaml_filename = name
                with z.open(yaml_filename) as f:
                    _data = f.read()
                _buffer = io.TextIOWrapper(io.BytesIO(_data))# def get_config(yaml_filename):
                # contents  = io.TextIOWrapper(io.BytesIO(_data), encoding='iso-8859-1', newline='\n')# def get_config(yaml_filename):
                content=[]
                for line in _buffer:
                    content.append(line)
                break

    else:
        for name in yaml_filenames:
            yaml_filename = Path(script_path / name)
            if yaml_filename.exists():
                # pdb.set_trace()
                with open(str(yaml_filename), 'r') as f:
                    content = f.readlines() # splitted in rows
                    # content = f.read() # single string
                break

    if content: # it's a LIST containing file rows...
        """ removal of all commented lines to avoid solving
        variables that could create errors"""
        rows = []
        for line in content:
            if not line.strip(): continue
            if line.strip()[0]=='#': continue
            rows.append(line)

        result = '\n'.join(rows)
        # content = yaml.safe_load(result) # non usa i constructors
        content = yaml.load(result)

    else:
        print ('configuration file {0} NOT FOUND'.format(prj_name))
        sys.exit(1)
    yaml_config_file = yaml_filename
    _ret = {}
    _ret['content'] = content
    _ret['prjname'] = prj_name
    _ret['script_path'] = str(script_path)
    _ret['yaml_config_file'] = str(yaml_config_file)
    # _ret['script_path'] = script_path
    # _ret['yaml_config_file'] = yaml_config_file

    return _ret # it's a dictionary





## define custom tag handler
def join(loader, node):
    seq = loader.construct_sequence(node)
    return ''.join([str(i) for i in seq])

def joinPath(loader, node):
    seq = loader.construct_sequence(node)
    return '/'.join([str(i) for i in seq])

def upper(loader, node):
    data = loader.construct_scalar(node)
    return data.upper()

def evaluate(loader, node):
    data = loader.construct_scalar(node)
    return eval(data)

## register the tag handler
yaml.add_constructor('!join', join)
yaml.add_constructor('!joinPath', joinPath)
yaml.add_constructor('!upper', upper)
yaml.add_constructor('!eval', evaluate)
# yaml.add_constructor('!incl', _include_variable)

