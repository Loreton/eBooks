#! /usr/bin/env python3
# updated by ...: Loreto Notarantonio
# Date .........: 05-02-2025 17.28.56
#
import os
from ..eBooks.ebook_processor.ebook_manager_deepseek01 import EpubProcessor


def scan_and_process(directory: str):
    """Scansiona e processa tutti gli EPUB in una directory."""
    results = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.epub'):
                epub_path = os.path.join(root, file)
                try:
                    processor = EpubProcessor(epub_path)
                    info = processor.get_info()
                    info['percorso'] = epub_path
                    info['capitoli'] = len(processor.get_chapters_titles())
                    results.append(info)
                    print(f"✓ {info['titolo']} - {info['autore']}")
                except Exception as e:
                    print(f"✗ Errore in {file}: {e}")

    return results

# Utilizzo
libri = scan_and_process("/percorso/libreria")
print(f"\nTrovati {len(libri)} libri EPUB")
