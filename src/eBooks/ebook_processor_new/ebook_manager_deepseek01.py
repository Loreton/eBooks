from modulefinder import test
import os
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Optional, List, Any
from datetime import datetime
from ebooklib import epub
import html
from bs4 import BeautifulSoup
import warnings

class EpubProcessor:
    """Classe per processare file EPUB utilizzando ebooklib e BeautifulSoup con lxml."""

    # Costanti per i tipi di item EPUB
    ITEM_DOCUMENT = 9  # Documento XHTML
    ITEM_COVER = 1     # Copertina
    ITEM_IMAGE = 3     # Immagine

    def __init__(self, filepath: str, use_lxml: bool = True):
        """
        Inizializza il processore EPUB.

        Args:
            filepath: Percorso del file EPUB
            use_lxml: Se True, usa lxml come parser per BeautifulSoup (più robusto)
        Raises:
            FileNotFoundError: Se il file non esiste
            ValueError: Se il file non è un EPUB valido
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File non trovato: {filepath}")

        if not filepath.lower().endswith('.epub'):
            raise ValueError(f"Il file non è un EPUB: {filepath}")

        self.filepath = filepath
        self.use_lxml = use_lxml
        self._parser = 'lxml' if use_lxml else 'html.parser'

        # Setup per lxml warnings (solo se disponibile)
        if use_lxml:
            try:
                # Prova a sopprimere il warning in modo generico
                warnings.filterwarnings("ignore", category=UserWarning, module='bs4')
                # Per versioni più recenti di BeautifulSoup
                if hasattr(BeautifulSoup, 'XMLParsedAsHTMLWarning'):
                    warnings.filterwarnings("ignore", category=BeautifulSoup.XMLParsedAsHTMLWarning)
            except:
                pass

        self._book = None
        self._metadata = None
        self._text = None
        self._title = None
        self._author = None
        self._opf_metadata = None
        self._load_book()
        self._read_opf_metadata()

    def _load_book(self) -> None:
        """Carica il libro EPUB."""
        try:
            self._book = epub.read_epub(self.filepath)
        except Exception as e:
            raise ValueError(f"Errore nel caricamento dell'EPUB: {e}")

    def _read_opf_metadata(self) -> None:
        """
        Legge i metadati direttamente dal file OPF dell'EPUB.
        Usa lxml per un parsing più robusto se disponibile.
        """
        try:
            with zipfile.ZipFile(self.filepath, 'r') as epub_zip:
                # Leggi il file container.xml per trovare il percorso dell'OPF
                container_xml = epub_zip.read('META-INF/container.xml')

                # Usa lxml per il parsing se disponibile
                try:
                    from lxml import etree
                    container = etree.fromstring(container_xml)
                    ns = {'ocf': 'urn:oasis:names:tc:opendocument:xmlns:container'}
                    rootfile = container.find('.//ocf:rootfile', ns)
                except:
                    container = ET.fromstring(container_xml)
                    ns = {'ocf': 'urn:oasis:names:tc:opendocument:xmlns:container'}
                    rootfile = container.find('.//ocf:rootfile', ns)

                if rootfile is not None:
                    opf_path = rootfile.get('full-path')

                    # Leggi il file OPF
                    opf_content = epub_zip.read(opf_path)

                    # Usa lxml per il parsing se disponibile
                    try:
                        from lxml import etree
                        opf = etree.fromstring(opf_content)
                        # Namespace per OPF
                        ns_opf = {
                            'opf': 'http://www.idpf.org/2007/opf',
                            'dc': 'http://purl.org/dc/elements/1.1/',
                            'dcterms': 'http://purl.org/dc/terms/',
                            'calibre': 'http://calibre.kovidgoyal.net/2009/metadata'
                        }
                    except:
                        opf = ET.fromstring(opf_content)
                        ns_opf = {
                            'opf': 'http://www.idpf.org/2007/opf',
                            'dc': 'http://purl.org/dc/elements/1.1/',
                            'dcterms': 'http://purl.org/dc/terms/',
                            'calibre': 'http://calibre.kovidgoyal.net/2009/metadata'
                        }

                    # Estrai metadati
                    metadata = {}

                    # Cerca tutti gli elementi DC
                    for ns_prefix, ns_url in [('dc', 'http://purl.org/dc/elements/1.1/'),
                                              ('dcterms', 'http://purl.org/dc/terms/')]:
                        # Usa XPath per trovare tutti gli elementi
                        try:
                            from lxml import etree
                            elements = opf.xpath(f'.//{{{ns_url}}}*', namespaces=ns_opf)
                        except:
                            elements = opf.findall(f'.//{{{ns_url}}}*')

                        for element in elements:
                            tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
                            text = element.text.strip() if element.text else ''

                            if tag == 'title':
                                metadata['title'] = text
                            elif tag == 'creator':
                                metadata['creator'] = text
                            elif tag == 'language':
                                metadata['language'] = text
                            elif tag == 'publisher':
                                metadata['publisher'] = text
                            elif tag == 'description':
                                metadata['description'] = text
                            elif tag == 'identifier':
                                metadata['identifier'] = text
                            elif tag == 'date':
                                metadata['date'] = text
                            elif tag == 'subject':
                                if 'subject' not in metadata:
                                    metadata['subject'] = []
                                if isinstance(metadata['subject'], list):
                                    metadata['subject'].append(text)
                                else:
                                    metadata['subject'] = [metadata['subject'], text]
                            elif tag == 'contributor':
                                if 'contributor' not in metadata:
                                    metadata['contributor'] = []
                                if isinstance(metadata['contributor'], list):
                                    metadata['contributor'].append(text)
                                else:
                                    metadata['contributor'] = [metadata['contributor'], text]
                            elif tag == 'rights':
                                metadata['rights'] = text

                    # Cerca metadati OPF aggiuntivi (meta tag)
                    try:
                        from lxml import etree
                        meta_elements = opf.xpath('.//opf:meta', namespaces=ns_opf)
                    except:
                        meta_elements = opf.findall('.//opf:meta', ns_opf)

                    for element in meta_elements:
                        name = element.get('name')
                        content = element.get('content')
                        if name and content:
                            metadata[name] = content
                        # Cerca anche attributi 'property'
                        prop = element.get('property')
                        if prop and content:
                            metadata[prop] = content
                        # Cerca 'http://purl.org/dc/terms/' con 'title'
                        if '}' in element.tag and 'title' in element.tag:
                            if element.text and 'title' not in metadata:
                                metadata['title'] = element.text.strip()

                    # Se il titolo contiene l'autore, separali
                    if 'title' in metadata and metadata['title']:
                        title = metadata['title']
                        # Cerca pattern "Autore - Titolo" o "Titolo / Autore"
                        patterns = [
                            (r'^(.+?)\s*[-–—]\s*(.+)$', 1, 2),  # "Autore - Titolo"
                            (r'^(.+?)\s*[/]\s*(.+)$', 1, 2),    # "Autore / Titolo"
                            (r'^(.+?)\s*[|]\s*(.+)$', 1, 2),    # "Autore | Titolo"
                            (r'^([^,]+),\s*(.+)$', 2, 1),       # "Cognome, Nome - Titolo"
                        ]

                        for pattern, author_idx, title_idx in patterns:
                            match = re.match(pattern, title)
                            if match:
                                potential_author = match.group(author_idx).strip()
                                potential_title = match.group(title_idx).strip()
                                # Verifica che l'autore abbia almeno 2 parole o contenga una virgola
                                if len(potential_author.split()) >= 2 or ',' in potential_author:
                                    if 'creator' not in metadata or not metadata['creator']:
                                        metadata['creator'] = potential_author
                                    metadata['title'] = potential_title
                                    break

                    self._opf_metadata = metadata

        except Exception as e:
            print(f"Errore nella lettura dell'OPF: {e}")
            self._opf_metadata = {}

    def _clean_title(self, title: str) -> str:
        """Pulisce il titolo rimuovendo spazi multipli e caratteri strani."""
        if not title:
            return title
        # Rimuovi spazi multipli
        title = ' '.join(title.split())
        # Rimuovi caratteri di controllo
        title = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', title)
        return title.strip()

    def extract_metadata(self) -> Dict[str, Any]:
        """
        Estrae i metadati dal file EPUB.
        Combina i metadati da ebooklib e quelli letti direttamente dall'OPF.

        Returns:
            Dizionario con i metadati del libro
        """
        if self._metadata is not None:
            return self._metadata

        if self._book is None:
            self._load_book()

        metadata = {}

        # Prima prendi i metadati dall'OPF (più affidabili)
        if self._opf_metadata:
            metadata.update(self._opf_metadata)

        # Poi integra con quelli di ebooklib (se mancano)
        try:
            # Estrai metadati Dublin Core da ebooklib
            dc_fields = ['title', 'creator', 'language', 'publisher', 'date',
                        'description', 'identifier', 'contributor', 'coverage',
                        'format', 'relation', 'rights', 'source', 'subject', 'type']

            for field in dc_fields:
                if field not in metadata or not metadata[field]:
                    key = f'DC:{field}'
                    if key in self._book.metadata:
                        values = self._book.metadata[key]
                        if values:
                            value = values[0][0] if values else None
                            if value:
                                if field == 'date' and value:
                                    try:
                                        for fmt in ['%Y-%m-%d', '%Y-%m', '%Y']:
                                            try:
                                                metadata[field] = datetime.strptime(value, fmt).date()
                                                break
                                            except:
                                                continue
                                        if field not in metadata:
                                            metadata[field] = value
                                    except:
                                        metadata[field] = value
                                else:
                                    metadata[field] = value

            # Aggiungi metadati OPF aggiuntivi (non DC)
            for key, values in self._book.metadata.items():
                if not key.startswith('DC:'):
                    if key not in metadata:
                        if values:
                            if len(values) == 1:
                                metadata[key] = values[0][0]
                            else:
                                metadata[key] = [v[0] for v in values if v[0]]

        except Exception as e:
            print(f"Errore durante l'estrazione dei metadati da ebooklib: {e}")

        # Se ancora non abbiamo il titolo, usa il nome del file
        if 'title' not in metadata or not metadata['title']:
            filename = os.path.basename(self.filepath)
            filename = os.path.splitext(filename)[0]
            filename = filename.replace('_', ' ').replace('-', ' ')
            filename = re.sub(r'\s+', ' ', filename).strip()

            # Prova a estrarre autore e titolo dal nome del file
            if ' - ' in filename:
                parts = filename.split(' - ', 1)
                if len(parts) == 2:
                    if 'creator' not in metadata or not metadata['creator']:
                        if len(parts[0].split()) >= 2:  # Probabilmente un nome
                            metadata['creator'] = parts[0].strip()
                    metadata['title'] = parts[1].strip()
                else:
                    metadata['title'] = filename
            else:
                metadata['title'] = filename

        # Pulisci il titolo
        if 'title' in metadata and metadata['title']:
            metadata['title'] = self._clean_title(metadata['title'])
            # Rimuovi (2014) o altri anni dal titolo
            metadata['title'] = re.sub(r'\s*\(\d{4}\)\s*$', '', metadata['title'])
            # Rimuovi " (La trilogia dei sensi 01)" o simili
            metadata['title'] = re.sub(r'\s*\([^)]*\)\s*', ' ', metadata['title']).strip()

        # Imposta valori di default
        if 'creator' not in metadata or not metadata['creator']:
            metadata['creator'] = 'Autore sconosciuto'
        if 'language' not in metadata or not metadata['language']:
            metadata['language'] = 'it'
        if 'publisher' not in metadata or not metadata['publisher']:
            metadata['publisher'] = 'Sconosciuto'
        if 'description' not in metadata or not metadata['description']:
            metadata['description'] = 'Nessuna descrizione'

        # Se abbiamo una lista di subject, uniscili
        if 'subject' in metadata and isinstance(metadata['subject'], list):
            metadata['subject'] = ', '.join(metadata['subject'])

        self._metadata = metadata

        return self._metadata

    def extract_text(self, clean: bool = True) -> str:
        """
        Estrae il testo completo dal file EPUB.

        Args:
            clean: Se True, pulisce il testo rimuovendo spazi multipli e formattazione

        Returns:
            Testo completo del libro
        """
        if self._text is not None:
            return self._text

        if self._book is None:
            self._load_book()

        text_parts = []

        try:
            # Itera su tutti gli items del libro
            for item in self._book.get_items():
                # Usa il tipo corretto per documenti
                if item.get_type() == self.ITEM_DOCUMENT:
                    # Decodifica il contenuto
                    content = item.get_body_content()
                    if content:
                        try:
                            # Decodifica in UTF-8
                            content_str = content.decode('utf-8', errors='ignore')
                            # Estrai testo con BeautifulSoup usando il parser specificato
                            soup = BeautifulSoup(content_str, self._parser)

                            # Rimuovi script e style
                            for script in soup(['script', 'style']):
                                script.decompose()

                            # Estrai testo
                            text = soup.get_text(separator=' ', strip=True)

                            if clean:
                                # Pulisci il testo
                                text = ' '.join(text.split())  # Rimuovi spazi multipli
                                text = html.unescape(text)    # Decodifica entità HTML

                            if text.strip():
                                text_parts.append(text.strip())

                        except Exception as e:
                            print(f"Errore nel processare l'item: {e}")

            # Unisci tutte le parti
            self._text = '\n\n'.join(text_parts)

            if clean:
                # Pulizia finale
                self._text = ' '.join(self._text.split())

        except Exception as e:
            print(f"Errore durante l'estrazione del testo: {e}")
            self._text = ""

        return self._text

    def extract_text_by_chapter(self) -> List[Dict[str, str]]:
        """
        Estrae il testo suddiviso per capitoli.

        Returns:
            Lista di dizionari con titolo e contenuto di ogni capitolo
        """
        if self._book is None:
            self._load_book()

        chapters = []

        try:
            # Cerca tutti gli item di tipo documento
            for item in self._book.get_items():
                if item.get_type() == self.ITEM_DOCUMENT:
                    content = item.get_body_content()
                    if content:
                        try:
                            content_str = content.decode('utf-8', errors='ignore')
                            soup = BeautifulSoup(content_str, self._parser)

                            # Rimuovi script e style
                            for script in soup(['script', 'style']):
                                script.decompose()

                            # Cerca di identificare il titolo del capitolo
                            title = None
                            # Cerca il primo h1, h2, h3 o titolo
                            for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                                header = soup.find(tag)
                                if header:
                                    title = header.get_text(strip=True)
                                    # Rimuovi l'header dal testo
                                    header.decompose()
                                    break

                            # Se non trovato, cerca un titolo in un paragrafo con classe 'title'
                            if not title:
                                title_elem = soup.find('p', class_='title')
                                if title_elem:
                                    title = title_elem.get_text(strip=True)
                                    title_elem.decompose()

                            # Se ancora non trovato, usa il nome del file
                            if not title:
                                # Usa il nome del file senza percorso
                                name = item.get_name() or f"Capitolo {len(chapters) + 1}"
                                # Pulisci il nome
                                if '/' in name:
                                    name = name.split('/')[-1]
                                if '.' in name:
                                    name = name.split('.')[0]
                                # Rimuovi prefissi numerici comuni
                                name = re.sub(r'^[0-9]+[_\-]', '', name)
                                name = name.replace('_', ' ').replace('-', ' ')
                                # Cerca parole chiave per titoli
                                if 'prologo' in name.lower():
                                    title = 'Prologo'
                                elif 'epilogo' in name.lower():
                                    title = 'Epilogo'
                                elif 'capitolo' in name.lower():
                                    # Cerca il numero del capitolo
                                    match = re.search(r'capitolo\s*([0-9]+)', name, re.IGNORECASE)
                                    if match:
                                        title = f'Capitolo {match.group(1)}'
                                    else:
                                        title = name
                                else:
                                    title = name

                            # Estrai il testo
                            text = soup.get_text(separator=' ', strip=True)
                            text = ' '.join(text.split())  # Pulisci

                            if text.strip():
                                chapters.append({
                                    'title': html.unescape(title),
                                    'content': html.unescape(text)
                                })

                        except Exception as e:
                            print(f"Errore nel processare il capitolo: {e}")

        except Exception as e:
            print(f"Errore durante l'estrazione dei capitoli: {e}")

        return chapters

    def get_title(self) -> str:
        """
        Ottiene il titolo del libro.

        Returns:
            Titolo del libro
        """
        if self._title is not None:
            return self._title

        metadata = self.extract_metadata()
        self._title = metadata.get('title', 'Titolo sconosciuto')
        return self._title

    def get_author(self) -> str:
        """
        Ottiene l'autore del libro.

        Returns:
            Autore del libro
        """
        if self._author is not None:
            return self._author

        metadata = self.extract_metadata()
        self._author = metadata.get('creator', 'Autore sconosciuto')
        return self._author

    def get_language(self) -> str:
        """
        Ottiene la lingua del libro.

        Returns:
            Lingua del libro
        """
        metadata = self.extract_metadata()
        lang = metadata.get('language', 'it')
        # Mappa codici lingua comuni
        lang_map = {
            'es': 'Spagnolo',
            'en': 'Inglese',
            'it': 'Italiano',
            'fr': 'Francese',
            'de': 'Tedesco',
            'pt': 'Portoghese',
            'ru': 'Russo',
            'zh': 'Cinese',
            'ja': 'Giapponese'
        }
        return lang_map.get(lang, lang)

    def get_publisher(self) -> str:
        """
        Ottiene l'editore del libro.

        Returns:
            Editore del libro
        """
        metadata = self.extract_metadata()
        return metadata.get('publisher', 'Sconosciuto')

    def get_description(self) -> str:
        """
        Ottiene la descrizione del libro.

        Returns:
            Descrizione del libro
        """
        metadata = self.extract_metadata()
        return metadata.get('description', 'Nessuna descrizione')

    def get_publication_date(self) -> Optional[datetime]:
        """
        Ottiene la data di pubblicazione del libro.

        Returns:
            Data di pubblicazione o None se non disponibile
        """
        metadata = self.extract_metadata()
        date_val = metadata.get('date')
        if date_val and isinstance(date_val, str):
            try:
                for fmt in ['%Y-%m-%d', '%Y-%m', '%Y']:
                    try:
                        return datetime.strptime(date_val, fmt)
                    except:
                        continue
            except:
                pass
        elif date_val and isinstance(date_val, datetime):
            return date_val
        return None

    def get_cover(self) -> Optional[bytes]:
        """
        Ottiene l'immagine di copertina.

        Returns:
            Dati binari dell'immagine di copertina o None se non disponibile
        """
        if self._book is None:
            self._load_book()

        try:
            # Cerca l'item di copertina usando il tipo corretto
            for item in self._book.get_items():
                if item.get_type() == self.ITEM_COVER:
                    return item.get_content()

                # Alcuni EPUB hanno la copertina come ITEM_IMAGE (3)
                if item.get_type() == self.ITEM_IMAGE:
                    # Controlla se il nome contiene "cover"
                    name = item.get_name() or ""
                    if 'cover' in name.lower():
                        return item.get_content()
        except Exception as e:
            print(f"Errore durante l'estrazione della copertina: {e}")

        return None

    def get_author_list(self) -> List[str]:
        """
        Ottiene la lista degli autori.

        Returns:
            Lista degli autori
        """
        metadata = self.extract_metadata()
        creators = metadata.get('creator', '')
        if isinstance(creators, str):
            # Gestisci "Miller, Raine" -> "Raine Miller"
            if ', ' in creators:
                parts = creators.split(', ', 1)
                if len(parts) == 2:
                    return [f"{parts[1]} {parts[0]}".strip()]
            # Gestisci "Raine Miller" -> ["Raine Miller"]
            return [creators.strip()]
        return []

    def get_info(self) -> Dict[str, Any]:
        """
        Ottiene tutte le informazioni principali del libro.

        Returns:
            Dizionario con tutte le informazioni disponibili
        """
        metadata = self.extract_metadata()

        info = {
            'titolo': self.get_title(),
            'autore': self.get_author(),
            'autori': self.get_author_list(),
            'lingua': self.get_language(),
            'editore': self.get_publisher(),
            'descrizione': self.get_description(),
            'data_pubblicazione': self.get_publication_date(),
            'identificatore': metadata.get('identifier'),
            'soggetto': metadata.get('subject'),
            'diritti': metadata.get('rights'),
            'percorso_file': self.filepath,
            'dimensione_file': os.path.getsize(self.filepath) if os.path.exists(self.filepath) else 0
        }

        # Aggiungi metadati extra
        extra_metadata = {k: v for k, v in metadata.items()
                         if k not in info and k not in ['title', 'creator', 'language',
                                                       'publisher', 'description', 'date',
                                                       'identifier', 'subject', 'rights']}
        if extra_metadata:
            info['metadata_extra'] = extra_metadata

        return info

    def get_statistics(self) -> Dict[str, Any]:
        """
        Ottiene statistiche sul libro.

        Returns:
            Dizionario con statistiche (parole, caratteri, capitoli, ecc.)
        """
        text = self.extract_text(clean=True)
        chapters = self.extract_text_by_chapter()

        # Pulisci il testo per contare parole
        words = [word for word in text.split() if len(word) > 0]

        stats = {
            'caratteri_totali': len(text),
            'parole_totali': len(words),
            'capitoli_totali': len(chapters),
            'parole_per_capitolo': [],
            'dimensione_file': os.path.getsize(self.filepath) if os.path.exists(self.filepath) else 0
        }

        for chapter in chapters:
            words_count = len(chapter['content'].split())
            stats['parole_per_capitolo'].append({
                'titolo': chapter['title'],
                'parole': words_count
            })

        return stats

    def save_cover(self, output_path: str) -> bool:
        """
        Salva la copertina su disco.

        Args:
            output_path: Percorso dove salvare l'immagine

        Returns:
            True se salvato con successo, False altrimenti
        """
        cover_data = self.get_cover()
        if cover_data:
            try:
                with open(output_path, 'wb') as f:
                    f.write(cover_data)
                return True
            except Exception as e:
                print(f"Errore nel salvare la copertina: {e}")
                return False
        return False

    def get_chapters_titles(self) -> List[str]:
        """
        Ottiene i titoli di tutti i capitoli.

        Returns:
            Lista dei titoli dei capitoli
        """
        chapters = self.extract_text_by_chapter()
        return [ch['title'] for ch in chapters]

    def get_toc(self) -> List[Dict[str, Any]]:
        """
        Ottiene il sommario (TOC) del libro.

        Returns:
            Lista di dizionari con titolo e riferimento di ogni voce del sommario
        """
        if self._book is None:
            self._load_book()

        toc = []

        try:
            # Il TOC è accessibile via self._book.toc
            def process_toc_item(item, level=0):
                if isinstance(item, tuple):
                    # È una sezione con sottovoci
                    if len(item) >= 2:
                        title, children = item[0], item[1]
                        # Estrai il titolo in modo robusto
                        if hasattr(title, 'title'):
                            title_text = title.title
                        else:
                            title_text = str(title)
                        toc.append({
                            'title': html.unescape(title_text),
                            'level': level,
                            'children': len(children) if children else 0,
                            'is_section': True
                        })
                        if children:
                            for child in children:
                                process_toc_item(child, level + 1)
                elif hasattr(item, 'title') and hasattr(item, 'href'):
                    # È un Link object
                    toc.append({
                        'title': html.unescape(item.title),
                        'href': item.href,
                        'level': level,
                        'is_section': False
                    })
                elif isinstance(item, (str, bytes)):
                    # È una stringa
                    try:
                        title = item.decode('utf-8') if isinstance(item, bytes) else str(item)
                        toc.append({
                            'title': html.unescape(title),
                            'level': level,
                            'is_section': False
                        })
                    except:
                        pass
                else:
                    # Prova a convertire in stringa
                    try:
                        toc.append({
                            'title': html.unescape(str(item)),
                            'level': level,
                            'is_section': False
                        })
                    except:
                        pass

            # Processa il TOC
            if self._book.toc:
                for item in self._book.toc:
                    process_toc_item(item)

        except Exception as e:
            print(f"Errore nell'estrazione del TOC: {e}")

        return toc

    def __str__(self) -> str:
        """Rappresentazione stringa del processore EPUB."""
        return f"EpubProcessor('{self.filepath}')"

    def __repr__(self) -> str:
        """Rappresentazione di debug del processore EPUB."""
        return f"EpubProcessor(filepath='{self.filepath}')"


# Esempio di utilizzo
def rapid_single_epub(epub_file):
    processor = EpubProcessor(epub_file)

    # Informazioni base
    print(f"Titolo: {processor.get_title()}")
    print(f"Autore: {processor.get_author()}")
    print(f"Editore: {processor.get_publisher()}")
    print(f"Lingua: {processor.get_language()}")

    # Tutte le info in un colpo
    info = processor.get_info()
    print(info)

    # Estrai testo
    testo = processor.extract_text()
    print(testo[:1000])

    # Salva copertina
    processor.save_cover("copertina.jpg")

def single_epub(epub_file):
    try:
        # epub_file = "/home/loreto/filu/ln-eBooks/new_books/single_test_book/Raine Miller - Nudo D'autore (2014).epub"

        # Usa lxml se disponibile, altrimenti html.parser
        processor = EpubProcessor(epub_file, use_lxml=True)

        # Estrai e mostra i metadati
        print("=== METADATI ===")
        metadata = processor.extract_metadata()
        for key, value in metadata.items():
            if value is not None:
                print(f"{key}: {value}")

        print("\n=== INFORMAZIONI PRINCIPALI ===")
        info = processor.get_info()
        for key, value in info.items():
            if value is not None:
                print(f"{key}: {value}")

        print(f"\nTitolo: {processor.get_title()}")
        print(f"Autore: {processor.get_author()}")
        print(f"Lingua: {processor.get_language()}")

        # Estrai il TOC
        print("\n=== SOMMARIO (TOC) ===")
        toc = processor.get_toc()
        if toc:
            for item in toc[:15]:
                indent = "  " * item['level']
                print(f"{indent}• {item['title']}")
        else:
            print("Nessun TOC trovato")

        # Estrai i capitoli
        print("\n=== PRIMI CAPITOLI ===")
        chapters = processor.extract_text_by_chapter()
        if chapters:
            for i, chapter in enumerate(chapters[:10]):
                word_count = len(chapter['content'].split())
                print(f"{i+1}. {chapter['title']} ({word_count} parole)")
        else:
            print("Nessun capitolo trovato")

        # Estrai e mostra un'anteprima del testo
        print("\n=== ANTEPRIMA TESTO ===")
        text = processor.extract_text()
        if text:
            preview = text[:500] + "..." if len(text) > 500 else text
            print(preview)
        else:
            print("Nessun testo estratto")

        # Statistiche
        print("\n=== STATISTICHE ===")
        stats = processor.get_statistics()
        print(f"Parole totali: {stats['parole_totali']}")
        print(f"Capitoli totali: {stats['capitoli_totali']}")
        print(f"Caratteri totali: {stats['caratteri_totali']}")

        # Salva la copertina se disponibile
        if processor.save_cover("copertina.jpg"):
            print("\nCopertina salvata come 'copertina.jpg'")
        else:
            print("\nNessuna copertina trovata")

    except Exception as e:
        print(f"Errore: {e}")
        import traceback
        traceback.print_exc()













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







# Esempio di utilizzo
if __name__ == "__main__":
    f_scan = False

    if f_scan:
        libri = scan_and_process("/home/loreto/filu/ln-eBooks/new_books")
        print(f"\nTrovati {len(libri)} libri EPUB")
    else:
        # single_epub("/home/loreto/filu/ln-eBooks/new_books/single_test_book/Raine Miller - Nudo D'autore (2014).epub")
        rapid_single_epub("/home/loreto/filu/ln-eBooks/new_books/single_test_book/Raine Miller - Nudo D'autore (2014).epub")
