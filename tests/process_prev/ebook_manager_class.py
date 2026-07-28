#! /usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 30-09-2025 18.06.06
#
import sys
sys.dont_write_bytecode = True
import re
import logging
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import hashlib

import ebooklib
from ebooklib import epub
import bs4


from pyLnLib import get_logger
logger = get_logger()


@dataclass
class EbookMetadata:
    """Data class per i metadati dell'ebook"""
    title: str = "Sconosciuto"
    authors: list[str] = field(default_factory=lambda: ["Sconosciuto"])
    language: str = "Sconosciuto"
    publisher: str = "Sconosciuto"
    publication_date: str = "Sconosciuto"


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

    def get_author_directory_name(self, author_name: str) -> str:
        """
        Genera un nome di directory valido per un autore

        Args:
            author_name: Nome dell'autore

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
        if len(dir_name) > 100:
            dir_name = dir_name[:100]

        return dir_name


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

    def get_stats(self) -> dict[str, any]:
        """Restituisce statistiche sui conflitti gestiti"""
        total_conflicts = 0
        total_files = 0

        for dir_files in self.saved_files.values():
            for base_name, count in dir_files.items():
                total_files += count
                if count > 1:
                    total_conflicts += count - 1

        return {
            'total_files': total_files,
            'total_conflicts': total_conflicts,
            'conflict_ratio': total_conflicts / total_files if total_files > 0 else 0
        }


class EbookProcessor:
    """
    Classe per processare ebook EPUB con funzionalità di:
    - Estrazione metadati
    - Estrazione testo pulito
    - Ricerca di testo nei libri
    - Scanning di directory
    - Organizzazione per autore
    - Gestione conflitti di nome
    """

    def __init__(self, decode_type: str = 'lxml', normalize_text: bool = True):
        """
        Inizializza il processor per ebook

        Args:
            decode_type: Tipo di parser per BeautifulSoup ('lxml' o 'html.parser')
            normalize_text: Se normalizzare il testo (rimuovere spazi multipli, etc.)
        """
        self.decode_type = decode_type
        self.normalize_text = normalize_text
        self.files_processed = 0
        self.books_processed: dict[str, dict] = {}
        self.author_normalizer = AuthorNormalizer()
        self.conflict_manager = FileConflictManager()

        # Setup per lxml warnings
        if decode_type == 'lxml':
            import warnings
            warnings.filterwarnings("ignore", category=bs4.XMLParsedAsHTMLWarning)

    def extract_metadata(self, book: epub.EpubBook) -> EbookMetadata:
        """
        Estrae i metadati dal libro EPUB

        Args:
            book: Oggetto libro EPUB

        Returns:
            EbookMetadata: Metadati estratti
        """
        metadata = EbookMetadata()

        # Estrai titolo
        try:
            titles = book.get_metadata('DC', 'title')
            if titles:
                metadata.title = self._get_first_item(titles)
        except Exception as e:
            logger.warning(f"Errore estrazione titolo: {e}")

        # Estrai autori e normalizzali
        try:
            creators = book.get_metadata('DC', 'creator')
            if creators:
                raw_authors = [c[0] for c in creators if c]
                # Normalizza ogni autore
                normalized_authors = []
                for author in raw_authors:
                    canonical = self.author_normalizer.get_canonical_name(author)
                    if canonical not in normalized_authors:
                        normalized_authors.append(canonical)
                metadata.authors = normalized_authors
        except Exception as e:
            logger.warning(f"Errore estrazione autori: {e}")

        # Estrai lingua
        try:
            languages = book.get_metadata('DC', 'language')
            if languages:
                metadata.language = self._get_first_item(languages)
        except Exception:
            pass

        # Estrai editore
        try:
            publishers = book.get_metadata('DC', 'publisher')
            if publishers:
                metadata.publisher = self._get_first_item(publishers)
        except Exception:
            pass

        return metadata

    def _get_first_item(self, value) -> str:
        """Helper per estrarre il primo item da una struttura dati"""
        if not value:
            return "Sconosciuto"
        if isinstance(value, (list, tuple)):
            if value:
                return self._get_first_item(value[0])
        return str(value).strip()

    def extract_text_from_epub(self, epub_file: Path) -> dict[str, any]:
        """
        Estrae il testo pulito da un file EPUB

        Args:
            epub_file: Percorso del file EPUB

        Returns:
            dict: Dizionario con metadati e contenuto del libro
        """
        if not epub_file.exists():
            logger.error(f"File non trovato: {epub_file}")
            return {}

        try:
            book = epub.read_epub(str(epub_file))
        except Exception as e:
            logger.error(f"Errore apertura file {epub_file}: {e}")
            return {}

        # Estrai metadati
        metadata = self.extract_metadata(book)

        # Estrai contenuto
        content = {}
        content['metadata'] = metadata
        content['source_file'] = str(epub_file)
        content['file_hash'] = hashlib.md5(str(epub_file).encode()).hexdigest()

        # Estrai testo completo per hash e contenuto
        full_text = []

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                try:
                    clean_text = self._process_document_item(item)
                    if clean_text:
                        # Usa le prime parole come identificatore della sezione
                        section_id = self._extract_section_id(clean_text)
                        content[section_id] = clean_text
                        full_text.append(clean_text)
                except Exception as e:
                    logger.warning(f"Errore processamento item: {e}")

        # Aggiungi hash del contenuto per rilevare duplicati
        if full_text:
            full_content = ' '.join(full_text)
            content['content_hash'] = hashlib.md5(full_content.encode('utf-8')).hexdigest()
        else:
            content['content_hash'] = hashlib.md5(b'empty').hexdigest()

        return content

    def _process_document_item(self, item) -> str:
        """Processa un item documento e restituisce testo pulito"""
        raw_content = item.content
        decoded_content = raw_content.decode('utf-8', errors='ignore')

        soup = bs4.BeautifulSoup(decoded_content, self.decode_type)

        # Estrai testo
        clean_text = soup.get_text(separator=' ', strip=True)

        # Normalizza se richiesto
        if self.normalize_text:
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        return clean_text

    def _extract_section_id(self, text: str) -> str:
        """Estrae un ID per la sezione dalle prime parole"""
        if not text:
            return "section_unknown"

        # Prendi le prime parole come ID
        first_words = text.split(' ', 3)[:3]
        section_id = '_'.join(first_words).strip()

        # Rimuovi caratteri non validi per ID
        section_id = re.sub(r'[^a-zA-Z0-9_]', '_', section_id)

        return section_id or "section_unknown"

    def search_text_in_ebook(self, epub_file: Path, search_text: str,
                           case_sensitive: bool = False) -> list[dict[str, any]]:
        """
        Cerca testo in un ebook e restituisce i risultati

        Args:
            epub_file: Percorso del file EPUB
            search_text: Testo da cercare
            case_sensitive: Se la ricerca deve essere case-sensitive

        Returns:
            list[dict]: Lista di risultati con contesto
        """
        results = []

        if not epub_file.exists():
            logger.error(f"File non trovato: {epub_file}")
            return results

        try:
            book = epub.read_epub(str(epub_file))
            metadata = self.extract_metadata(book)
        except Exception as e:
            logger.error(f"Errore apertura file {epub_file}: {e}")
            return results

        search_pattern = re.compile(re.escape(search_text),
                                  0 if case_sensitive else re.IGNORECASE)

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                try:
                    clean_text = self._process_document_item(item)

                    # Cerca il pattern nel testo
                    matches = list(search_pattern.finditer(clean_text))

                    for match in matches:
                        # Estrai contesto (100 caratteri prima e dopo)
                        start = max(0, match.start() - 100)
                        end = min(len(clean_text), match.end() + 100)
                        context = clean_text[start:end]

                        results.append({
                            'file': str(epub_file),
                            'title': metadata.title,
                            'authors': metadata.authors,
                            'context': context,
                            'match': match.group(),
                            'position': match.start()
                        })

                except Exception as e:
                    logger.warning(f"Errore ricerca in item: {e}")

        return results

    def scan_directory(self, root_dir: Path, pattern: str = '*.epub',
                       recursive: bool = True) -> list[Path]:
        """
        Scansiona una directory per trovare file EPUB

        Args:
            root_dir: Directory root da scansionare
            pattern: Pattern dei file da cercare
            recursive: Se cercare ricorsivamente

        Returns:
            list[Path]: Lista di percorsi dei file trovati
        """
        root_path = Path(root_dir)
        if not root_path.exists():
            logger.error(f"Directory non trovata: {root_path}")
            return []

        if recursive:
            file_list = list(root_path.glob(f'**/{pattern}'))
        else:
            file_list = list(root_path.glob(pattern))

        logger.info(f"Trovati {len(file_list)} file {pattern} in {root_path}")
        return file_list

    def process_directory(self, root_dir: Path, output_dir: Path | None = None,
                         pattern: str = '*.epub',
                         organize_by_author: bool = True,
                         skip_duplicates: bool = True) -> dict[str, dict[str, any]]:
        """
        Processa tutti gli EPUB in una directory

        Args:
            root_dir: Directory da processare
            output_dir: Directory per i file di output (opzionale)
            pattern: Pattern dei file da processare
            organize_by_author: Se organizzare i file per autore
            skip_duplicates: Se saltare i file duplicati basati sul contenuto

        Returns:
            dict: Dizionario con i risultati del processamento
        """
        results = {}
        epub_files = self.scan_directory(root_dir, pattern)
        processed_hashes = set()  # Per tracciare contenuti duplicati

        for i, epub_file in enumerate(epub_files, 1):
            logger.info(f"[{i}/{len(epub_files)}] Processando: {epub_file.name}")

            try:
                content = self.extract_text_from_epub(epub_file)
                if not content:
                    logger.warning(f"Nessun contenuto estratto da {epub_file.name}")
                    continue

                # Verifica duplicati basati sul contenuto
                if skip_duplicates:
                    content_hash = content.get('content_hash')
                    if content_hash and content_hash in processed_hashes:
                        logger.info(f"  ⏭️  Skipping duplicato: {epub_file.name}")
                        continue
                    if content_hash:
                        processed_hashes.add(content_hash)

                results[str(epub_file)] = content
                self.files_processed += 1

                # Salva se richiesto
                if output_dir:
                    self._save_book_content(epub_file, content, output_dir, organize_by_author)

            except Exception as e:
                logger.error(f"Errore processando {epub_file}: {e}")

        # Salva il report degli autori e dei conflitti
        if output_dir:
            self._save_author_report(output_dir)
            self._save_conflict_report(output_dir)

        logger.info(f"Processati {self.files_processed} file con successo")
        return results

    def _save_book_content(self, epub_file: Path, content: dict, output_dir: Path,
                          organize_by_author: bool = True):
        """
        Salva il contenuto del libro in un file di testo, gestendo i conflitti di nome

        Args:
            epub_file: File EPUB originale
            content: Contenuto del libro
            output_dir: Directory di output
            organize_by_author: Se organizzare per autore
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        metadata = content.get('metadata')

        # Determina la directory di destinazione
        target_dir = output_dir

        if organize_by_author and metadata and metadata.authors and metadata.authors[0] != "Sconosciuto":
            primary_author = metadata.authors[0]
            author_dir_name = self.author_normalizer.get_author_directory_name(primary_author)
            target_dir = output_dir / author_dir_name
            target_dir.mkdir(parents=True, exist_ok=True)

            # Salva anche l'elenco dei libri dell'autore
            if len(metadata.authors) > 1:
                authors_file = target_dir / "_AUTHORS.txt"
                with open(authors_file, 'a', encoding='utf-8') as af:
                    af.write(f"{metadata.title}: {', '.join(metadata.authors)}\n")

        # Prepara il nome base del file
        if metadata and metadata.title != "Sconosciuto":
            base_filename = self._sanitize_filename(metadata.title)
        else:
            base_filename = self._sanitize_filename(epub_file.stem)

        # Aggiungi informazioni extra per distinguere edizioni diverse
        extra_info = []
        if metadata and metadata.publisher and metadata.publisher != "Sconosciuto":
            extra_info.append(metadata.publisher)
        if metadata and metadata.publication_date and metadata.publication_date != "Sconosciuto":
            extra_info.append(metadata.publication_date)

        if extra_info:
            base_filename += f"_{'_'.join(extra_info[:2])}"

        # Limita la lunghezza del nome file
        if len(base_filename) > 200:
            base_filename = base_filename[:200]

        # Ottieni un nome unico usando il conflict manager
        output_file = self.conflict_manager.get_unique_filename(
            target_dir,
            base_filename,
            '.txt'
        )

        # Verifica se è un duplicato (contenuto già salvato)
        # Crea un hash del contenuto da salvare
        content_text = self._prepare_content_text(epub_file, content)
        content_hash = hashlib.md5(content_text.encode('utf-8')).hexdigest()

        # Salva il file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content_text)

            # Registra l'hash
            self.conflict_manager.add_file_hash(output_file, content_text)

            # Log del risultato
            if '_' in output_file.name and output_file.name.count('_') > 2:
                # C'è un numero di versione nel nome
                logger.info(f"  💾 Salvato (versione {output_file.stem.split('_')[-1]}): {output_file}")
            else:
                logger.info(f"  💾 Salvato: {output_file}")

        except Exception as e:
            logger.error(f"Errore salvataggio file {output_file}: {e}")

    def _sanitize_filename(self, filename: str) -> str:
        """Pulisce un filename rimuovendo caratteri non validi"""
        if not filename:
            return "untitled"

        # Rimuovi caratteri non validi per filename
        clean = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Rimuovi spazi multipli
        clean = re.sub(r'\s+', ' ', clean).strip()
        # Sostituisci spazi con underscore
        clean = re.sub(r'\s+', '_', clean)
        return clean

    def _prepare_content_text(self, epub_file: Path, content: dict) -> str:
        """Prepara il testo del contenuto da salvare"""
        metadata = content.get('metadata')

        lines = []
        lines.append("=" * 60)
        lines.append("METADATI")
        lines.append("=" * 60)

        if metadata:
            lines.append(f"Titolo: {metadata.title}")
            lines.append(f"Autori: {', '.join(metadata.authors)}")
            lines.append(f"Lingua: {metadata.language}")
            lines.append(f"Editore: {metadata.publisher}")
            lines.append(f"File originale: {epub_file.name}")

        lines.append("")
        lines.append("=" * 60)
        lines.append("CONTENUTO")
        lines.append("=" * 60)
        lines.append("")

        # Scrivi contenuto
        for section_id, text in content.items():
            if section_id not in ['metadata', 'source_file', 'file_hash', 'content_hash']:
                lines.append("=" * 40)
                lines.append(f"SEZIONE: {section_id}")
                lines.append("=" * 40)
                lines.append(text[:500])  # Limita a 500 caratteri per esempio
                lines.append("")

        return '\n'.join(lines)

    def _save_author_report(self, output_dir: Path):
        """Salva un report con tutti gli autori normalizzati"""
        report_file = output_dir / "_AUTHORS_REPORT.txt"

        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("REPORT AUTORI NORMALIZZATI\n")
                f.write("=" * 60 + "\n\n")

                all_authors = self.author_normalizer.get_all_authors()

                for author in all_authors:
                    variants = self.author_normalizer.get_author_variants(author)
                    f.write(f"Canonico: {author}\n")
                    if len(variants) > 1:
                        f.write(f"Varianti ({len(variants)}):\n")
                        for variant in variants:
                            f.write(f"  - {variant}\n")
                    f.write("\n")

                f.write(f"\nTotale autori unici: {len(all_authors)}")

            logger.info(f"📊 Report autori salvato: {report_file}")

        except Exception as e:
            logger.error(f"Errore salvataggio report autori: {e}")

    def _save_conflict_report(self, output_dir: Path):
        """Salva un report sui conflitti gestiti"""
        conflict_stats = self.conflict_manager.get_stats()

        if conflict_stats['total_conflicts'] > 0:
            report_file = output_dir / "_CONFLICT_REPORT.txt"

            try:
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("REPORT CONFLITTI NOMI FILE\n")
                    f.write("=" * 60 + "\n\n")

                    f.write(f"Totale file salvati: {conflict_stats['total_files']}\n")
                    f.write(f"Totale conflitti risolti: {conflict_stats['total_conflicts']}\n")
                    f.write(f"Rapporto conflitti: {conflict_stats['conflict_ratio']:.2%}\n")
                    f.write("\n")

                    # Dettaglio per directory
                    f.write("DETTAGLIO PER DIRECTORY:\n")
                    f.write("-" * 40 + "\n")

                    for dir_path, files in self.conflict_manager.saved_files.items():
                        dir_name = Path(dir_path).name
                        f.write(f"\n{dir_name}:\n")
                        for base_name, count in files.items():
                            if count > 1:
                                f.write(f"  - {base_name}: {count} versioni\n")
                            else:
                                f.write(f"  - {base_name}\n")

                logger.info(f"📊 Report conflitti salvato: {report_file}")

            except Exception as e:
                logger.error(f"Errore salvataggio report conflitti: {e}")

    def search_in_directory(self, root_dir: Path, search_text: str,
                           pattern: str = '*.epub',
                           case_sensitive: bool = False) -> list[dict[str, any]]:
        """
        Cerca testo in tutti gli EPUB di una directory

        Args:
            root_dir: Directory da scansionare
            search_text: Testo da cercare
            pattern: Pattern dei file da cercare
            case_sensitive: Se la ricerca deve essere case-sensitive

        Returns:
            list[dict]: Lista di risultati della ricerca
        """
        all_results = []
        epub_files = self.scan_directory(root_dir, pattern)

        for epub_file in epub_files:
            logger.info(f"Ricerca in: {epub_file.name}")
            try:
                results = self.search_text_in_ebook(epub_file, search_text, case_sensitive)
                all_results.extend(results)
            except Exception as e:
                logger.error(f"Errore ricerca in {epub_file}: {e}")

        return all_results

    def get_author_statistics(self) -> dict[str, any]:
        """
        Restituisce statistiche sugli autori

        Returns:
            dict: Statistiche sugli autori
        """
        all_authors = self.author_normalizer.get_all_authors()

        return {
            'total_unique_authors': len(all_authors),
            'authors': all_authors,
            'variants': {
                author: self.author_normalizer.get_author_variants(author)
                for author in all_authors
            }
        }

    def get_statistics(self) -> dict[str, any]:
        """
        Restituisce statistiche sul processamento

        Returns:
            dict: Statistiche
        """
        return {
            'files_processed': self.files_processed,
            'books_processed': len(self.books_processed),
            'timestamp': datetime.now().isoformat(),
            'authors': self.get_author_statistics(),
            'conflicts': self.conflict_manager.get_stats()
        }


