""" This module contains functions for text preprocessing. """

import re
import unicodedata
import spacy
import nltk
from nltk.corpus import stopwords


# Télécharger les stopwords de NLTK
nltk.download('stopwords')

# Charger le modèle spaCy pour le français
nlp = spacy.load("fr_core_news_sm")

# Supprimer les accents pour une optionnalité
def enlever_accents(texte):
    return ''.join(c for c in unicodedata.normalize('NFD', texte) if unicodedata.category(c) != 'Mn')

# Prétraitement du texte
def preprocess_text(texte):
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
