#!/usr/bin/env python

# from pathlib import Path
# from pyLnLib.context import ctx
from enum import unique

from pyLnLib.calibre import CalibreMetadataReader
from pyLnLib import keyboardPrompt



# ============================================================
# UTILIZZO
# ============================================================
def get_duplicated_books(reader: CalibreMetadataReader, fields: list[str]|None=None) -> None:
    f_print: bool = False

    print("=" * 70)
    print("📚 LETTURA METADATI DA CALIBRE")
    print("=" * 70)

    # Ottieni i libri con i campi che ti servono
    if not fields:
        fields = ['id', 'title', 'authors', 'path', '#Status', '#ReadDate']
    books = reader.get_books(fields=fields)
    db_path=reader.db_path
    print(f"\n\t📚 on db_path: {db_path}")
    print(f"\t📚 Trovati {len(books)} libri\n")

    # Mostra i primi 3
    unique_book = []
    duplicated_book = []
    no_path = []

    for i, book in enumerate(books, 1):
        file_path = reader.get_book_file_path(book)
        title=book.get('title', 'NO title')
        authors=book.get('authors', 'N/D').replace('|', ' ')
        if file_path is None:
            no_path.append(f"{authors} - {title}")
        if title in unique_book:
            duplicated_book.append(f"{authors} - {title}")
        else:
            unique_book.append(title)

        if f_print:
            print(f"📖 Libro {i}: {title}")
            print(f"   Autori: {authors}")
            print(f"   Editore: {book.get('publisher', 'N/D')}")
            print(f"   status: {book.get('#Status', 'N/D')}")
            print(f"   file_path: {file_path}")

            for field in reader.get_custom_fields():
                if book.get(field):
                    print(f"   {field}: {book.get(field)}")
            print()



    # print(len(unique_book))
    # for book in sorted(duplicated_book):
    #     print(book)
    print("unique_book:     ", len(unique_book))
    print("duplicated_book: ", len(duplicated_book))
    print("no_path:         ", len(no_path))
    if False:
        n_books = len(no_path)
        for index, book in enumerate(no_path):
            print(f"{index:04} of {n_books:04} - {book}")
            keyb_msg: str = '\n\t[enter] to continue '
            _choice = keyboardPrompt( text_msg=keyb_msg, validKeys=["ENTER"])


    import sys
    sys.exit("Uscita temporanea")



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
