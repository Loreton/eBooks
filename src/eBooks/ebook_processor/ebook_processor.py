# ebook_processor/ebook_processor.py (parte modificata)
"""
Main Ebook Processor class
"""

import sys
sys.dont_write_bytecode = True
import re
import hashlib
from pathlib import Path
from datetime import datetime

import ebooklib
from ebooklib import epub
import bs4

from .models import EbookMetadata
from .author_normalizer import AuthorNormalizer
from .conflict_manager import FileConflictManager
from .filename_cleaner import FilenameCleaner  # <-- Nuovo import

# Setup logger per la classe
from pyLnLib.logger import get_logger
# from pyLnLib import get_colors, get_logger
# C=get_colors()


class EbookProcessor:
    """
    Classe per processare ebook EPUB con funzionalità di:
    - Estrazione metadati
    - Estrazione testo pulito
    - Ricerca di testo nei libri
    - Scanning di directory
    - Organizzazione per autore
    - Gestione conflitti di nome
    - Pulizia nomi file
    """

    def __init__(self, decode_type: str = 'lxml',
                normalize_text: bool = True,
                clean_filenames: bool = False,
                remove_authors_from_filename: bool = False):
        """
        Inizializza il processor per ebook

        Args:
            decode_type: Tipo di parser per BeautifulSoup ('lxml' o 'html.parser')
            normalize_text: normalizzare il testo (rimuovere spazi multipli, etc.)
            clean_filenames: pulire i nomi dei file rimuovendo pattern indesiderati
            remove_authors_from_filename: rimuovere gli autori dal nome del file
        """
        self.logger=get_logger()
        self.decode_type = decode_type
        self.normalize_text = normalize_text
        self.clean_filenames = clean_filenames
        self.remove_authors_from_filename = remove_authors_from_filename
        self.files_processed = 0
        self.books_processed: dict[str, dict] = {}
        self.author_normalizer = AuthorNormalizer()
        self.conflict_manager = FileConflictManager()

        # Cleaner per nomi file
        self.filename_cleaner = FilenameCleaner()
        # if clean_filenames:
        #     self.filename_cleaner = FilenameCleaner()
        # else:
        #     self.filename_cleaner = None

        # Setup per lxml warnings
        if decode_type == 'lxml':
            import warnings
            warnings.filterwarnings("ignore", category=bs4.XMLParsedAsHTMLWarning)

    def _sanitize_filename(self, filename: str) -> str:
        """
        Pulisce un filename rimuovendo caratteri non validi

        Se clean_filenames è attivo, applica anche la pulizia avanzata
        """
        if not filename:
            return "untitled"

        # Se la pulizia è attiva, usa il cleaner avanzato
        if self.clean_filenames:
            return self.filename_cleaner.clean_filename(filename, remove_authors=self.remove_authors_from_filename )

        # Altrimenti pulizia base
        clean = re.sub(r'[<>:"/\\|?*]', '_', filename)
        clean = re.sub(r'\s+', ' ', clean).strip()
        clean = re.sub(r'\s+', '_', clean)
        return clean


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
            self.logger.warning("Error extracting title: %s", e)

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
            self.logger.warning("Error extracting authors: %s", e)

        # Estrai lingua
        try:
            languages = book.get_metadata('DC', 'language')
            if languages:
                metadata.language = self._get_first_item(languages)
        except Exception as e:
            self.logger.warning("Error extracting language: %s", e)
            pass

        # Estrai editore
        try:
            publishers = book.get_metadata('DC', 'publisher')
            if publishers:
                metadata.publisher = self._get_first_item(publishers)
        except Exception as e:
            self.logger.warning("Error extracting publisher: %s", e)
            pass

        return metadata

    def _get_first_item(self, value) -> str:
        """Helper per estrarre il primo item da una struttura dati"""
        if not value:
            return "Sconosciuto"
        if isinstance(value, (list, tuple)):
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
            self.logger.error(f"File non trovato: {epub_file}")
            return {}

        try:
            book = epub.read_epub(str(epub_file))
        except Exception as e:
            self.logger.error(f"Errore apertura file {epub_file}: {e}")
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
                    self.logger.warning(f"Errore processamento item: {e}")

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
            self.logger.error(f"File non trovato: {epub_file}")
            return results

        try:
            book = epub.read_epub(str(epub_file))
            metadata = self.extract_metadata(book)
        except Exception as e:
            self.logger.error(f"Errore apertura file {epub_file}: {e}")
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
                    self.logger.warning(f"Errore ricerca in item: {e}")

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
            self.logger.error(f"Directory non trovata: {root_path}")
            return []

        if recursive:
            file_list = list(root_path.glob(f'**/{pattern}'))
        else:
            file_list = list(root_path.glob(pattern))

        self.logger.info(f"Trovati {len(file_list)} file {pattern} in {root_path}")
        return file_list

    def process_directory(self, root_dir: Path,
                                output_dir: Path | None = None,
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
            # self.logger.info(f"[{i}/{len(epub_files)}] Processando: {epub_file.name}")
            self.logger.info("[%s/%s] Processing: %s", i, len(epub_files), epub_file.name)

            try:
                content = self.extract_text_from_epub(epub_file)
                if not content:
                    self.logger.warning("Nessun contenuto estratto da %s", epub_file.name)
                    continue

                # Verifica duplicati basati sul contenuto
                if skip_duplicates:
                    content_hash = content.get('content_hash')
                    if content_hash and content_hash in processed_hashes:
                        self.logger.info("  ⏭️  Skipping duplicated: %s", epub_file.name)
                        continue
                    if content_hash:
                        processed_hashes.add(content_hash)

                results[str(epub_file)] = content
                self.files_processed += 1

                # Salva se richiesto
                if output_dir:
                    self._save_book_content(epub_file, content, output_dir, organize_by_author)

            except Exception as e:
                self.logger.error("Error processing %s: %s", epub_file, e)

        # Salva il report degli autori e dei conflitti
        if output_dir:
            self._save_author_report(output_dir)
            self._save_conflict_report(output_dir)

        self.logger.info(f"Processati {self.files_processed} file con successo")
        return results

    def _save_book_content(self, epub_file: Path, content: dict, output_dir: Path, organize_by_author: bool = True):
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

        if self.clean_filenames:
            cleaned_filename = self.filename_cleaner.clean_filename(filename=str(epub_file.stem))
        else:
            cleaned_filename = epub_file.stem

        metadata = content.get('metadata')
        primary_author = metadata.authors[0]

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
        self.logger.info("cleaned filename: %s", base_filename)

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
        output_file = self.conflict_manager.get_unique_filename( target_dir, base_filename, '.txt' )

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
                # self.logger.info(f"  💾 Salvato (versione {output_file.stem.split('_')[-1]}): {output_file}")
                self.logger.info("Salvato:\nauthor: %s\ntitle: %s\nfile: %s", primary_author, cleaned_filename, output_file)
            else:
                self.logger.info(f"  💾 Salvato: {output_file}")

        except Exception as e:
            self.logger.error(f"Errore salvataggio file {output_file}: {e}")


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

            self.logger.info(f"📊 Report autori salvato: {report_file}")

        except Exception as e:
            self.logger.error(f"Errore salvataggio report autori: {e}")

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

                self.logger.info(f"📊 Report conflitti salvato: {report_file}")

            except Exception as e:
                self.logger.error(f"Errore salvataggio report conflitti: {e}")

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
            self.logger.info(f"Ricerca in: {epub_file.name}")
            try:
                results = self.search_text_in_ebook(epub_file, search_text, case_sensitive)
                all_results.extend(results)
            except Exception as e:
                self.logger.error(f"Errore ricerca in {epub_file}: {e}")

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

    def reset(self):
        """Resetta lo stato del processor"""
        self.files_processed = 0
        self.books_processed.clear()
        self.author_normalizer = AuthorNormalizer()
        self.conflict_manager.reset()
