#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
from pathlib import Path

def esplora_database(db_path):
    """Esplora la struttura del database di Calibre"""

    if not Path(db_path).exists():
        print(f"❌ Database non trovato: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=" * 70)
    print("🔍 ESPLORAZIONE DATABASE CALIBRE")
    print("=" * 70)

    # 1. Tutte le tabelle
    print("\n📊 TABELLE NEL DATABASE:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()
    for table in tables:
        print(f"  - {table[0]}")

    # 2. Struttura della tabella books
    print("\n📋 COLONNE NELLA TABELLA 'books':")
    cursor.execute("PRAGMA table_info(books);")
    columns = cursor.fetchall()
    col_names = []
    for col in columns:
        col_names.append(col[1])
        print(f"  - {col[1]} ({col[2]})")

    # 3. Primi 5 libri con tutti i campi
    print("\n📖 PRIMI 5 LIBRI (tutti i campi):")
    cursor.execute("SELECT * FROM books LIMIT 5;")
    rows = cursor.fetchall()

    for i, row in enumerate(rows, 1):
        print(f"\nLibro {i}:")
        for j, value in enumerate(row):
            if value:  # Mostra solo i campi con valori
                print(f"  {col_names[j]}: {value[:100] if isinstance(value, str) and len(value) > 100 else value}")

    # 4. Statistiche sui campi
    print("\n📊 STATISTICHE CAMPI:")

    # Controlla quali campi hanno dati
    for col in col_names:
        try:
            cursor.execute(f"SELECT COUNT({col}) FROM books WHERE {col} IS NOT NULL AND {col} != '';")
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"  - {col}: {count} libri hanno questo campo")
        except:
            pass

    # 5. Campi personalizzati (se presenti)
    print("\n🏷️  CAMP PERSONALIZZATI:")
    try:
        cursor.execute("SELECT id, name, datatype FROM custom_columns;")
        custom_cols = cursor.fetchall()
        if custom_cols:
            for col_id, name, datatype in custom_cols:
                table_name = f"custom_column_{col_id}"
                print(f"  - #{name} (tabella: {table_name}, tipo: {datatype})")
        else:
            print("  Nessun campo personalizzato trovato")
    except:
        print("  Tabella custom_columns non trovata")

    conn.close()

    print("\n" + "=" * 70)
    print("✅ Esplorazione completata!")
    print("=" * 70)

if __name__ == "__main__":
    # MODIFICA QUESTO PERCORSO
    CALIBRE_PATH = "/home/loreto/filu/ln-eBooks/lnLibraries/Others"   # <--- INSERISCI IL PERCORSO QUI

    db_path = Path(CALIBRE_PATH) / "metadata.db"
    esplora_database(db_path)
