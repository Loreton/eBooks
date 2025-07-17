#! /usr/bin/env python3
# updated by ...: Loreto Notarantonio
# Date .........: 17-07-2025 09.39.00
#

import sys; sys.dont_write_bytecode=True
import os

import os
import zipfile
import re


# ==============================================
# - funzione utile per usarla nei display....
# - ref https://tldp.org/HOWTO/Bash-Prompt-HOWTO/x329.html
# ==============================================
def getColors():
    from types import SimpleNamespace
    colors=SimpleNamespace(
        red        = '\033[0;31m',
        redH       = '\033[1;31m',
        green      = '\033[0;32m',
        greenH     = '\033[1;32m',
        yellow     = '\033[0;33m',
        yellowH    = '\033[1;33m',
        blue       = '\033[0;34m',
        blueH      = '\033[1;34m',
        purple     = '\033[0;35m',
        purpleH    = '\033[1;35m',
        cyan       = '\033[0;36m',
        cyanH      = '\033[1;36m',
        gray       = '\033[0;37m',
        white      = '\033[1;37m',
        reset      = '\033[0m',
    )
    return colors
color=getColors()
HIGHLIGHT_START = color.yellowH # Codice ANSI per grassetto
HIGHLIGHT_END = color.reset # Codice ANSI per reset formattazione




import os
import zipfile
import re
from bs4 import BeautifulSoup # Importa BeautifulSoup

def estrai_metadati_epub(percorso_file_epub):
    """
    Estrae il titolo e l'autore da un file EPUB.
    Cerca il file .opf all'interno dell'archivio EPUB.
    """
    titolo = "Sconosciuto"
    autori = ["Sconosciuto"] # Lista per supportare più autori

    try:
        with zipfile.ZipFile(percorso_file_epub, 'r') as zf:
            opf_file_name = None
            # Cerca il file .opf, spesso si trova nella cartella META-INF/container.xml
            # che punta al .opf, o direttamente nella root o nella cartella OEBPS
            for name in zf.namelist():
                if name.endswith('.opf'):
                    opf_file_name = name
                    break

            # Se non trovato direttamente, prova a leggere container.xml per trovare il .opf
            if not opf_file_name and 'META-INF/container.xml' in zf.namelist():
                with zf.open('META-INF/container.xml', 'r') as container_xml:
                    soup_container = BeautifulSoup(container_xml.read(), 'xml') # Parser XML
                    rootfile = soup_container.find('rootfile')
                    if rootfile and 'full-path' in rootfile.attrs:
                        opf_file_name = rootfile['full-path']

            if opf_file_name:
                with zf.open(opf_file_name, 'r') as opf_xml:
                    soup_opf = BeautifulSoup(opf_xml.read(), 'xml') # Parser XML

                    # Estrai il titolo
                    title_tag = soup_opf.find('dc:title')
                    if title_tag:
                        titolo = title_tag.get_text(strip=True)

                    # Estrai gli autori (dc:creator)
                    creators = soup_opf.find_all('dc:creator')
                    if creators:
                        autori = [creator.get_text(strip=True) for creator in creators]
                    else:
                        autori = ["Sconosciuto"] # Nessun autore trovato

    except zipfile.BadZipFile:
        print(f"Attenzione: '{percorso_file_epub}' non è un file ZIP (o EPUB) valido.")
    except Exception as e:
        print(f"Errore durante l'estrazione dei metadati da '{percorso_file_epub}': {e}")

    return titolo, autori

