# #############################################
#
# updated by ...: Loreto Notarantonio
# Version ......: 05-04-2020 12.23.29
#
# #############################################
import os

def ListFiles(baseDir, filetype):
    """
    Recursively returns files matching a filetype from
    a path (e.g. return a list of paths from a folder
    of epub files).
    """
    files = []
    for item in os.scandir(baseDir):
        if item.is_file():
            if item.path.endswith(filetype):
            # full_path = os.path.join(baseDir, item.name)
            # if spec.match_file(full_path):
                files.append(os.path.join(baseDir, item.name))
        else:
            files.extend(ListFiles(item.path, filetype))
    return files