#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import os
from pathlib import Path

class CalibreMetadataReader:
    """
    Lettore leggero dei metadati di Calibre usando SQLite.
    Non richiede l'installazione di Calibre.
    """

    def __init__(self, library_path: str):
        """
        Inizializza il lettore con il percorso della libreria Calibre.

        Args:
            library_path (str): Percorso della cartella della libreria Calibre
                               (quella che contiene metadata.db)
        """
        self.library_path = Path(library_path)
        self.db_path = self.library_path / "metadata.db"

        if not self.db_path.exists():
            raise FileNotFoundError(f"Database non trovato: {self.db_path}")

        # Dizionario per mappare i campi richiesti alle query SQL
        self._field_mappings = {
            'id': 'b.id',
            'title': 'b.title',
            'authors': self._get_authors_subquery(),
            'publisher': 'b.publisher',
            'pubdate': 'b.pubdate',
            'isbn': 'b.isbn',
            'series': self._get_series_subquery(),
            'series_index': 'b.series_index',
            'tags': self._get_tags_subquery(),
            'comments': 'b.comments',
            'language': 'b.language',
            'path': 'b.path',
            'formats': self._get_formats_subquery(),
            'rating': 'b.rating',
            'timestamp': 'b.timestamp',
            'last_modified': 'b.last_modified',
        }

    # ============ SUBQUERY METODI PER I CAMPI COMPLESSI ============

    def _get_authors_subquery(self) -> str:
        """Subquery per ottenere tutti gli autori come stringa"""
        return """(
            SELECT group_concat(a.name, ', ')
            FROM books_authors_link AS bal
            JOIN authors AS a ON bal.author = a.id
            WHERE bal.book = b.id
        )"""

    def _get_series_subquery(self) -> str:
        """Subquery per ottenere la serie (solo la prima, se multipla)"""
        return """(
            SELECT s.name
            FROM books_series_link AS bsl
            JOIN series AS s ON bsl.series = s.id
            WHERE bsl.book = b.id
            LIMIT 1
        )"""

    def _get_tags_subquery(self) -> str:
        """Subquery per ottenere tutti i tag come stringa"""
        return """(
            SELECT group_concat(t.name, ', ')
            FROM books_tags_link AS btl
            JOIN tags AS t ON btl.tag = t.id
            WHERE btl.book = b.id
        )"""

    def _get_formats_subquery(self) -> str:
        """Subquery per ottenere tutti i formati come stringa"""
        return """(
            SELECT group_concat(format, ', ')
            FROM data
            WHERE data.book = b.id
        )"""

    # ============ METODO PER I CAMPI PERSONALIZZATI ============

    def _get_custom_columns(self) -> dict[str, str]:
        """
        Identifica i campi personalizzati nel database.

        Returns:
            dict: {nome_colonna: nome_tabella}
        """
        custom_cols = {}

        # La tabella custom_columns contiene le definizioni
        query = """
            SELECT id, name, datatype
            FROM custom_columns
            WHERE is_multiple = 0 OR is_multiple IS NULL
        """

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query)
                for col_id, name, datatype in cursor.fetchall():
                    # La tabella dei valori è custom_column_{id}
                    table_name = f"custom_column_{col_id}"
                    custom_cols[name] = table_name
        except sqlite3.OperationalError:
            # Potrebbe non esistere se non ci sono campi personalizzati
            pass

        return custom_cols

    def _get_custom_value_subquery(self, col_name: str, table_name: str) -> str:
        """
        Genera la subquery per un campo personalizzato.

        Args:
            col_name (str): Nome del campo personalizzato
            table_name (str): Nome della tabella dei valori

        Returns:
            str: Subquery SQL
        """
        return f"""(
            SELECT value
            FROM {table_name}
            WHERE {table_name}.book = b.id
            LIMIT 1
        )"""

    # ============ METODO PRINCIPALE ============

    def get_books(self, fields: list[str] = None) -> list[dict[str, any]]:
        """
        Recupera i libri dal database con i campi specificati.

        Args:
            fields (list[str]): Lista dei campi da estrarre.
                               Se None, usa tutti i campi standard.
                               Esempi: ['id', 'title', 'authors', 'tags']

        Returns:
            list[dict[str, any]]: Lista di dizionari con i metadati
        """
        # Se non specificato, usa tutti i campi standard
        if fields is None:
            fields = list(self._field_mappings.keys())

        # Prepara la query
        select_parts = []
        for field in fields:
            if field.startswith('#'):
                # Campo personalizzato - lo gestiamo dopo
                continue
            if field in self._field_mappings:
                select_parts.append(f"{self._field_mappings[field]} AS {field}")
            else:
                print(f"⚠️  Campo '{field}' non riconosciuto, ignorato")

        if not select_parts:
            raise ValueError("Nessun campo valido specificato")

        # Query base
        query = f"""
            SELECT {', '.join(select_parts)}
            FROM books b
            ORDER BY b.id
        """

        # Esegui la query
        results = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query)

            # Ottieni i campi personalizzati se richiesti
            custom_fields = [f for f in fields if f.startswith('#')]
            custom_columns = self._get_custom_columns() if custom_fields else {}

            for row in cursor.fetchall():
                book_dict = dict(row)

                # Aggiungi campi personalizzati
                for custom_field in custom_fields:
                    col_name = custom_field.lstrip('#')
                    if col_name in custom_columns:
                        table_name = custom_columns[col_name]
                        subquery = self._get_custom_value_subquery(col_name, table_name)

                        # Esegui subquery per questo libro
                        val_query = f"SELECT value FROM {table_name} WHERE book = ? LIMIT 1"
                        val_cursor = conn.execute(val_query, (book_dict['id'],))
                        val_row = val_cursor.fetchone()

                        book_dict[custom_field] = val_row[0] if val_row else None
                    else:
                        book_dict[custom_field] = None

                results.append(book_dict)

        return results

    def get_book_by_id(self, book_id: int, fields: list[str] = None) -> dict[str, any]:
        """
        Recupera un singolo libro per ID.

        Args:
            book_id (int): ID del libro
            fields (list[str]): Campi da estrarre

        Returns:
            dict[str, any]: Metadati del libro o None se non trovato
        """
        books = self.get_books(fields)
        for book in books:
            if book.get('id') == book_id:
                return book
        return None

    def get_all_ids(self) -> list[int]:
        """
        Recupera tutti gli ID dei libri.

        Returns:
            list[int]: Lista di ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id FROM books ORDER BY id")
            return [row[0] for row in cursor.fetchall()]

    def get_book_file_path(self, book_metadata: dict[str, any]) -> Path|None:
        """
        Costruisce il percorso completo del file ebook.

        Args:
            book_metadata (dict): Metadati del libro (deve contenere 'path' e 'id')

        Returns:
            Path: Percorso del file o None se non trovato
        """
        if 'path' not in book_metadata:
            return None

        # Il percorso in Calibre è relativo alla libreria
        book_path = self.library_path / book_metadata['path']

        # Cerca file in quella cartella
        if book_path.exists():
            # Cerca qualsiasi file che non sia metadata.opf o cover.jpg
            for file in book_path.iterdir():
                if file.is_file() and file.suffix.lower() in ['.epub', '.mobi', '.pdf', '.azw3', '.txt']:
                    return file

        return None



import sqlite3

def esplora_database(db_path):
    """Esplora la struttura del database di Calibre"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Vedi tutte le tabelle
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("📊 Tabelle nel database:")
    for table in tables:
        print(f"  - {table[0]}")

    # 2. Vedi le colonne della tabella books
    print("\n📋 Colonne nella tabella 'books':")
    cursor.execute("PRAGMA table_info(books);")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

    # 3. Vedi un esempio di dati
    print("\n📖 Primo libro (esempio):")
    cursor.execute("SELECT * FROM books LIMIT 1;")
    sample = cursor.fetchone()
    if sample:
        col_names = [col[1] for col in columns]
        for i, value in enumerate(sample):
            if value:  # Mostra solo i campi non vuoti
                print(f"  {col_names[i]}: {value}")

    conn.close()