def cerca_in_epub(percorso_file_epub, stringa_ricerca, ricerca_esatta=True, distanza_parole=5):
    """
    Ricerca una stringa o parole vicine all'interno di un file EPUB.
    Utilizza BeautifulSoup per rimuovere i tag HTML prima della ricerca.

    Args:
        percorso_file_epub (str): Il percorso completo del file EPUB.
        stringa_ricerca (str): La frase o le parole da cercare.
        ricerca_esatta (bool): Se True, cerca la frase esatta. Se False, cerca parole vicine.
        distanza_parole (int): Numero massimo di parole tra le parole cercate (usato solo se ricerca_esatta è False).

    Returns:
        list: Una lista di frasi contenenti la corrispondenza, con le parole evidenziate, o una lista vuota se non trovata.
    """
    trovate = []
    HIGHLIGHT_START = color.yellowH # Codice ANSI per grassetto
    HIGHLIGHT_END = color.reset # Codice ANSI per reset formattazione

    try:
        with zipfile.ZipFile(percorso_file_epub, 'r') as zf:
            for nome_file_interno in zf.namelist():
                # I file con contenuto testuale in EPUB sono spesso .html, .xhtml.
                # Vogliamo anche il file .ncx e .opf per completezza (anche se di solito non contengono testo continuo)
                if nome_file_interno.endswith(('.html', '.xhtml', '.ncx', '.opf', '.xml')):
                    try:
                        with zf.open(nome_file_interno, 'r') as f_interno:
                            contenuto_greggio = f_interno.read()

                            # Decodifica il contenuto per BeautifulSoup
                            contenuto_decodificato = contenuto_greggio.decode('utf-8', errors='ignore')

                            # *** Inizio della pulizia con BeautifulSoup ***
                            soup = BeautifulSoup(contenuto_decodificato, 'html.parser')
                            # Estrai il testo, pulendo i tag
                            testo_pulito = soup.get_text(separator=' ', strip=True)
                            # *** Fine della pulizia ***

                            if ricerca_esatta:
                                # Prepara la stringa per la regex, escapando caratteri speciali e evidenziando
                                escaped_string = re.escape(stringa_ricerca)
                                # Usiamo testo_pulito per la ricerca
                                pattern = re.compile(f"(.{{0,100}})({escaped_string})(.{{0,100}})", re.IGNORECASE | re.DOTALL)

                                for match in pattern.finditer(testo_pulito):
                                    pre_context = match.group(1).strip()
                                    found_phrase = match.group(2)
                                    post_context = match.group(3).strip()

                                    # Evidenzia la frase trovata
                                    evidenziato = f"{HIGHLIGHT_START}{found_phrase}{HIGHLIGHT_END}"

                                    trovate.append(f"...{pre_context} {evidenziato} {post_context}...")
                            else:
                                # Ricerca di parole vicine
                                parole_cercate = stringa_ricerca.split()
                                if len(parole_cercate) < 2:
                                    # Se c'è solo una parola, la ricerca "vicina" è una ricerca esatta di quella parola
                                    escaped_word = re.escape(stringa_ricerca)
                                    pattern = re.compile(f"(.{{0,100}})({escaped_word})(.{{0,100}})", re.IGNORECASE | re.DOTALL)

                                    for match in pattern.finditer(testo_pulito): # Usiamo testo_pulito per la ricerca
                                        pre_context = match.group(1).strip()
                                        found_word = match.group(2)
                                        post_context = match.group(3)

                                        evidenziato = f"{HIGHLIGHT_START}{found_word}{HIGHLIGHT_END}"
                                        trovate.append(f"...{pre_context} {evidenziato} {post_context}...")

                                else:
                                    # Costruisce una regex per parole vicine con evidenziazione
                                    context_pattern_pre = r"(.{0,100})" # 100 caratteri prima
                                    context_pattern_post = r"(.{0,100})" # 100 caratteri dopo

                                    regex_parts = []
                                    for i, parola in enumerate(parole_cercate):
                                        regex_parts.append(f"({re.escape(parola)})") # Ogni parola è un gruppo catturante
                                        if i < len(parole_cercate) - 1:
                                            regex_parts.append(r'(?:[^.!?\n\r]+\s*){0,' + str(distanza_parole) + r'}')

                                    full_regex_str = "".join(regex_parts)
                                    full_pattern = re.compile(f"{context_pattern_pre}{full_regex_str}{context_pattern_post}", re.IGNORECASE | re.DOTALL)

                                    for match in full_pattern.finditer(testo_pulito): # Usiamo testo_pulito per la ricerca
                                        pre_context = match.group(1).strip()

                                        found_and_highlighted = ""
                                        group_index = 2 # Il primo gruppo è pre_context (1), poi iniziano le parole
                                        for i, parola in enumerate(parole_cercate):
                                            found_and_highlighted += f"{HIGHLIGHT_START}{match.group(group_index)}{HIGHLIGHT_END}"
                                            group_index += 1
                                            if i < len(parole_cercate) - 1:
                                                end_of_prev_highlight = match.end(group_index - 1)
                                                start_of_next_highlight = match.start(group_index)
                                                intermediate_text = testo_pulito[end_of_prev_highlight:start_of_next_highlight]
                                                found_and_highlighted += intermediate_text

                                        post_context = match.group(group_index).strip()

                                        trovate.append(f"...{pre_context} {found_and_highlighted} {post_context}...")

                    except Exception as e:
                        print(f"Errore nella lettura o elaborazione del contenuto del file interno in '{percorso_file_epub}': {e}")
    except zipfile.BadZipFile:
        print(f"Attenzione: '{percorso_file_epub}' non è un file ZIP (o EPUB) valido.")
    except Exception as e:
        print(f"Errore durante l'apertura di '{percorso_file_epub}': {e}")
    return trovate

