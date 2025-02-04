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
    """Initialize the spaCy model if it is not already loaded.

    This function loads the `fr_core_news_sm` spaCy model and ensures it is available globally.
    """
    global nlp
    if nlp is None:
        nlp_start_time = time.time()
        nlp = spacy.load("fr_core_news_sm")
        print(f"Modèle spaCy chargé en {time.time() - nlp_start_time:.2f} secondes.")
    else:
        print("Le modèle spaCy est déjà chargé.")
    sys.stdout.flush()

def enlever_accents(text: str) -> str:
    """Remove accents from a string.

    :param str text: The input text
    :return: Text without accents
    :rtype: str
    """
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

def preprocess_text(texte: str) -> str:
    """Preprocess a text by removing non-alphabetic characters and stopwords, and lemmatizing it.

    This function also converts text to lowercase, removes accents, and applies tokenization and lemmatization using spaCy.

    :param str texte: The input text to preprocess
    :return: The cleaned and lemmatized text
    :rtype: str
    """
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

def refine_words(words):
    """Refine a list of words by removing non-alphabetic words.

    :param list words: List of words to refine
    :return: A filtered list containing only valid words
    :rtype: list
    """
    refined = []
    for word in words:
        # Vérifier si un mot est cohérent
        if is_valid_word(word):
            refined.append(word)
    return refined

def is_valid_word(word):
    """Check if a word is valid using spaCy.

    This function verifies if the word exists in the spaCy vocabulary and is an alphabetic word.

    :param str word: The word to check
    :return: True if the word is valid, False otherwise
    :rtype: bool
    """
    return word in nlp.vocab and nlp.vocab[word].is_alpha

