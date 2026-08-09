#!/usr/bin/env python

# from pathlib import Path
# from pyLnLib.context import ctx

from pyLnLib.calibre import CalibreMetadataReader
from pyLnLib import keyboardPrompt
from pyLnLib import get_emoji
from pyLnLib.logger import get_logger

E=get_emoji()
logger=get_logger()

# ============================================================
# UTILIZZO
# ============================================================






if __name__ == "__main__":
    CALIBRE_PATH = "/home/loreto/filu/ln-eBooks/lnLibraries/Others"  # MODIFICA QUI
    CALIBRE_PATH = "/home/loreto/filu/ln-eBooks/lnLibraries/allInOne"  # MODIFICA QUI
    main(calibre_path=CALIBRE_PATH)



def come_usarlo():
    # Nel tuo programma principale
    from read_calibre_v3 import CalibreMetadataReaderAlt

    # Inizializza
    reader = CalibreMetadataReaderAlt("/home/loreto/filu/Library")

    # Ottieni i libri con i campi che ti servono
    campi = ['id', 'title', 'authors', 'path', '#Status', '#ReadDate']
    books = reader.get_books(campi)

    # Per ogni libro
    for book in books:
        # Trova il file
        file_path = reader.get_book_file_path(book)
        if file_path:
            # Estrai il testo (con la tua funzione)
            testo = estrai_testo(file_path)

            # Usa i metadati per arricchire l'output
            salva_con_metadati(
                testo=testo,
                titolo=book['title'],
                autore=book['authors'],
                status=book.get('#Status', ''),
                read_date=book.get('#ReadDate', '')
            )


def vedere_i_campi_disponibili():
    # Per vedere tutti i campi disponibili
    reader = CalibreMetadataReaderAlt("/home/loreto/filu/Library")
    print(reader.get_available_fields())

    # Per ottenere solo alcuni campi
    campi_ridotti = ['id', 'title', '#Status']
    books = reader.get_books(campi_ridotti)

    # Per filtrare per status
    books_letti = [b for b in books if b.get('#Status') == 'Letto']
