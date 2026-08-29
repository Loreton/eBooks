#!/usr/bin/env python3
# ebook_processor/main.py
"""
Example usage of the EbookProcessor
"""
# ruff: noqa: SIM114 Combine `if` branches using logical `or` operator help: Combine `if` branches (Ruff SIM114)

import sys; sys.dont_write_bytecode = True


# --- pyLnLib modules
from pyLnLib.context    import pVars as pv
from pyLnLib.logger    import get_logger



# --- project modules
from .input_init import initialize_program
from .process import (
                        start_calibre,
                        authors_from_authors,
                        authors_from_ebooks,
                        library_to_text,
                        extract_text,
                        OR_search,
                        AND_search,
                        update_metadata,
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
            library_to_text(reader=reader, target_path=pv.config.text_extracted_path)


    elif args.choice == 'epubs':

        if args.extract_text:
            extract_text(epubs_top_dir=pv.args.top_dir, target_path=pv.config.epubs_collection_path, replace=args.replace)

        elif args.update_metadata:
            update_metadata(epubs_top_dir=pv.args.top_dir, target_path=f"{pv.config.epubs_collection_path}/new", replace=args.replace)


    elif args.choice == 'search':
        if args.and_arg:
            if len(args.terms) < 2:
                print(f'\t{C.yellowH}--and argument require at least two terms'.format(**locals()))
                sys.exit(1)
            AND_search()
        else:
            OR_search()


if __name__ == "__main__":
    main()
