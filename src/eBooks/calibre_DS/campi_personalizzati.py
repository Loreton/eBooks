#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
from pathlib import Path

def scopri_campi_personalizzati(db_path):
    """Scopre tutti i campi personalizzati nel database Calibre"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=" * 70)
    print("🔍 CAMP PERSONALIZZATI NEL DATABASE")
    print("=" * 70)

    # Leggi la tabella custom_columns
    try:
        cursor.execute("""
            SELECT
                id,
                name,
                datatype,
                label,
                display,
                is_multiple
            FROM custom_columns
            ORDER BY id
        """)

        columns = cursor.fetchall()

        if not columns:
            print("❌ Nessun campo personalizzato trovato!")
            return

        print(f"\n✅ Trovati {len(columns)} campi personalizzati:\n")

        for col_id, name, datatype, label, display, is_multiple in columns:
            print(f"📌 Campo #{name}")
            print(f"   ID tabella: {col_id}")
            print(f"   Tipo: {datatype}")
            print(f"   Label: {label}")
            print(f"   È multiplo: {is_multiple}")

            # Mostra un esempio di valori
            table_name = f"custom_column_{col_id}"
            cursor.execute(f"""
                SELECT value
                FROM {table_name}
                WHERE value IS NOT NULL AND value != ''
                LIMIT 3
            """)
            sample_values = cursor.fetchall()

            if sample_values:
                print(f"   Valori esempio: {', '.join([v[0] for v in sample_values])}")
            else:
                print("   Nessun valore presente")

            # Suggerisci il nome da usare nel codice
            print(f"   🔑 Usa nel codice: #{name}")
            print()

    except sqlite3.OperationalError as e:
        print(f"❌ Errore: {e}")
        print("   La tabella custom_columns potrebbe non esistere")

    conn.close()

if __name__ == "__main__":
    # MODIFICA QUESTO PERCORSO
    CALIBRE_PATH = "/home/loreto/filu/ln-eBooks/lnLibraries/allInOne"  # <--- INSERISCI IL TUO PERCORSO
    db_path = Path(CALIBRE_PATH) / "metadata.db"

    if not db_path.exists():
        print(f"❌ Database non trovato: {db_path}")
    else:
        scopri_campi_personalizzati(db_path)
