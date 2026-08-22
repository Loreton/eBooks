#!/usr/bin/env python3
# ebook_processor/main.py
"""
Example usage of the EbookProcessor
"""
# ruff: noqa: SIM114 Combine `if` branches using logical `or` operator help: Combine `if` branches (Ruff SIM114)

from pathlib import Path
from tracemalloc import start


# --- pyLnLib modules
from pyLnLib.context    import ctx, pVars as pv
from pyLnLib.logger    import get_logger
# from pyLnLib.files      import scan_directory
# from pyLnLib.varie      import menu_select_from_list

# from eBooks.epubs import loadAuthors_from_books


# --- project modules
from .init.initialize_program import initialize_program
from .epubs.calibre import (
                            start_calibre,
                            authors_from_authors,
                            authors_from_ebooks,
                            epub_to_text,
                        )


logger = get_logger()

"""
    procedura per l'utilizzo di questo programma.
    Se usiamo il database di calibre per gestire le librerie:
        1. Verificare che tutti gli autori siano nel formato corretto:
            - Cognome, Nome
            - Cognome, Nome & Cognome, Nome
        2. nelle preferenze di calibre impostare:
            Salvataggio libri su disco
            flag --> Aggiorna metadati nelle copie salvate
            set --> schema di salvataggio: {author_sort}/{title} (o altro. determina come vengono salvati su disco)
        3. ...
"""


def main():
    _ctx = initialize_program()
    args=pv.args

    if args.choice == 'calibre':
        reader = start_calibre(libraries=pv.config.calibre_config.folders)
        if pv.args.authors_from_authors:
            authors_from_authors(reader=reader)
        elif pv.args.authors_from_ebooks:
            authors_from_ebooks(reader=reader)
        elif pv.args.extract_text:
            epub_to_text(reader=reader, target_path=pv.config.text_extracted_path)


        # if args.from_authors:
        #     start_calibre(libraries=pv.config.calibre_config.folders, action="from_authors")
        # elif args.from_ebooks:
        #     start_calibre(libraries=pv.config.epubs_config.folders, action="from_ebooks")


        # if args.choice == 'authors' and args.calibre:
        # _choice, library = menu_select_from_list(pv.config.calibre_config.folders)
        # loadAuthors_from_books(library_path=Path(library))
        # start_calibre(libraries=pv.config.calibre_config.folders, action="load_authors")



    if args.choice == 'duplicated':
        ...
        # logger.info(ctx.calibre.get_duplicate_report())

    elif args.choice == 'search':
        ...

    elif args.choice == 'copy_new':
        # target_top_dir=Path(pv.config.main_epubs_path) / "epubs"
        # if args.calibre:
        #     _choice, library = menu_select_from_list(pv.config.calibre_config.folders)
        #     processCalibreLibrary(library_path=Path(library), target_path=target_top_dir)
        # else: # ---> args.epubs
        #     _choice, library = menu_select_from_list(pv.config.epubs_config.folders)
        #     copy_new(epubs_path=Path(library), target_path=target_top_dir)

        # source_top_dir=Path(args.source_epubs)
        """ copia il sorgente nella directory di destinazione
            cambiando nome del file come da titolo
        """


    elif args.choice == 'extract':
        ...
        # if args.calibre:
        #     _choice, library = menu_select_from_list(pv.config.calibre_config.folders)
        #     pv.calibre = initialize_calibre(library)
        # else: # ---> args.epubs
        #     _choice, library = menu_select_from_list(pv.config.epubs_config.folders)

        # if isinstance(library, str):
        #     library=[library]
        # for source_dir in library:
        #     file_list = scan_directory(root_dir=source_dir, pattern='*.epub')
        #     nfiles=len(file_list)
        #     logger.info(file_list)

        #     for index, file in enumerate(file_list):
        #         if file.stem in pv.config.files_to_skip:
        #             logger.warning(f"Skipping {file.stem}")
        #             continue
        #         extract_text(epub_path=file, export_dir=pv.config.main_folder, index=f"{index:04}/{nfiles:04}")

    elif pv.args.choice == 'extract_from_calibre':
        ...
        # calibre_folders = pv.config.calibre
        # print(calibre_folders.to_dict())
        # breakpoint()

    # sys.exit("temporary exit")

if __name__ == "__main__":
    main()
