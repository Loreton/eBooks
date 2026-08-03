#!/usr/bin/env python

from pathlib import Path
from pyLnLib.calibre import CalibreMetadataReader

# ============================================================
# UTILIZZO
# ============================================================

def test01_main(calibre_path: str ) -> None:

    print("=" * 70)
    print("📚 LETTURA METADATI DA CALIBRE")
    print("=" * 70)

    try:
        reader = CalibreMetadataReader(calibre_path)
    except FileNotFoundError as e:
        print(f"❌ Errore: {e}")
        return

    # Mostra campi disponibili
    print("\n📋 Campi disponibili:")
    print("\n   Campi standard:")
    for field in sorted(reader.field_queries.keys()):
        print(f"     - {field}")

    print("\n   Campi personalizzati:")
    for field in sorted(reader.get_custom_fields()):
        print(f"     - {field}")

    # ===== 1. Tutti i libri =====
    print("\n" + "=" * 70)
    print("1️⃣  Tutti i libri:")
    print("=" * 70)

    # Scegli i campi che ti interessano
    campi_principali = [
        'id',
        'title',
        'authors',
        'publisher',
        'isbn',
        'pubdate',
        'series',
        'tags',
        '#Status',
        '#ReadDate',
        '#Comments',
        '#Tipologia'
    ]

    books = reader.get_books(campi_principali)
    print(f"\n📚 Trovati {len(books)} libri\n")

    # Mostra i primi 3
    for i, book in enumerate(books[:3], 1):
        print(f"📖 Libro {i}: {book.get('title', 'Senza titolo')}")
        print(f"   Autori: {book.get('authors', 'N/D')}")
        print(f"   Editore: {book.get('publisher', 'N/D')}")
        print(f"   ISBN: {book.get('isbn', 'N/D')}")

        # Mostra i campi personalizzati
        for field in reader.get_custom_fields():
            if book.get(field):
                print(f"   {field}: {book.get(field)}")
        print()

    # ===== 2. Dettaglio libro specifico =====
    print("=" * 70)
    print("2️⃣  Dettaglio libro (ID 1):")
    print("=" * 70)

    book = reader.get_book_by_id(1)
    if book:
        for key, value in book.items():
            if value:
                print(f"   {key}: {value}")
    else:
        print("   ❌ Libro non trovato")

    # ===== 3. Esporta in JSON =====
    print("\n" + "=" * 70)
    print("3️⃣  Esportazione in JSON:")
    print("=" * 70)

    export_file = Path("metadati_export.json")

    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, (bytes, bytearray)):
            return obj.decode('utf-8', errors='ignore')
        raise TypeError(f"Type {type(obj)} not serializable")

    try:
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(books, f, indent=2, ensure_ascii=False, default=json_serializer)
        print(f"   ✅ Dati esportati in: {export_file}")
        print(f"   📏 Dimensione: {export_file.stat().st_size / 1024:.1f} KB")
    except Exception as e:
        print(f"   ❌ Errore nell'esportazione: {e}")

    # ===== 4. Percorsi file =====
    print("\n" + "=" * 70)
    print("4️⃣  Percorsi file (primi 2 libri):")
    print("=" * 70)

    for book in books[:2]:
        file_path = reader.get_book_file_path(book)
        if file_path:
            print(f"   📁 {book.get('title')}:")
            print(f"      {file_path}")
        else:
            print(f"   ⚠️  {book.get('title')}: Nessun file trovato")

    print("\n" + "=" * 70)
    print("✅ Completato!")
    print("=" * 70)


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
