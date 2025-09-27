#!/usr/bin/env python3
#
# Progamma per testare regex
#
# updated by ...: Loreto Notarantonio
# Version ......: 14-10-2020 09.22.06
#


import sys; sys.dont_write_bytecode = True

import re
import time


def setup(gVars):
    global gv, logger
    gv=gVars
    logger=gv.logger


def function_executing_time(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logger.notify(f"[Function: {func.__name__}] eseguita in {end - start:.6f} secondi", stacklevel=1)
        return result
    return wrapper



#################################
#
#################################
def FindAll(p, data):
    logger.info("processing: %s", p)
    if isinstance(data, str): data=[data]
    result=[]
    occurrencies = p.findall(' '.join(data))
    if  occurrencies:
        # if fPRINT:print(occurrencies)
        result.extend(occurrencies)

    return result




#################################
# return: {
#           'word1': {
#                       "start": 99,
#                       "end": 88,
#                       "context": "text"
#                       }
#          }
#################################
def FindIter(p, source_data: str, context_length: int=0):
    logger.info("processing: %s", p)
    occurrences = {}

    # Normalizza il testo per la ricerca
    processed_text = ' '.join(source_data.split())

    for match in p.finditer(processed_text):
        start, end = match.span()
        matched_text = match.group() ### nome della word

        # Estrai il contesto
        if context_length < 1:
            context_length = 0

        start_context = max(0, start - context_length)
        end_context   = min(len(processed_text), end + context_length)
        context = processed_text[start_context:end_context]

        # creal il dictionary di ritorno
        if matched_text not in occurrences:
            occurrences[matched_text] = {}

        occurrences[matched_text]["text"] = context
        occurrences[matched_text]["start"] = start
        occurrences[matched_text]["end"] = end

    return occurrences



#################################
# - search all words (AND)
##################################
@function_executing_time
def AND_justCheck(source_data: str, string_list: list, word_boundary=False):
    '''
        Esegue una ricerca AND per verificare se tutte le parole di string_list sono presenti nel testo.

        Args:
            source_data (str): Il testo in cui cercare.
            string_list (list): La lista di parole da cercare.
            word_boundary (bool): Se True, cerca le parole come entità separate.

        Returns:
            bool: True se tutte le parole sono presenti, altrimenti False.
    '''
    processed_text = ' '.join(source_data.split()).lower()

    # Itera su ogni parola e verifica la sua presenza
    for word in string_list:
        if word_boundary:
            # Crea un pattern con il confine di parola
            pattern = fr'\b{re.escape(word.lower())}\b'
        else:
            # Crea un pattern senza il confine di parola
            pattern = re.escape(word.lower())

        if re.search(pattern, processed_text) is None:
            # Se una parola non viene trovata, restituisce False immediatamente
            return False

    # Se il ciclo termina, tutte le parole sono state trovate
    return True


#################################
# - search all words (AND) any order
# - ritorna il contesto
#################################
@function_executing_time
def AND(source_data: str, string_list: list, word_boundary=False, context_length: int=0):
    '''
        Esegue una ricerca AND per verificare se tutte le parole di string_list sono presenti nel testo.

        Args:
            source_data (str): Il testo in cui cercare.
            string_list (list): La lista di parole da cercare.
            word_boundary (bool): Se True, cerca le parole come entità separate.

        Returns:
            dict: entries se tutte le parole sono presenti, altrimenti {}.
    '''
    logger.notify("sarching the following words: %s", string_list)

    base_pattern = r'\b({item})\b' if word_boundary else r'({item})'

    matches={}

    for item in string_list:
        p=re.compile(base_pattern.format(**locals()), re.IGNORECASE)
        _dict = FindIter(p=p, source_data=source_data, context_length=context_length)
        ### --- esci alla prima stringa non trovata
        if not _dict:
            matches={}
            break
        matches.update(_dict)

    return matches




#################################
# - search any word (OR)
#################################
@function_executing_time
def OR(source_data: str, string_list: list, word_boundary=False, context_length: int=0):
    logger.notify("sarching far all the following strings: %s", string_list)

    base_pattern = r'\b({item})\b' if word_boundary else r'({item})'

    matches={}

    for item in string_list:
        p=re.compile(base_pattern.format(**locals()), re.IGNORECASE)
        _dict = FindIter(p=p, source_data=source_data, context_length=context_length)
        if _dict:
            matches.update(_dict)

    return matches



#################################
# - search near words
#################################
@function_executing_time
def two_near_words(source_data: str, word1, word2, near):
    if not isinstance(source_data, str) or not word1 or not word2 or not isinstance(near, list) or len(near) != 2:
        print("Input non valido.")
        return {}

    min_words, max_words = near

    # Costruisci il pattern con f-string per maggiore leggibilità
    pattern = rf'\b{word1}\W+(?:\w+\W+){{{min_words},{max_words}}}{word2}\b'

    # Compila l'espressione regolare per maggiore efficienza
    p = re.compile(pattern, re.IGNORECASE)

    return FindIter(p=p, source_data=source_data)




#################################
# - search near words
#################################
@function_executing_time
def multi_near_words(source_data: str, words_list: list, near: list):
    # Controllo che gli input siano validi e che ci siano almeno due parole
    if not isinstance(source_data, str) or not isinstance(words_list, list) or len(words_list) < 2 or not isinstance(near, list) or len(near) != 2:
        print("Input non valido. Fornire una lista di almeno due parole.")
        return {}

    min_words, max_words = near


    # Costruisci l'espressione regolare per la prima parola
    pattern_parts = [rf'\b{words_list[0]}\b']

    # Aggiungi le altre parole e lo spazio tra di esse
    # Il loop parte dalla seconda parola
    for i in range(1, len(words_list)):
        pattern_parts.append(rf'\W+(?:\w+\W+){{{min_words},{max_words}}}{words_list[i]}\b')

    # Unisci le parti del pattern
    pattern = ''.join(pattern_parts)

    # Compila l'espressione regolare
    p = re.compile(pattern, re.IGNORECASE)

    return FindIter(p=p, source_data=source_data)









if __name__ == '__main__':
    # sys.path.insert(0, "test")
    print("ESEGUIRE:" "test/LnRegex_TEST.py")