""" This module contains functions for text preprocessing. """

import re
import sys
import time
import unicodedata
import spacy
import nltk
from nltk.corpus import stopwords
from datetime import datetime


# Télécharger les stopwords de NLTK
try:
    start_time = time.time()
    stopwords.words('french')
    print(f"La vérification de l'installation des stopwords en {time.time() - start_time:.5f} secondes.")
    sys.stdout.flush()
except LookupError:
    start_time = time.time()
    nltk.download('stopwords')
    print(f"Les stopwords ont été téléchargés en {time.time() - start_time:.5f} secondes.")
    sys.stdout.flush()

# Variable globale pour le modèle spaCy
nlp = None

def initialize_spacy_model():
    """Initialiser le modèle spaCy si nécessaire."""
    global nlp
    if nlp is None:
        nlp_start_time = time.time()
        nlp = spacy.load("fr_core_news_sm")
        print(f"Modèle spaCy chargé en {time.time() - nlp_start_time:.2f} secondes.")
    else:
        print("Le modèle spaCy est déjà chargé.")
    sys.stdout.flush()


# Supprimer les accents pour une optionnalité
def enlever_accents(text: str) -> str:
    """delete accents from a string."""
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

# Prétraitement du texte
def preprocess_text(texte: str) -> str:
    """Preprocess a text by removing non-alphabetic characters and stopwords, and lemmatizing it."""
    initialize_spacy_model()

    # Télécharger les stopwords de NLTK
    try:
        stopwordsFR = stopwords.words('french')
    except LookupError:
        nltk.download('stopwords')
        stopwordsFR = stopwords.words('french')

    # Texte en minuscules
    texte = texte.lower()

    # Suppression des caractères non alphabétiques et des espaces supplémentaires
    texte = texte.replace('´', '').replace('–', ' ').replace('ˆ', '').replace('’', ' ').replace('‘', ' ').replace('“', ' ').replace('”', ' ').replace('…', ' ').replace('©', '').replace('®', '').replace('™', '').replace('°', ' ').replace('‹', ' ').replace('›', ' ').replace('’', ' ').replace('—', ' ').replace('«', ' ').replace('»', ' ')
    texte = texte.replace('\uFB01', 'fi').replace('\uFB02', 'fl').replace('\uFB00', 'ff').replace('\uFB03', 'ffi').replace('\uFB04', 'ffl').replace('\u0300','')
    texte = texte.replace('€', 'euros').replace('$', 'dollars').replace('£', 'livres')
    texte = re.sub(r'[^a-zA-Z0-9éàèùâêîôûçäëïöüôâàèéùê\s/-]', ' ', texte)
    texte = re.sub(r'\s+', ' ', texte).strip()

    # Suppression des accents
    texte = enlever_accents(texte)

    # Tokenisation et lemmatisation avec spaCy
    doc = nlp(texte)
    texte_lematise = ' '.join([token.lemma_ for token in doc if not token.is_stop])

    # Suppression des accents
    texte_lematise = enlever_accents(texte_lematise)

    return texte_lematise


    # Prétraitement pour les dates

# Prétraitement pour les dates
def preprocess_date(texte: str) -> str:

    mois = {
        "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4,
        "mai": 5, "juin": 6, "juillet": 7, "août": 8, "aout": 8,
        "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12, "decembre": 12
    }

    # Expression régulière
    pattern = r"""
    \b
    (?:
        (\d{1,2})                    
        (?:/|-|\s)                   
    )?
    (janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre|\d{1,2})  
    (?:\s|-|/)?                       
    (\d{4})?                        
    \b
    """

    # Rechercher toutes les correspondances
    matches = re.findall(pattern, text, re.VERBOSE | re.IGNORECASE)

    # Traiter les correspondances
    dates = []
    for match in matches:
        day, month, year = match
        # Convertir le mois en nombre si nécessaire
        month_number = None
        if month:
            if month.isdigit():  # Mois en chiffres
                month_number = int(month)
            elif month.lower() in mois:  # Mois en lettres
                month_number = mois[month.lower()]

        

        # Vérifier si une année est présente, sinon en mettre 1900 par défaut
        year = int(year) if year else 1900

        # Créer une date valide si le mois est présent
        if month_number:
            if day:  # Si un jour est présent
                try:
                    date_obj = datetime(year=year, month=month_number, day=int(day))
                    dates.append(date_obj)
                except ValueError:
                    pass
            else:  # Si seul le mois est présent, jour par défaut 01
                try:
                    date_obj = datetime(year=year, month=month_number, day=1)
                    dates.append(date_obj)
                except ValueError:
                    pass

    # Afficher les résultats
    print("Dates détectées :")
    for date in dates:
        print(date.strftime("%d/%m/%Y"))

    return texte

if __name__ == "__main__":
    text =  text = """
    Les evenements importants sont les suivants : 
    - Le 12 janvier 2021, un incident s'est produit.
    - Une autre date importante : 25/03.
    - Le mois de mars est souvent charge.
    - Une reunion est prevue en avril.
    - le doc date du 28-07
    - rattrapage le 18 mai
    - facture de juillet 2023
    - fiche de paie 11-2022
    - fiche de paie 01/2025
    - fiche de paie 01 2002
    """

    text = preprocess_date(text)
