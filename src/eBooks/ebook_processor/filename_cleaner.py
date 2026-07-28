# ebook_processor/filename_cleaner.py
"""
Filename cleaning and normalization utilities
"""

import re
from pathlib import Path


class FilenameCleaner:
    """
    Classe per pulire e normalizzare i nomi dei file
    Rimuove pattern indesiderati come:
    - Parentesi e il loro contenuto: (Newton Compton 2022-05)
    - Numeri ISBN
    - Edizioni
    - Extra metadata
    """

    def __init__(self):
        # Pattern da rimuovere
        self.patterns = [
            # Parentesi tonde e il loro contenuto: (Newton Compton 2022-05)
            (r'\s*\([^)]*\)\s*', ' '),

            # Parentesi quadre e il loro contenuto: [Edizione 2022]
            (r'\s*\[[^\]]*\]\s*', ' '),

            # ISBN: 978-88-1234-567-8
            (r'\s*ISBN[-:\s]*\d+[-:\s]*\d+[-:\s]*\d+[-:\s]*\d+[-:\s]*\d+\s*', ' ', re.IGNORECASE),

            # Pattern "Edizione X" o "Ed."
            (r'\s*Edizione\s+\d+[ª°]?\s*', ' ', re.IGNORECASE),
            (r'\s*Ed\.\s+\d+[ª°]?\s*', ' ', re.IGNORECASE),

            # Volume: "Vol. 1" o "Volume 1"
            (r'\s*Vol\.?\s+\d+\s*', ' ', re.IGNORECASE),
            (r'\s*Volume\s+\d+\s*', ' ', re.IGNORECASE),

            # Anno in formato: "2022" con eventuale parentesi
            (r'\s*\(\s*\d{4}\s*\)\s*', ' '),
            (r'\s*\d{4}\s*', ' '),  # Solo se non fa parte di titolo? Da usare con cautela

            # Editore: "Newton Compton" (ma manteniamo se è parte del titolo?)
            (r'\s*[-:]\s*[A-Z][a-z]+\s+[A-Z][a-z]+\s*', ' '),

            # Pattern " di " seguito da casa editrice
            (r'\s*\([^)]*Edizioni?[^)]*\)\s*', ' ', re.IGNORECASE),
            (r'\s*\([^)]*Editore[^)]*\)\s*', ' ', re.IGNORECASE),
        ]

        # Pattern per mantenere (titoli nobiliari, parte del nome)
        self.preserve_patterns = [
            (r'\bDott\.?\s+', ''),  # Rimuovi titoli
            (r'\bProf\.?\s+', ''),
            (r'\bDr\.?\s+', ''),
        ]

    def clean_filename(self, filename: str, remove_authors: bool = False) -> str:
        """
        Pulisce il nome del file rimuovendo pattern indesiderati

        Args:
            filename: Nome del file da pulire
            remove_authors: Se rimuovere anche gli autori dal nome

        Returns:
            str: Nome del file pulito
        """
        if not filename:
            return "untitled"

        # Rimuovi l'estensione per lavorare sul nome base
        file_path = Path(filename)
        base_name = file_path.stem
        extension = file_path.suffix

        # Applica i pattern di pulizia
        clean_name = base_name

        # Se richiesto, rimuovi gli autori (pattern "Nome Cognome - ")
        if remove_authors:
            # Rimuovi pattern come "Elena Armas - "
            clean_name = re.sub(r'^[A-Z][a-z]+\s+[A-Z][a-z]+\s+[-–—]\s+', '', clean_name)
            # Rimuovi pattern come "Elena Armas, "
            clean_name = re.sub(r'^[A-Z][a-z]+\s+[A-Z][a-z]+\s*,\s*', '', clean_name)

        # Applica i pattern di pulizia
        for pattern, replacement, *flags in self.patterns:
            flags = flags[0] if flags else 0
            clean_name = re.sub(pattern, replacement, clean_name, flags=flags)


        # Pulizia finale
        clean_name = re.sub(r'\s+', ' ', clean_name).strip()  # Rimuovi spazi multipli
        clean_name = re.sub(r'[^\w\s\-]', '', clean_name)    #  Rimuovi caratteri speciali (mantieni solo lettere, numeri, spazi, underscore, trattini)
        clean_name = re.sub(r'\s+', '_', clean_name)         # Sostituisci spazi con underscore
        clean_name = re.sub(r'_+', '_', clean_name)          # Rimuovi underscore multipli
        clean_name = clean_name.strip('_')                   # Rimuovi underscore a inizio/fine


        # Se il nome è vuoto, usa un default
        if not clean_name:
            clean_name = "untitled"

        # Ricostruisci il filename con l'estensione
        return f"{clean_name}{extension}"

    def extract_title(self, filename: str) -> str:
        """Estrae il titolo dal nome del file"""
        return Path(self.clean_filename(filename, remove_authors=True)).stem

    def extract_author(self, filename: str) -> str | None:
        """Estrae l'autore dal nome del file se presente"""
        base_name = Path(filename).stem

        # Pattern "Nome Cognome - "
        match = re.match(r'^([A-Z][a-z]+\s+[A-Z][a-z]+)\s+[-–—]\s+', base_name)
        if match:
            return match.group(1)

        # Pattern "Nome Cognome, "
        match = re.match(r'^([A-Z][a-z]+\s+[A-Z][a-z]+)\s*,\s*', base_name)
        if match:
            return match.group(1)

        return None

    def get_clean_path___(self, filepath: Path, remove_authors: bool = False) -> Path:
        """
        Ottiene un Path con il nome del file pulito

        Args:
            filepath: Path del file originale
            remove_authors: Se rimuovere gli autori

        Returns:
            Path: Path con nome pulito
        """
        clean_name = self.clean_filename(filepath.name, remove_authors)
        return filepath.parent / clean_name


