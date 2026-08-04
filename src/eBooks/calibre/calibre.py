#!/usr/bin/env python

from pathlib import Path
from pyLnLib.calibre import CalibreMetadataReader


def open

# ============================================================
# UTILIZZO
# ============================================================

def get_duplicated_books(calibre_path: str, fields: list[str]) -> None:

    print("=" * 70)
    print("📚 LETTURA METADATI DA CALIBRE")
    print("=" * 70)

    try:
        reader = CalibreMetadataReader(calibre_path)
    except FileNotFoundError as e:
        print(f"❌ Errore: {e}")
        return

    # Ottieni i libri con i campi che ti servono
    if not fields:
        fields = ['id', 'title', 'authors', 'path', '#Status', '#ReadDate']
    books = reader.get_books(fields=fields)
    print(f"\n📚 Trovati {len(books)} libri\n")

    # Mostra i primi 3
    for i, book in enumerate(books[:3], 1):
        print(f"📖 Libro {i}: {book.get('title', 'NO title')}")
        print(f"   Autori: {book.get('authors', 'N/D')}")
        print(f"   Editore: {book.get('publisher', 'N/D')}")
        print(f"   status: {book.get('#Status', 'N/D')}")
        print(f"   path: {book.get('path', 'N/D')}")

        # Mostra i campi personalizzati
        for field in reader.get_custom_fields():
            if book.get(field):
                print(f"   {field}: {book.get(field)}")
        print()


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
