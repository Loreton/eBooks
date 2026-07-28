# ebook_processor/conflict_manager.py
"""
File conflict management for duplicate filenames
"""

import hashlib
from pathlib import Path
from collections import defaultdict
import re


class FileConflictManager:
    """
    Gestisce i conflitti di nome file quando si salvano i libri
    """

    def __init__(self):
        # Traccia i file già salvati: {author_dir: {filename_base: count}}
        self.saved_files: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        # Traccia i file originali per evitare rinominare inutilmente
        self.file_hashes: dict[str, str] = {}

    def get_unique_filename(self, directory: Path, base_filename: str,
                           extension: str = '.txt') -> Path:
        """
        Genera un nome file unico nella directory, gestendo i conflitti

        Args:
            directory: Directory dove salvare il file
            base_filename: Nome base del file (senza estensione)
            extension: Estensione del file

        Returns:
            Path: Percorso unico per il file
        """
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        # Pulisci il nome base
        clean_base = self._clean_filename(base_filename)

        # Controlla se esiste già
        counter = self.saved_files[str(directory)][clean_base]

        if counter == 0:
            # Prima occorrenza - usa il nome base
            filename = f"{clean_base}{extension}"
            self.saved_files[str(directory)][clean_base] = 1
            return directory / filename
        else:
            # Conflitto - aggiungi numero
            filename = f"{clean_base}_{counter:03d}{extension}"
            self.saved_files[str(directory)][clean_base] = counter + 1
            return directory / filename

    def _clean_filename(self, filename: str) -> str:
        """Pulisce il filename rimuovendo caratteri non validi"""
        if not filename:
            return "untitled"

        # Rimuovi caratteri non validi per filename
        clean = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Rimuovi spazi multipli
        clean = re.sub(r'\s+', ' ', clean).strip()
        # Sostituisci spazi con underscore
        clean = re.sub(r'\s+', '_', clean)
        # Limita lunghezza
        if len(clean) > 200:
            clean = clean[:200]
        return clean

    def add_file_hash(self, file_path: Path, content: str) -> str:
        """
        Aggiunge un hash del contenuto per identificare duplicati

        Args:
            file_path: Percorso del file
            content: Contenuto del file

        Returns:
            str: Hash del contenuto
        """
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        self.file_hashes[str(file_path)] = content_hash
        return content_hash

    def is_duplicate_content(self, content: str, existing_hash: str) -> bool:
        """Verifica se il contenuto è duplicato"""
        new_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        return new_hash == existing_hash

    def get_stats(self) -> dict[str, str|int|float]:
        """Restituisce statistiche sui conflitti gestiti"""
        total_conflicts = 0
        total_files = 0

        for dir_files in self.saved_files.values():
            for count in dir_files.values():
                total_files += count
                if count > 1:
                    total_conflicts += count - 1

        return {
            'total_files': total_files,
            'total_conflicts': total_conflicts,
            'conflict_ratio': total_conflicts / total_files if total_files > 0 else 0
        }

    def reset(self):
        """Resetta il manager (utile per nuove sessioni)"""
        self.saved_files.clear()
        self.file_hashes.clear()
