# clean_filename.py
#
# Funzioni per pulire i nomi dei file

import re

def clean_filename(text: str) -> str:
    """
    Es: filename = "Mate: edizione italiana (Bride Vol. 2).epub"
    Rimuove tutto dal primo ':', '(', '[' o '-' fino alla fine della stringa
    Come funziona la regex r"(s*[:([-].*)":
        s*: ignora eventuali spazi prima del separatore.
        [:([-]: individua il punto di inizio del taglio (due punti :, parentesi tonda (, parentesi quadra [, o trattino -).
        .*: seleziona tutto il resto della stringa fino alla fine.
        "": sostituisce tutta la parte selezionata con una stringa vuota, lasciando solo il titolo principale.
    """


# Rimuove tutto dal primo ':', '(', '[' o '-' fino alla fine della stringa
    cleaned_text = re.sub(r"\s*[:\(\[-].*", "", text)
    cleaned_text = re.sub(r"s*[:([-].*", "", text)
    return cleaned_text.strip()
