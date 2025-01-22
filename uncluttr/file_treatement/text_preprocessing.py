""" This module contains functions for text preprocessing. """

import re
import sys
import time
import unicodedata
import spacy
import nltk
from nltk.corpus import stopwords


# Télécharger les stopwords de NLTK
try:
    start_time = time.time()
    stopwords.words('french')
    print(f"Les stopwords ont été verifies en {time.time() - start_time:.5f} secondes.")
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

    # Texte en minuscules
    texte = texte.lower()

    # Suppression des caractères non alphabétiques et des espaces supplémentaires
    texte = re.sub(r'[^a-zA-Zéàèùâêîôûçäëïöüôâàèéùê]', ' ', texte)
    texte = re.sub(r'\s+', ' ', texte).strip()

    # Suppression des accents (si nécessaire)
    texte = enlever_accents(texte)

    # Tokenisation et lemmatisation avec spaCy
    doc = nlp(texte)
    texte_lematise = " ".join([token.lemma_ for token in doc if token.lemma_ not in stopwords.words('french')])

    return texte_lematise.strip()
