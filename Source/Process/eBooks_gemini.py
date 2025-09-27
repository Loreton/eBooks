#! /usr/bin/env python3
# updated by ...: Loreto Notarantonio
# Date .........: 22-09-2025 09.07.09
#

import sys; sys.dont_write_bytecode=True
import os
import re

from pathlib import Path

from html.parser import HTMLParser
# from htmlfilter import HTMLFilter  ### pip install htmlfilter  https://pypi.org/project/htmlfilter/


import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup








##############################################################
# read one book and save it to txt file
##############################################################
def read_epub(gVars: dict, filein: str, fileout: str=None):
    global gv
    gv=gVars

    book = epub.read_epub(filein)
    content = ""

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            bodyContent = item.get_body_content().decode()
            f = HTMLFilter()
            f.feed(bodyContent)
            content += f.text

    if fileOut:
        with open(fileOut, 'w', encoding='utf-8') as fout:
            fout.write(content)




# #######################################################
# # book = epub.read_epub(percorso_file_epub)
# #######################################################
def extractMetadata(book):
    try:
        titles = book.get_metadata('DC', 'title')
        if titles:
            title = titles[0][0]

        creators = book.get_metadata('DC', 'creator')
        if creators:
            authors = [c[0] for c in creators]
        else:
            authors = ["Sconosciuto"]

    except Exception as e:
        # Aumentiamo la verbosità dell'errore per il debug
        print(f"Errore durante l'estrazione dei metadati con EbookLib da '{percorso_file_epub}': {e}")

    return title, authors






def cerca_in_epub_con_ebooklib(percorso_file_epub, stringa_ricerca, ricerca_esatta=True, distanza_parole=5):
    """
    Ricerca una stringa o parole vicine all'interno di un file EPUB usando EbookLib.
    """
    trovate = []
    HIGHLIGHT_START = "\033[1m"
    HIGHLIGHT_END = "\033[0m"

    try:
        book = epub.read_epub(percorso_file_epub)

        for item in book.get_items():
            if item.get_type() in ['application/xhtml+xml', 'text/html']:
                try:
                    contenuto_greggio = item.content
                    contenuto_decodificato = contenuto_greggio.decode('utf-8', errors='ignore')

                    soup = BeautifulSoup(contenuto_decodificato, 'html.parser')

                    # *** INIZIO MODIFICA PER NORMALIZZAZIONE TESTO ***
                    # Estrai il testo e poi normalizzalo ulteriormente
                    testo_pulito_intermedio = soup.get_text(separator=' ', strip=True)

                    # Rimuovi i salti di riga e i ritorni a capo per trattare tutto come una singola riga di testo
                    # e sostituisci eventuali spazi multipli con un singolo spazio
                    testo_pulito = re.sub(r'\s+', ' ', testo_pulito_intermedio).strip()
                    # *** FINE MODIFICA PER NORMALIZZAZIONE TESTO ***

                    if ricerca_esatta:
                        escaped_string = re.escape(stringa_ricerca)
                        # Assicurati che la ricerca sia case-insensitive e che la stringa non sia parte di una parola più grande
                        # Aggiungiamo \b (word boundary) attorno alla stringa cercata se è composta da singole parole alfanumeriche
                        # Altrimenti, una semplice ricerca della sottostringa.
                        if re.fullmatch(r'\w+', stringa_ricerca): # Se la stringa è una singola parola alfanumerica
                             pattern = re.compile(f"(.{{0,100}})\\b({escaped_string})\\b(.{{0,100}})", re.IGNORECASE | re.DOTALL)
                        else: # Altrimenti cerca la frase come blocco di caratteri
                             pattern = re.compile(f"(.{{0,100}})({escaped_string})(.{{0,100}})", re.IGNORECASE | re.DOTALL)

                        for match in pattern.finditer(testo_pulito):
                            pre_context = match.group(1).strip()
                            found_phrase = match.group(2)
                            post_context = match.group(3).strip()

                            evidenziato = f"{HIGHLIGHT_START}{found_phrase}{HIGHLIGHT_END}"
                            trovate.append(f"...{pre_context} {evidenziato} {post_context}...")
                    else:
                        parole_cercate = stringa_ricerca.split()
                        if len(parole_cercate) < 2:
                            escaped_word = re.escape(stringa_ricerca)
                            if re.fullmatch(r'\w+', stringa_ricerca):
                                pattern = re.compile(f"(.{{0,100}})\\b({escaped_word})\\b(.{{0,100}})", re.IGNORECASE | re.DOTALL)
                            else:
                                pattern = re.compile(f"(.{{0,100}})({escaped_word})(.{{0,100}})", re.IGNORECASE | re.DOTALL)

                            for match in pattern.finditer(testo_pulito):
                                pre_context = match.group(1).strip()
                                found_word = match.group(2)
                                post_context = match.group(3).strip()

                                evidenziato = f"{HIGHLIGHT_START}{found_word}{HIGHLIGHT_END}"
                                trovate.append(f"...{pre_context} {evidenziato} {post_context}...")
                        else:
                            context_pattern_pre = r"(.{0,100})"
                            context_pattern_post = r"(.{0,100})"

                            regex_parts = []
                            # Per la ricerca di parole vicine, assicuriamoci che ogni parola sia delimitata da word boundary \b
                            # e che la distanza sia tra le parole effettive, non tra i caratteri del pattern.
                            for i, parola in enumerate(parole_cercate):
                                regex_parts.append(f"({re.escape(parola)})") # Ogni parola è un gruppo catturante
                                if i < len(parole_cercate) - 1:
                                    # Questo pattern cerca "distanza_parole" parole (o gruppi di non-spazi) tra le parole cercate
                                    # \W* cerca zero o più caratteri non-parola (punteggiatura, spazi)
                                    # (\s+\S+){0,distanza_parole} cerca blocchi di (spazio + non-spazio)
                                    # Usiamo \b\W* per essere più precisi sui confini delle parole
                                    regex_parts.append(r'\b(?:(?:\s+\S+){0,' + str(distanza_parole) + r'})\s*\b')

                            full_regex_str = "".join(regex_parts)
                            # Nota: La cattura del contesto pre/post e della parte intermedia è più complessa
                            # Ho semplificato un po' l'estrazione del contesto per renderla più robusta.
                            full_pattern = re.compile(f"{context_pattern_pre}{full_regex_str}{context_pattern_post}", re.IGNORECASE | re.DOTALL)

                            for match in full_pattern.finditer(testo_pulito):
                                pre_context = match.group(1).strip()

                                found_and_highlighted = ""
                                group_index = 2 # Il primo gruppo è pre_context (1), poi iniziano le parole cercate
                                for i, parola_originale in enumerate(parole_cercate):
                                    # Estrai la parola trovata dalla corrispondenza
                                    parola_trovata_nel_match = match.group(group_index)
                                    found_and_highlighted += f"{HIGHLIGHT_START}{parola_trovata_nel_match}{HIGHLIGHT_END}"
                                    group_index += 1

                                    if i < len(parole_cercate) - 1:
                                        # Calcola la porzione di testo tra la parola corrente e la successiva
                                        # Questo richiede di sapere dove finisce la parola corrente e dove inizia la prossima all'interno del match globale
                                        # Questo approccio è più robusto del calcolo manuale degli indici.
                                        # Prendiamo la parte di testo *all'interno del match completo* che non è stata catturata dai gruppi delle parole.

                                        # Per semplificare e rendere più robusta la gestione del testo intermedio tra le parole
                                        # per la visualizzazione, ri-applichiamo una logica di estrazione più ampia
                                        # o accettiamo che il testo intermedio potrebbe non essere evidenziato.

                                        # Metodo più semplice per il testo intermedio: assumere uno spazio
                                        found_and_highlighted += " "

                                post_context = match.group(group_index).strip()

                                trovate.append(f"...{pre_context} {found_and_highlighted} {post_context}...")

                except Exception as e:
                    # Aumentiamo la verbosità dell'errore per il debug
                    print(f"Errore nella lettura o elaborazione del contenuto dell'elemento in '{percorso_file_epub}': {e}")
    except Exception as e:
        # Aumentiamo la verbosità dell'errore per il debug
        print(f"Errore durante l'apertura di '{percorso_file_epub}' con EbookLib: {e}")
    return trovate

