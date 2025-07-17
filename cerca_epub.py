#! /usr/bin/env python3
# updated by ...: Loreto Notarantonio
# Date .........: 17-07-2025 09.07.48
#

import sys; sys.dont_write_bytecode=True
import os


import re
import csv
import argparse
from ebooklib import epub
from bs4 import BeautifulSoup

# --- Estrai testo e metadati ---
def estrai_dati_epub(percorso_file):
    try:
        libro = epub.read_epub(percorso_file)
        testo = ""
        import pdb; pdb.set_trace() # by Loreto
        for item in libro.get_items():
            if item.get_type() == epub.EpubHtml:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                testo += soup.get_text(separator=' ')
        titolo = libro.get_metadata('DC', 'title')
        autore = libro.get_metadata('DC', 'creator')
        return {
            'titolo': titolo[0][0] if titolo else "Sconosciuto",
            'autore': autore[0][0] if autore else "Sconosciuto",
            'testo': testo
        }
    except Exception as e:
        print(f"[ERRORE] {percorso_file}: {e}")
        return None

# --- Crea regex per parole vicine ---
def costruisci_regex(parole, distanza):
    pattern = re.escape(parole[0])
    for parola in parole[1:]:
        pattern += r'(?:\W+\w+){0,' + str(distanza) + r'}?\W+' + re.escape(parola)
    return pattern

# --- Trova le anteprime ---
def trova_anteprime(testo, parole, distanza, frase_esatta=False, righe_context=3):
    if frase_esatta:
        pattern = re.escape(" ".join(parole))
    else:
        pattern = costruisci_regex(parole, distanza)
    matches = list(re.finditer(pattern, testo, flags=re.IGNORECASE | re.DOTALL))

    righe = testo.splitlines()
    anteprime = []
    for match in matches:
        start, end = match.start(), match.end()
        estratto = match.group(0).strip()
        contesto = testo[max(0, start - 200): min(len(testo), end + 200)].strip()
        anteprime.append((contesto, estratto))
    return anteprime

# --- Ricerca principale ---
def cerca(cartella, testo, distanza, frase_esatta, filtro_titolo, filtro_autore):
    risultati = []
    parole = testo.strip().lower().split()

    for root, _, files in os.walk(cartella):
        for file in files:
            if file.lower().endswith(".epub"):
                percorso = os.path.join(root, file)
                dati = estrai_dati_epub(percorso)
                print(percorso)
                if not dati:
                    print("     nessun dato....")
                    continue

                if filtro_titolo and filtro_titolo.lower() not in dati['titolo'].lower():
                    continue
                if filtro_autore and filtro_autore.lower() not in dati['autore'].lower():
                    continue

                anteprime = trova_anteprime(dati['testo'], parole, distanza, frase_esatta)
                if anteprime:
                    risultati.append((percorso, dati['titolo'], dati['autore'], anteprime))
    return risultati

# --- Evidenziazione nel terminale ---
def evidenzia(text, parola):
    return re.sub(f"({re.escape(parola)})", r"\033[93m\1\033[0m", text, flags=re.IGNORECASE)

# --- Esportazione ---
def esporta(risultati, formato):
    nome_file = f"risultati_ricerca.{formato}"
    try:
        if formato == "txt":
            with open(nome_file, "w", encoding="utf-8") as f:
                for percorso, titolo, autore, anteprime in risultati:
                    f.write(f"{percorso}\nTitolo: {titolo}\nAutore: {autore}\n")
                    for contesto, _ in anteprime:
                        f.write(contesto + "\n\n")
        elif formato == "csv":
            with open(nome_file, "w", encoding="utf-8", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["File", "Titolo", "Autore", "Contesto"])
                for percorso, titolo, autore, anteprime in risultati:
                    for contesto, _ in anteprime:
                        writer.writerow([percorso, titolo, autore, contesto])
        print(f"\n✅ Risultati esportati in {nome_file}")
    except Exception as e:
        print(f"❌ Errore durante l'esportazione: {e}")

# --- Argomenti da riga di comando ---
parser = argparse.ArgumentParser(description="Cerca testo in file .epub")
parser.add_argument('--cartella', required=True, help="Percorso della cartella con gli epub")
parser.add_argument('--testo', required=True, help="Testo da cercare")
parser.add_argument('--distanza', type=int, default=5, help="Max parole intermedie (solo per ricerca parole vicine)")
parser.add_argument('--tipo', choices=["vicine", "frase"], default="vicine", help="Tipo di ricerca")
parser.add_argument('--formato', choices=["txt", "csv"], default="txt", help="Formato di esportazione")
parser.add_argument('--titolo', default="", help="Filtro titolo parziale")
parser.add_argument('--autore', default="", help="Filtro autore parziale")

args = parser.parse_args()

# --- Esecuzione ---
print(f"\n🔍 Avvio ricerca: \"{args.testo}\" ({'frase esatta' if args.tipo == 'frase' else f'entro {args.distanza} parole'})")

risultati = cerca(
    cartella=args.cartella,
    testo=args.testo,
    distanza=args.distanza,
    frase_esatta=(args.tipo == "frase"),
    filtro_titolo=args.titolo,
    filtro_autore=args.autore
)

if risultati:
    for percorso, titolo, autore, anteprime in risultati:
        print(f"\n📘 {percorso}")
        print(f"   Titolo: {titolo}")
        print(f"   Autore: {autore}")
        for contesto, evidenziato in anteprime:
            print(evidenzia(contesto, evidenziato))
            print("---")
    esporta(risultati, args.formato)
else:
    print("\n❌ Nessuna corrispondenza trovata.")