def cerca_file_e_contenuto(cartella_base, stringa_ricerca, ricerca_esatta=True, distanza_parole=5, filtro_autore=None, filtro_titolo=None):
    """
    Cerca file .epub in una cartella e sottocartelle, e poi cerca una stringa al loro interno,
    applicando filtri opzionali per autore e/o titolo.

    Args:
        cartella_base (str): La cartella da cui iniziare la ricerca.
        stringa_ricerca (str): La frase o le parole da cercare.
        ricerca_esatta (bool): Se True, cerca la frase esatta. Se False, cerca parole vicine.
        distanza_parole (int): Numero massimo di parole tra le parole cercate (usato solo se ricerca_esatta è False).
        filtro_autore (str, optional): Stringa parziale per filtrare per autore. Non case-sensitive.
        filtro_titolo (str, optional): Stringa parziale per filtrare per titolo. Non case-sensitive.
    """
    print(f"Ricerca di file EPUB nella cartella: '{cartella_base}'...")
    print(f"Stringa da cercare: '{stringa_ricerca}'")
    print(f"Modalità di ricerca: {'Esatta' if ricerca_esatta else f'Parole vicine (max {distanza_parole} parole di distanza)'}")
    if filtro_autore:
        print(f"Filtro Autore: '{filtro_autore}'")
    if filtro_titolo:
        print(f"Filtro Titolo: '{filtro_titolo}'")
    print("\n")

    trovati_epub = 0
    corrispondenze_totali = 0
    epub_filtrati = 0

    for root, _, files in os.walk(cartella_base):
        for file in files:
            if file.endswith('.epub'):
                trovati_epub += 1
                percorso_completo_epub = os.path.join(root, file)

                # --- Applicazione dei filtri di autore/titolo ---
                titolo_epub, autori_epub = estrai_metadati_epub(percorso_completo_epub)

                match_autore = True
                if filtro_autore:
                    match_autore = False
                    for autore in autori_epub:
                        if filtro_autore.lower() in autore.lower():
                            match_autore = True
                            break

                match_titolo = True
                if filtro_titolo:
                    if filtro_titolo.lower() not in titolo_epub.lower():
                        match_titolo = False

                if not (match_autore and match_titolo):
                    # print(f"  Saltato '{file}' (non corrisponde ai filtri metadati).")
                    continue # Salta questo file se non corrisponde ai filtri

                epub_filtrati += 1
                print(f"Analisi del file: '{percorso_completo_epub}'")
                print(f"  Metadati: Titolo: '{titolo_epub}', Autori: {', '.join(autori_epub)}")

                risultati_ricerca = cerca_in_epub(percorso_completo_epub, stringa_ricerca, ricerca_esatta, distanza_parole)

                if risultati_ricerca:
                    print(f"  --> Corrispondenze trovate in '{file}':")
                    corrispondenze_totali += len(risultati_ricerca)
                    for r in risultati_ricerca:
                        print(f"    - {r}")
                else:
                    print(f"  Nessuna corrispondenza trovata nel contenuto di '{file}'.")

        print("-" * 50) # Separatore tra cartelle

    print(f"\n--- Riepilogo Ricerca ---")
    print(f"File EPUB trovati (totale): {trovati_epub}")
    print(f"File EPUB analizzati (dopo filtri): {epub_filtrati}")
    print(f"Corrispondenze totali trovate nel contenuto: {corrispondenze_totali}")
    if trovati_epub == 0:
        print("Nessun file EPUB trovato nella cartella specificata.")
    elif epub_filtrati == 0:
        print("Nessun file EPUB corrisponde ai filtri di autore/titolo specificati.")

# --- Configurazione e utilizzo ---
if __name__ == "__main__":
    # La cartella da cui iniziare la ricerca (puoi cambiarla)
    cartella_di_partenza = "./" # La cartella corrente. Puoi mettere un percorso assoluto come "C:/Users/TuUtente/Documents/Ebooks"
    cartella_di_partenza = "/home/loreto/ln-eBooks/Ln_Library_prev/authorsLibrary/Vi_Keeland-A5" # La cartella corrente. Puoi mettere un percorso assoluto come "C:/Users/TuUtente/Documents/Ebooks"

    # Stringa da cercare nel contenuto dei libri
    stringa_da_cercare = "Python" # Prova con "Harry Potter" o "Python programming"

    # Modalità di ricerca del contenuto
    # Imposta a True per una ricerca esatta della frase.
    # Imposta a False per cercare parole vicine.
    ricerca_esatta_frase = False
    ricerca_esatta_frase = True

    # Distanza massima tra le parole (solo se ricerca_esatta_frase è False)
    distanza_massima_parole = 10

    # --- Nuovi filtri per autore e/o titolo ---
    # Imposta a None per disabilitare il filtro.
    # Le stringhe sono parziali e non case-sensitive.
    filtro_autore_parziale = "keel" # Es: "Rowling", "Asimov", None
    filtro_titolo_parziale = "Programming" # Es: "Potter", "Foundation", None
    filtro_titolo_parziale = None # Es: "Potter", "Foundation", None

    cerca_file_e_contenuto(
        cartella_di_partenza,
        stringa_da_cercare,
        ricerca_esatta_frase,
        distanza_massima_parole,
        filtro_autore=filtro_autore_parziale,
        filtro_titolo=filtro_titolo_parziale
    )
# --- Configurazione e utilizzo ---

