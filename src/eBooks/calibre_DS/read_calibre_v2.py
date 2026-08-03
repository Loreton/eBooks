#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import json
from pathlib import Path
from datetime import datetime

class CalibreMetadataReader:
    """Lettore di metadati Calibre per il database specifico"""

    def __init__(self, library_path: str):
        self.library_path = Path(library_path)
        self.db_path = self.library_path / "metadata.db"

        if not self.db_path.exists():
            raise FileNotFoundError(f"Database non trovato: {self.db_path}")

        # Campi disponibili con le relative query
        self.field_queries: dict[str, str] = {
            # Campi standard (dalla tabella books)
            'id': 'b.id',
            'title': 'b.title',
            'sort': 'b.sort',
            'timestamp': 'b.timestamp',
            'pubdate': 'b.pubdate',
            'series_index': 'b.series_index',
            'author_sort': 'b.author_sort',
            'path': 'b.path',
            'uuid': 'b.uuid',
            'has_cover': 'b.has_cover',
            'last_modified': 'b.last_modified',

            # Campi collegati
            'authors': """(SELECT group_concat(a.name, ', ')
                          FROM books_authors_link bal
                          JOIN authors a ON bal.author = a.id
                          WHERE bal.book = b.id)""",

            'publisher': """(SELECT group_concat(p.name, ', ')
                           FROM books_publishers_link bpl
                           JOIN publishers p ON bpl.publisher = p.id
                           WHERE bpl.book = b.id)""",

            'isbn': """(SELECT val
                       FROM identifiers
                       WHERE book = b.id AND type = 'isbn'
                       LIMIT 1)""",

            'identifiers': """(SELECT group_concat(type || ': ' || val, ', ')
                             FROM identifiers
                             WHERE book = b.id)""",

            'tags': """(SELECT group_concat(t.name, ', ')
                       FROM books_tags_link btl
                       JOIN tags t ON btl.tag = t.id
                       WHERE btl.book = b.id)""",

            'series': """(SELECT s.name
                         FROM books_series_link bsl
                         JOIN series s ON bsl.series = s.id
                         WHERE bsl.book = b.id
                         LIMIT 1)""",

            'language': """(SELECT lang_code
                           FROM books_languages_link bll
                           WHERE bll.book = b.id
                           LIMIT 1)""",

            'rating': """(SELECT r.name
                         FROM books_ratings_link brl
                         JOIN ratings r ON brl.rating = r.id
                         WHERE brl.book = b.id
                         LIMIT 1)""",
        }

        # Mappa per i campi personalizzati
        self.custom_columns: dict[str, str] = {
            '#Narrazione': 'custom_column_1',
            '#Status': 'custom_column_2',
            '#Tipologia': 'custom_column_3',
        }

    def get_books(self, fields: list[str] | None = None) -> list[dict[str, any]]:
        """
        Recupera i libri con i campi specificati.

        Args:
            fields: Lista di campi da estrarre.
                   Se None, usa ['id', 'title', 'authors', 'publisher', 'isbn']
        """
        if fields is None:
            fields = ['id', 'title', 'authors', 'publisher', 'isbn']

        # Costruisci la SELECT
        select_parts = []
        select_parts.append("b.id AS _id")  # Sempre presente per riferimento

        for field in fields:
            if field.startswith('#'):
                # Campo personalizzato
                col_name = field.lstrip('#')
                if col_name in self.custom_columns:
                    table_name = self.custom_columns[field]
                    select_parts.append(f"""(SELECT value FROM {table_name}
                                            WHERE book = b.id LIMIT 1) AS "{field}" """)
                else:
                    print(f"⚠️  Campo personalizzato '{field}' non riconosciuto")
            elif field in self.field_queries:
                select_parts.append(f"{self.field_queries[field]} AS {field}")
            else:
                print(f"⚠️  Campo '{field}' non riconosciuto")

        # Costruisci la query finale
        query = f"""
            SELECT {', '.join(select_parts)}
            FROM books b
            ORDER BY b.id
        """

        results: list[dict[str, any]] = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query)

            for row in cursor.fetchall():
                book_dict = dict(row)
                # Rimuovi il campo temporaneo _id
                if '_id' in book_dict:
                    # Se id è richiesto, usalo, altrimenti usa _id come id
                    if 'id' not in book_dict:
                        book_dict['id'] = book_dict.pop('_id')
                    else:
                        del book_dict['_id']
                results.append(book_dict)

        return results

    def get_book_by_id(self, book_id: int) -> dict[str, any] | None:
        """Recupera un singolo libro per ID"""
        books = self.get_books()
        for book in books:
            if book.get('id') == book_id:
                return book
        return None

    def get_all_ids(self) -> list[int]:
        """Recupera tutti gli ID dei libri"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id FROM books ORDER BY id")
            return [row[0] for row in cursor.fetchall()]

    def get_book_file_path(self, book_metadata: dict[str, any]) -> Path | None:
        """Trova il percorso del file ebook"""
        if 'path' not in book_metadata:
            return None

        book_path = self.library_path / book_metadata['path']

        if book_path.exists():
            # Cerca file di ebook
            for ext in ['.epub', '.mobi', '.pdf', '.azw3', '.txt']:
                for file in book_path.glob(f"*{ext}"):
                    return file

        return None

    def get_available_fields(self) -> dict[str, str]:
        """Restituisce tutti i campi disponibili con una breve descrizione"""
        return {
            **self.field_queries,
            **{k: f"Campo personalizzato ({self.custom_columns[k]})"
               for k in self.custom_columns}
        }


# ============================================================
# UTILIZZO PRATICO
# ============================================================

def main(calibre_path: str | None = None) -> None:
    if calibre_path is None:
        # MODIFICA QUESTO PERCORSO
        calibre_path = "/home/loreto/filu/Library"  # <--- INSERISCI IL TUO PERCORSO

    print("=" * 70)
    print("📚 LETTURA METADATI DA CALIBRE")
    print("=" * 70)

    # Inizializza il lettore
    try:
        reader = CalibreMetadataReader(calibre_path)
    except FileNotFoundError as e:
        print(f"❌ Errore: {e}")
        print("   Verifica il percorso della libreria Calibre")
        return

    # Mostra campi disponibili
    print("\n📋 Campi disponibili:")
    available = reader.get_available_fields()
    for field, desc in available.items():
        print(f"  - {field}: {desc[:50]}...")

    # ===== 1. Tutti i libri con campi selezionati =====
    print("\n" + "=" * 70)
    print("1️⃣  Tutti i libri (campi principali):")
    print("=" * 70)

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
        '#Narrazione',
        '#ReadDate',
        '#Tipologia',
        '#Comments',
    ]

    books = reader.get_books(campi_principali)
    print(f"\n📚 Trovati {len(books)} libri\n")

    # Mostra i primi 3
    for i, book in enumerate(books[:3], 1):
        print(f"📖 Libro {i}: {book.get('title', 'Senza titolo')}")
        print(f"   Autori: {book.get('authors', 'N/D')}")
        print(f"   Editore: {book.get('publisher', 'N/D')}")
        print(f"   ISBN: {book.get('isbn', 'N/D')}")
        print(f"   Status: {book.get('#Status', 'N/D')}")
        if book.get('series'):
            print(f"   Serie: {book.get('series')}")
        if book.get('tags'):
            print(f"   Tags: {book.get('tags')}")
        print()

    # ===== 2. Statistiche =====
    print("=" * 70)
    print("2️⃣  Statistiche:")
    print("=" * 70)

    # Conta libri per Status
    status_count: dict[str, int] = {}
    for book in books:
        status = book.get('#Status', 'Senza status')
        status_count[status] = status_count.get(status, 0) + 1

    print("\n   📊 Libri per Status:")
    for status, count in sorted(status_count.items()):
        print(f"     - {status}: {count}")

    # Conta editore e ISBN
    with_publisher = sum(1 for b in books if b.get('publisher'))
    with_isbn = sum(1 for b in books if b.get('isbn'))

    print(f"\n   📊 Dettagli:")
    print(f"     - Con editore: {with_publisher}/{len(books)}")
    print(f"     - Con ISBN: {with_isbn}/{len(books)}")

    # ===== 3. Esporta in JSON =====
    print("\n" + "=" * 70)
    print("3️⃣  Esportazione dati:")
    print("=" * 70)

    export_file = Path("metadati_export.json")

    # Converti datetime in stringhe per JSON
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    try:
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(books, f, indent=2, ensure_ascii=False, default=json_serializer)
        print(f"   ✅ Dati esportati in: {export_file}")
        print(f"   📏 Dimensione: {export_file.stat().st_size / 1024:.1f} KB")
    except Exception as e:
        print(f"   ❌ Errore nell'esportazione: {e}")

    # ===== 4. Trova percorsi file =====
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

    # ===== 5. Dettaglio libro specifico =====
    print("\n" + "=" * 70)
    print("5️⃣  Dettaglio libro (ID 1):")
    print("=" * 70)

    book = reader.get_book_by_id(1)
    if book:
        for key, value in book.items():
            if value:
                print(f"   {key}: {value}")
    else:
        print("   ❌ Libro non trovato")

    print("\n" + "=" * 70)
    print("✅ Completato!")
    print("=" * 70)



if __name__ == "__main__":
    CALIBRE_PATH = "/home/loreto/filu/ln-eBooks/lnLibraries/Others"  # MODIFICA QUI
    CALIBRE_PATH = "/home/loreto/filu/ln-eBooks/lnLibraries/allInOne"  # MODIFICA QUI
    main(calibre_path=CALIBRE_PATH)
