
#
from pathlib import Path
# --- pyLnLib modules
# from eBooks.calibre.test01 import test01_main
from pyLnLib.logger    import get_logger
# from pyLnLib.context   import ctx
# from pyLnLib.calibre import  CalibreMetadataReader
# from pyLnLib.git.pyproject_class import PyProjectManager
# from pyLnLib.files     import get_yaml_engine
# from pyLnLib.lndict    import lnDict
# from pyLnLib.colors    import get_colors
# from pyLnLib.system import start_signal_handler
# # from pyLnLib import keyboardPrompt
# from pyLnLib.varie import menu_select_from_list
from pyLnLib.epub      import EpubProcessor
logger = get_logger()



#==========================================
# - main_folder/
# -     author/
# -         text/
# -         epubs/
#==========================================
def extract_text(epub_path: str|Path, main_folder: Path | None = None, index: str|None=None) -> None:
    book = EpubProcessor(epub_path)
    author = book.author
    index=f"{index} - "  if index is not None else ''

    logger.info("%sprocessing: %s/%s", index, book.author, book.filename.name)
    # justxtract
    if main_folder:
        if author:
            output_dir = Path(main_folder) / author / "text"
            saved_filename = book.export_text(filename=output_dir / f"{book.filename.stem}.txt", replace=False, unique=False)
            logger.debug("saved:      \"%s\"", saved_filename)
        return


    logger.info("filename:   %s", book.filename)
    logger.info("title:      %s", book.title)
    logger.info("author:     %s", book.author)
    logger.info("language:   %s", book.language)
    logger.info("identifier: %s", book.identifier)
    logger.info("sections:   %s", len(book.get_sections()))


def init_epubs():
    ...