# ============================================================
# ESEMPIO DI UTILIZZO
# ============================================================

def main():
    # Configurazione
    CALIBRE_PATH = "/home/loreto/filu/ln-eBooks/lnLibraries/Others"  # MODIFICA QUI

    # Inizializza il lettore
    reader = CalibreMetadataReader(CALIBRE_PATH)

    print("=" * 60)
    print("📚 LETTURA METADATI DA CALIBRE")
    print("=" * 60)

    # ===== ESEMPIO 1: Leggi tutti i libri con campi specifici =====
    print("\n1️⃣  Tutti i libri con campi selezionati:")

    # Scegli quali campi vuoi
    campi_richiesti = [
        'id',
        'title',
        'authors',
        'publishers',
        'pubdate',
        'series',
        'tags',
        # 'isbn',
        'path',
        '#stato',      # Campo personalizzato (se esiste)
        '#genere',     # Campo personalizzato (se esiste)
    ]

    books = reader.get_books(campi_richiesti)

    print(f"Trovati {len(books)} libri\n")

    # Mostra i primi 3 come esempio
    for i, book in enumerate(books[:3], 1):
        print(f"Libro {i}:")
        for key, value in book.items():
            if value:
                print(f"  {key}: {value}")
        print("-" * 40)

    # ===== ESEMPIO 2: Ottieni solo alcuni campi per tutti i libri =====
    print("\n2️⃣  Solo titolo e autore per tutti i libri:")

    campi_minimi = ['id', 'title', 'authors']
    books_slim = reader.get_books(campi_minimi)

    for book in books_slim[:5]:  # primi 5
        print(f"  {book['id']}: {book['title']} - {book['authors']}")

    # ===== ESEMPIO 3: Cerca un libro specifico =====
    print("\n3️⃣  Cerca un libro per titolo (esempio):")

    # Cerca manualmente nei risultati
    ricerca = "Harry"
    trovati = [b for b in books if ricerca.lower() in b.get('title', '').lower()]

    for book in trovati[:3]:
        print(f"  📖 {book['title']} di {book['authors']}")
        print(f"     ID: {book['id']}")
        if book.get('#stato'):
            print(f"     Stato: {book['#stato']}")

    # ===== ESEMPIO 4: Ottieni i percorsi dei file =====
    print("\n4️⃣  Percorsi dei file ebook:")

    for book in books[:3]:
        file_path = reader.get_book_file_path(book)
        if file_path:
            print(f"  {book['title']}: {file_path}")
        else:
            print(f"  {book['title']}: Nessun file trovato")

    # ===== ESEMPIO 5: Esporta in formato strutturato (es. JSON) =====
    print("\n5️⃣  Esempio di esportazione strutturata:")

    import json

    # Prepara i dati per l'export
    export_data = {
        'total_books': len(books),
        'fields': campi_richiesti,
        'books': books
    }

    # Salva come JSON (solo per esempio, puoi usare il tuo formato)
    output_file = Path("metadati_export.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, default=str, ensure_ascii=False)

    print(f"  💾 Dati esportati in: {output_file}")

    # ===== STATISTICHE =====
    print("\n📊 Statistiche:")
    print(f"  Totale libri: {len(books)}")

    # Conteggio per formato
    if 'formats' in campi_richiesti:
        formats_count = {}
        for book in books:
            if book.get('formats'):
                for fmt in book['formats'].split(', '):
                    formats_count[fmt] = formats_count.get(fmt, 0) + 1
        print("  Formati disponibili:")
        for fmt, count in formats_count.items():
            print(f"    {fmt}: {count}")


if __name__ == "__main__":
    CALIBRE_PATH = "/home/loreto/filu/ln-eBooks/lnLibraries/Others"  # MODIFICA QUI

    esplora_database(f"{CALIBRE_PATH}/metadata.db")
    # main()