# class FilenamePatterns:
#     """
#     Pattern predefiniti per la pulizia dei nomi dei file
#     """

#     # Pattern per diversi formati di ebook

#     @classmethod
#     def get_all_patterns(cls) -> list[str]:
#         EPUB_PATTERNS = {
#             'amazon': [
#                 r'\(\s*Amazon\s+Digital\s+Services\s*\)',
#                 r'\(\s*Kindle\s+Edition\s*\)',
#             ],
#             'kobo': [
#                 r'\(\s*Kobo\s+Edition\s*\)',
#             ],
#             'google': [
#                 r'\(\s*Google\s+Books\s*\)',
#             ],
#             'editions': [
#                 r'\(\s*\d+[ª°]?\s+Edizione\s*\)',
#                 r'\(\s*Ed\.\s+\d+\s*\)',
#             ]
#         }
#         """Restituisce tutti i pattern"""
#         all_patterns = []
#         for patterns in EPUB_PATTERNS.values():
#             all_patterns.extend(patterns)
#         return all_patterns



def demo_filename_cleaning():
    """Funzione main per testare la classe"""

    """Demo della pulizia dei nomi dei file"""
    cleaner = FilenameCleaner()

    test_filenames = [
        "Elena Armas - Facciamo Finta Che Mi Ami (Newton Compton 2022-05).epub",
        "Paolo Bianchi - La Storia (Ed. 2023).epub",
        "Mario Rossi, Il Romanzo [ISBN 978-88-1234-567-8].epub",
        "Giulia Verdi - Poesie (Volume 2) (Editore XYZ 2024).epub",
        "Anna Neri - Racconti (Amazon Digital Services).epub",
    ]

    print("\n" + "=" * 60)
    print("🧹 TEST PULIZIA NOMI FILE")
    print("=" * 60)

    for filename in test_filenames:
        print(f"\n📄 Originale: {filename}")

        # Pulisci mantenendo l'autore
        clean_with_author = cleaner.clean_filename(filename, remove_authors=False)
        print(f"   Pulito (con autore): {clean_with_author}")

        # Pulisci rimuovendo l'autore
        clean_without_author = cleaner.clean_filename(filename, remove_authors=True)
        print(f"   Pulito (senza autore): {clean_without_author}")

        # Estrai titolo
        title = cleaner.extract_title(filename)
        print(f"   Titolo estratto: {title}")

        # Estrai autore
        author = cleaner.extract_author(filename)
        if author:
            print(f"   Autore estratto: {author}")



if __name__ == "__main__":
    demo_filename_cleaning()