# Esempio di utilizzo e funzione main
def main():
    """Funzione main per testare la classe"""
    # Setup logging
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - %(message)s')

    # Crea il processor
    processor = EbookProcessor(decode_type='lxml', normalize_text=True)

    # Directory di esempio
    root_dir = Path('/home/loreto/filu/ln-eBooks/new_books')  # Cambia con la tua directory
    output_dir = Path('output')  # Directory di output

    # Esempio di scanning e processamento
    if root_dir.exists():
        # Processa tutti gli EPUB nella directory, organizzando per autore
        # skip_duplicates=True salta i file duplicati basati sul contenuto
        results = processor.process_directory(
            root_dir,
            output_dir,
            organize_by_author=True,
            skip_duplicates=True
        )

        # Mostra statistiche sugli autori
        author_stats = processor.get_author_statistics()
        print(f"\n📚 Autori unici trovati: {author_stats['total_unique_authors']}")
        print("Autori:")
        for author in author_stats['authors'][:10]:  # Mostra solo primi 10
            variants = author_stats['variants'][author]
            if len(variants) > 1:
                print(f"  - {author} (varianti: {len(variants)})")
            else:
                print(f"  - {author}")

        # Mostra statistiche conflitti
        stats = processor.get_statistics()
        conflicts = stats['conflicts']
        if conflicts['total_conflicts'] > 0:
            # print(f"\n⚠️  Conflitti risolti: {conflicts['total_conflicts']}")
            logger.info("⚠️  Conflitti risolti: %s", conflicts['total_conflicts'])
            # print(f"   Rapporto conflitti: {conflicts['conflict_ratio']:.2%}")
            logger.info("   Rapporto conflitti: %s", conflicts['conflict_ratio'])

        # Cerca un testo specifico
        search_string="gambe"
        search_results = processor.search_in_directory(root_dir, search_string)
        logger.info("🔍 Trovate %s occorrenze di '%s'", len(search_results), search_string)

        # Mostra statistiche complete
        logger.info("📊 Statistiche: %s", stats)


if __name__ == "__main__":
    main()