# --- Il resto dello script (cerca_file_e_contenuto e configurazione) rimane invariato ---
# Assicurati che le chiamate siano ancora a estrai_metadati_epub_con_ebooklib e cerca_in_epub_con_ebooklib

def cerca_file_e_contenuto(cartella_base, stringa_ricerca, ricerca_esatta=True, distanza_parole=5, filtro_autore=None, filtro_titolo=None):
    """
    Cerca file .epub in una cartella e sottocartelle, e poi cerca una stringa al loro interno,
    applicando filtri opzionali per autore e/o titolo.
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

                titolo_epub, autori_epub = estrai_metadati_epub_con_ebooklib(percorso_completo_epub)

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
                    continue

                epub_filtrati += 1
                print(f"Analisi del file: '{percorso_completo_epub}'")
                print(f"  Metadati: Titolo: '{titolo_epub}', Autori: {', '.join(autori_epub)}")

                risultati_ricerca = cerca_in_epub_con_ebooklib(percorso_completo_epub, stringa_ricerca, ricerca_esatta, distanza_parole)

                if risultati_ricerca:
                    print(f"  --> Corrispondenze trovate in '{file}':")
                    corrispondenze_totali += len(risultati_ricerca)
                    for r in risultati_ricerca:
                        print(f"    - {r}")
                else:
                    print(f"  Nessuna corrispondenza trovata nel contenuto di '{file}'.")
        print("-" * 50)

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
    cartella_di_partenza = "./"
    stringa_da_cercare = "Harry Potter" # Prova con una parola o frase che sai esserci
    ricerca_esatta_frase = False # Prova entrambe le modalità (True/False)
    distanza_massima_parole = 10
    filtro_autore_parziale = None
    filtro_titolo_parziale = None

    cerca_file_e_contenuto(
        cartella_di_partenza,
        stringa_da_cercare,
        ricerca_esatta_frase,
        distanza_massima_parole,
        filtro_autore=filtro_autore_parziale,
        filtro_titolo=filtro_titolo_parziale
    )