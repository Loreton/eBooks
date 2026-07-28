# ebook_processor/author_normalizer.py
"""
Author name normalization and management
"""

import re
from collections import defaultdict


class AuthorNormalizer:
    """
    Classe per normalizzare e gestire i nomi degli autori.
    Mantiene una mappa per associare diverse varianti allo stesso autore.
    """

    def __init__(self):
        # Mappa: nome_normalizzato -> nome_canonico
        self.author_map: dict[str, str] = {}
        # Mappa inversa: nome_canonico -> lista di varianti
        self.variants_map: dict[str, list[str]] = defaultdict(list)
        # Insieme di tutti gli autori normalizzati
        self.normalized_authors: set[str] = set()

    def normalize_author(self, author_name: str) -> str:
        """
        Normalizza il nome di un autore.
        Gestisce formati come:
        - "Mario Rossi" -> "Rossi, Mario"
        - "Rossi, Mario" -> "Rossi, Mario"
        - "Mario Rossi, PhD" -> "Rossi, Mario"
        - "Rossi Mario" -> "Rossi, Mario"

        Args:
            author_name: Nome dell'autore da normalizzare

        Returns:
            str: Nome normalizzato nel formato "Cognome, Nome"
        """
        if not author_name or author_name == "Sconosciuto":
            return "Sconosciuto"

        # Pulisci il nome da titoli e suffissi comuni
        clean_name = self._clean_author_name(author_name)

        # Dividi in parti
        parts = self._split_author_name(clean_name)

        if len(parts) == 1:
            # Solo un nome - prova a capire se è cognome o nome
            return parts[0]

        elif len(parts) == 2:
            # Due parti: potrebbe essere "Nome Cognome" o "Cognome, Nome"
            if ',' in author_name:
                # Già nel formato "Cognome, Nome"
                return f"{parts[0].strip()}, {parts[1].strip()}"
            else:
                # Formato "Nome Cognome" -> converti in "Cognome, Nome"
                return f"{parts[1].strip()}, {parts[0].strip()}"

        else:
            # Più di due parti - gestisci casi complessi
            return self._handle_complex_name(parts)

    def _clean_author_name(self, name: str) -> str:
        """Rimuove titoli, suffissi e caratteri speciali dal nome"""
        # Rimuovi titoli comuni
        titles = [
            'Dr.', 'Dr', 'Dott.', 'Dott', 'Prof.', 'Prof',
            'PhD', 'M.D.', 'MD', 'Sr.', 'Jr.', 'I', 'II', 'III',
            'IV', 'V', 'VI'
        ]

        clean = name
        for title in titles:
            clean = clean.replace(title, '')

        # Rimuovi parentesi e il loro contenuto
        clean = re.sub(r'\([^)]*\)', '', clean)
        clean = re.sub(r'\[[^]]*\]', '', clean)

        # Rimuovi spazi multipli e trim
        clean = re.sub(r'\s+', ' ', clean).strip()

        # Rimuovi virgole extra
        clean = re.sub(r',+', ',', clean)

        return clean

    def _split_author_name(self, name: str) -> list[str]:
        """Divide il nome in parti gestendo virgole e spazi"""
        if ',' in name:
            # Formato "Cognome, Nome"
            parts = [p.strip() for p in name.split(',')]
        else:
            # Formato "Nome Cognome"
            parts = name.split()

        return [p for p in parts if p]  # Rimuovi parti vuote

    def _handle_complex_name(self, parts: list[str]) -> str:
        """Gestisce nomi con più di due parti"""
        # Cerca di capire se l'ultima parte è il cognome
        # Assumiamo che l'ultima parola sia il cognome
        if len(parts) >= 2:
            last_name = parts[-1]
            first_name = ' '.join(parts[:-1])
            return f"{last_name}, {first_name}"
        else:
            return ' '.join(parts)

    def get_canonical_name(self, author_name: str) -> str:
        """
        Ottiene il nome canonico per un autore.
        Se l'autore non esiste nella mappa, lo aggiunge.

        Args:
            author_name: Nome dell'autore da normalizzare

        Returns:
            str: Nome canonico normalizzato
        """
        if not author_name or author_name == "Sconosciuto":
            return "Sconosciuto"

        normalized = self.normalize_author(author_name)

        # Verifica se esiste già nella mappa
        if normalized in self.author_map:
            return self.author_map[normalized]

        # Cerca varianti simili
        for existing_normalized, canonical in self.author_map.items():
            if self._are_similar(normalized, existing_normalized):
                # Aggiungi come variante
                self.variants_map[canonical].append(author_name)
                return canonical

        # Nuovo autore - aggiungi alla mappa
        self.author_map[normalized] = normalized
        self.normalized_authors.add(normalized)
        self.variants_map[normalized].append(author_name)

        return normalized

    def _are_similar(self, name1: str, name2: str) -> bool:
        """Verifica se due nomi sono simili (fuzzy matching base)"""
        # Normalizza entrambi
        n1 = name1.lower().replace(',', '').strip()
        n2 = name2.lower().replace(',', '').strip()

        # Controlla se condividono parole chiave
        words1 = set(n1.split())
        words2 = set(n2.split())

        # Se hanno almeno una parola in comune (probabilmente il cognome)
        if words1 & words2:
            # Verifica che la parola condivisa sia lunga almeno 2 caratteri
            common = words1 & words2
            for word in common:
                if len(word) >= 2:
                    return True

        return False

    def get_all_authors(self) -> list[str]:
        """Restituisce tutti gli autori normalizzati"""
        return sorted(self.normalized_authors)

    def get_author_variants(self, canonical_name: str) -> list[str]:
        """Restituisce tutte le varianti di un autore"""
        return self.variants_map.get(canonical_name, [canonical_name])

    def get_author_directory_name(self, author_name: str, max_length: int = 100) -> str:
        """
        Genera un nome di directory valido per un autore

        Args:
            author_name: Nome dell'autore
            max_length: Lunghezza massima del nome della directory

        Returns:
            str: Nome valido per una directory
        """
        if not author_name or author_name == "Sconosciuto":
            return "Unknown_Author"

        # Normalizza per uso come nome directory
        dir_name = author_name.replace(',', '').strip()
        dir_name = re.sub(r'[^a-zA-Z0-9_\s-]', '', dir_name)
        dir_name = re.sub(r'\s+', '_', dir_name)

        # Limita la lunghezza del nome della directory
        if len(dir_name) > max_length:
            dir_name = dir_name[:max_length]

        return dir_name
