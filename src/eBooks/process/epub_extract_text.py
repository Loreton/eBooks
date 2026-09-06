#
# ruff: noqa: SIM113 - Use `enumerate()` for index variable `index` in `for` loop (Ruff SIM113)

import os
from pathlib import Path
import shutil
from datetime import datetime


# --- pyLnLib modules
from pyLnLib.context    import pVars as pv
from pyLnLib.logger    import get_logger
from pyLnLib.colors    import get_colors
# from pyLnLib.files import get_unique_filename
from pyLnLib.epub      import EpubManager
from pyLnLib.files      import scan_directory
# from pyLnLib.varie import keyboardPrompt, select_from_list



from .clean_filename import clean_filename
logger = get_logger()
C = get_colors()





#==========================================
# - main_folder/
# -     author/
# -         text/
# -         epubs/
#==========================================
def extract_text(epubs_top_dir: Path, target_path: Path, replace: bool = False) -> None:
    file_list = scan_directory(root_dir=epubs_top_dir, pattern='*.epub')
    nfiles=len(file_list)
    logger.debug(file_list)

    os.chdir(target_path)
    # file_list=['/home/loreto/.aMule/Copied/Verity - Hoover, Colleen.epub']
    # file_list=['/home/loreto/filu/ln-eBooks/lnExtracted/epubs/Bluebook/TREDICESIMA STORIA, lA.epub']

    for index, epub_path in enumerate(file_list, 1):
        # logger.info("working on file: %s", epub_path)
        # try:
            with EpubManager(epub_path) as book:
                print()
                logger.info(f"{C.white}{index:03d}/{nfiles:03d}: {C.cyan}{book.source_path}")
                # non aggiorniamo il registry perché sugli epub sciolti potrebbero esserci errori nei nomi autori
                author_name=pv.author_registry.format(book.author, canonical=True, registry_update=False)
                if not author_name:
                    continue

                author_name = author_name[0]
                cleaned_title = clean_filename(text=book.title)

                logger.info("\torig. author %s", book.author)
                logger.info("\tnew   author %s", author_name)
                logger.info("\torig. title  %s", book.title)
                logger.info("\tnew   title  %s", cleaned_title)


                dest_author_path = Path(target_path) / author_name
                dest_author_path.mkdir(parents=True, exist_ok=True)



                output_filename=dest_author_path / f"{cleaned_title}.txt"
                logger.info("extracting to: %s", output_filename)
                # - creiamo l'istanza EpubProcess per il file epub
                # - ed il metodo to_text() per convertire il file epub in testo
                # epub_obj = EpubManager(book.file_path)
                book.to_text(output_file=output_filename, replace=replace)
        # except Exception as e:
        #     logger.error("%s", e, show_stack=True)
        #     breakpoint()
